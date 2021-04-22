import numpy as np
from numpy import linalg as LA
from typing import List, Dict


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

    def _reweight_similarity_matrix(self, similarity_matrix:np.ndarray, siblings:Dict, alpha=1)->np.ndarray:
        """
        Re-weights similarity matrix in order to preserve tree structure.
        """

        m,n = similarity_matrix.shape
        for i in range(n):
            for j in range(n):
                delta = 1 if siblings[i] == j else 0
                similarity_matrix[i, j] = similarity_matrix[i, j] * (1 + alpha * delta)
        return similarity_matrix

    def _compute_leaf_ordering(self, distance_matrix:np.ndarray, similarity_matrix:np.ndarray)->np.array:
        """
        Details in Analysis of gene expression profiles: clas discovery and leaf ordering
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

    def get_optimal_leaf_ordering(self):
        pass