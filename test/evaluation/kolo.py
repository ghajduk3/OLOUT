import json
from src.orderings.kolo import KOLO
from src.orderings.kolo import KOLO
from src.utils.newick import Parser
import numpy as np
# from src.utils.preprocess import get_distance_matrix
from src.utils.distance_matrix import ReconstructDistanceMatrix
import itertools
from src.visualizations import radial
from src.utils.pipeline import leaf_ordering_kolo, radial_visualization


if __name__ == "__main__":

    dis_1 = np.array([[0, 5, 4, 7, 6, 8],
                      [5, 0, 7, 10, 9, 11],
                      [4, 7, 0, 7, 6, 8],
                      [7, 10, 7, 0, 5, 9],
                      [6, 9, 6, 5, 0, 8],
                      [8, 11, 8, 9, 8, 0]])

    tree_string_1 = "(5:5.00000,(2:2.000000,(1:4.000000, 0:1.000000):1.000000):2.000000,(4:2.000000, 3:3.000000):1.000000);"

    dis_2 = np.array([[0, 5, 9, 9, 8],
                      [5, 0, 10, 10, 9],
                      [9, 10, 0, 8, 7],
                      [9, 10, 8, 0, 3],
                      [8, 9, 7, 3, 0]])
    tree_string_2 = '(4:1.000000,(2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000,3:2.000000);'

    # tree_1, mapping = Parser.parse_newick_tree(tree_string_1)
    # distance_matrix_1 = get_distance_matrix(tree_1)
    #
    # kolo = KOLO(tree_string_1, np.array(distance_matrix_1))
    # print("Tree 1 --------------------", kolo.get_optimal_leaf_ordering())

    # tree_2, mapping_2 = Parser.parse_newick_tree(tree_string_2)
    # distance_matrix_2 = ReconstructDistanceMatrix(tree_2).get_reconstructed_distance_matrix()
    # print(distance_matrix_2)
    # # distance_matrix_2 = get_distance_matrix(tree_2)
    #
    # kolo = KOLO(tree_string_2, np.array(distance_matrix_2))
    # ordered_tree, optimal_ordering = kolo.get_optimal_leaf_ordering()
    # print("Tree 2 --------------------",optimal_ordering)
    ordered_tree, leaf_ordering, node_mapping = leaf_ordering_kolo(tree_string_1)
    radial_visualization(ordered_tree, node_mapping)

















