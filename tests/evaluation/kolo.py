# import json
# from olout.orderings.kolo import KOLO
# from olout.orderings.kolo import KOLO
# from olout.utils.newick import Parser
# import numpy as np
# # from olout.utils.preprocess import get_distance_matrix
# from olout.utils.distance_matrix import ReconstructDistanceMatrix
# import itertools
# from olout.visualizations import radial
# from olout.utils import constants
# import os
# from olout.visualizations import radial
#
# from olout.utils.pipeline import leaf_ordering_kolo, radial_visualization
# from olout.utils.evaluation_pipeline import run_single_evaluation_suite
# import rootpath
#
# FINAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'final_data')
# EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')
# QUARANTINE_EVAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'quarantine_evaluations')
# QUARANTINE_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'quarantine')
#
# def load_tree_from_data_dir_name(dir_name):
#     json_file = open(os.path.join(FINAL_DATA_PATH, dir_name, 'data.json'), 'r')
#     data_json = json.load(json_file)
#     nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
#     tree, node_mapping = Parser.parse_newick_tree(phylogenetic_newick_string)
#     distance_matrix = ReconstructDistanceMatrix(tree).get_reconstructed_distance_matrix()
#     radial_layout = radial.RadialLayoutLeafCount(tree)
#     print(radial_layout.get_pair_distance(14,15))
#     print(radial_layout.get_pair_distance(10, 13))
#     print(node_mapping)
#
#
#
#
# if __name__ == "__main__":
#
#     dis_1 = np.array([[0, 5, 4, 7, 6, 8],
#                       [5, 0, 7, 10, 9, 11],
#                       [4, 7, 0, 7, 6, 8],
#                       [7, 10, 7, 0, 5, 9],
#                       [6, 9, 6, 5, 0, 8],
#                       [8, 11, 8, 9, 8, 0]])
#
#     tree_string_1 = "(5:5.00000,(2:2.000000,(1:4.000000, 0:1.000000):1.000000):2.000000,(4:2.000000, 3:3.000000):1.000000);"
#
#     dis_2 = np.array([[0, 5, 9, 9, 8],
#                       [5, 0, 10, 10, 9],
#                       [9, 10, 0, 8, 7],
#                       [9, 10, 8, 0, 3],
#                       [8, 9, 7, 3, 0]])
#     tree_string_2 = '(4:1.000000, 3:2.000000, (2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000);'
#
#     tree, ordered_tree, leaf_ordering, node_mapping = leaf_ordering_kolo(tree_string_2)
#     # radial_visualization(ordered_tree, tree,node_mapping, show_flag=True)
#     # radial_visualization(ordered_tree, tree, node_mapping,radial_visualization_method=constants.RADIAL_LAYOUT_LEAF_COUNT, show_flag=True)
#     # print(node_mapping)
#     run_single_evaluation_suite('S141443')
#     # run_single_evaluation_suite('S141443',radial_visualization_method=constants.RADIAL_LAYOUT_LEAF_COUNT)
#     # load_tree_from_data_dir_name('S118920')


from olout.utils import pipeline, constants, evaluation_pipeline

if __name__ == '__main__':
    phylo_tree_newick = '(4:1.000000, 3:2.000000, (2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000);'
    # To obtain optimal leaf ordering for the given string
    original_tree, optimally_ordered_tree, optimal_leaf_ordering, node_mapping = pipeline.leaf_ordering_kolo(phylo_tree_newick)

    # To visualize above described four different layouts use. A new page with BOKEH plots will appear
    evaluation_data = pipeline.radial_visualization(optimally_ordered_tree, original_tree, node_mapping, radial_visualization_method=constants.RADIAL_LAYOUT_LEAF_COUNT, show_flag=True)
    # evaluation_pipeline.run_single_evaluation_suite('S116180', constants.RADIAL_LAYOUT_LEAF_COUNT)
