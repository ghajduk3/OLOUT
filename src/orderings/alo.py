import numpy as np
from numpy import linalg as LA
from typing import List, Dict
from src.utils.newick import Parser


class ALO(object):

    def __init__(self, newick_tree, similarity_matrix):
        self.newick = newick_tree
        self.similarity_matrix = similarity_matrix

    def _compute_distance_matrix(self,similarity_matrix:np.ndarray)->np.ndarray:
        """
        Computes distance matrix D. D is a diagonal matrix where Di = sum(Sij).

        """
        m, n = similarity_matrix.shape
        distance_matrix = np.identity(n)
        np.fill_diagonal(distance_matrix, [sum(similarity_matrix[i]) for i in range(n)])
        return distance_matrix

    def _compute_p_vector(self, ordering: List):
        """
        Computes p vector according to p(i) = (i - (n/2)) / (n/2)
        """
        n = len(ordering)
        return np.apply_along_axis(lambda x: (x - n / 2) / (n / 2), 0, ordering).reshape(1, n)

    def _reweight_similarity_matrix(self, similarity_matrix:np.ndarray, siblings:Dict, alpha=5)->np.ndarray:
        """
        Re-weights similarity matrix in order to preserve tree structure.
        """

        m,n = similarity_matrix.shape
        for i in range(n):
            for j in range(n):
                delta = 0 if j in siblings[i] else 1
                similarity_matrix[i, j] = similarity_matrix[i, j] * (1 + alpha * delta)
        return similarity_matrix

    def _compute_leaf_ordering(self, distance_matrix:np.ndarray, similarity_matrix:np.ndarray)->np.array:
        """
        Details in Analysis of gene expression profiles: class discovery and leaf ordering
        """
        order_len = distance_matrix.shape[1]
        final_matrix = np.identity(order_len) - np.matmul(LA.inv(distance_matrix), similarity_matrix)
        eig_values, eig_vectors = LA.eig(final_matrix)
        second_min_ind = np.argsort(eig_values)[1]
        second_min_vector = eig_vectors[:, second_min_ind]
        return np.argsort(second_min_vector)[::-1]

    def _calculate_adjacent_pair_sim_ratio(self, ordering, similarity_matrix):
        m,n = similarity_matrix.shape
        jd = sum([similarity_matrix[ordering[ind], ordering[ind + 1]] for ind in range(n - 1)])
        jd_random = (n - 1) * sum(
            [similarity_matrix[i, j] / n ** 2 for i in range(n) for j in range(n)])
        return jd / jd_random

    def _parse_newick_tree(self):
        return Parser.parse_newick_tree(self.newick)

    @staticmethod
    def _generate_sibling_pairs(root, siblings ={}):


        for child in root.get_children():
            if child.is_leaf():
                if root.get_id() not in siblings:
                    siblings[root.get_id()] = [child.get_id()]
                else:
                    siblings[root.get_id()].append(child.get_id())

            else:
                ALO._generate_sibling_pairs(child,siblings)

        return siblings

    @staticmethod
    def _get_siblings(root):
        siblings_temporary = ALO._generate_sibling_pairs(root)
        siblings = {}
        for parent,children in siblings_temporary.items():
            for index, child in enumerate(children):
                siblings[child] = children[:index] + children[index+1:]
        return siblings


    def get_optimal_leaf_ordering(self):
        newick_tree = self._parse_newick_tree()
        siblings = ALO._get_siblings(newick_tree)
        similarity_matrix = self._reweight_similarity_matrix(self.similarity_matrix, siblings)
        distance_matrix = self._compute_distance_matrix(self.similarity_matrix)
        ordering = self._compute_leaf_ordering(distance_matrix,similarity_matrix)
        return ordering