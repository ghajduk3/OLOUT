import time

import json
import os
import rootpath

from src.utils import constants
from src.utils import pipeline
from src.utils.preprocess import NexusDataPreprocess
from src.utils.utilities import writeToJson

FINAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'final_data')
EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')


def evaluation_suite(phylogenetic_tree:str, distance_matrix, radial_visualization_method=constants.RADIAL_LAYOUT_BRANCH_LENGTH):
    # kolo
    start_time_kolo = time.time()
    unordered_tree, optimal_ordered_tree, optimal_leaf_ordering, node_mapping =pipeline.leaf_ordering_kolo(phylogenetic_tree)
    elapsed_time_kolo = time.time() - start_time_kolo

    number_leaves = len(distance_matrix)
    number_nodes = len(unordered_tree.pre_order_internal())

    # radial visualization evaluation
    radial_visualization_data = pipeline.radial_visualization(optimal_ordered_tree, unordered_tree, node_mapping, radial_visualization_method=radial_visualization_method, show_flag=True)

    evaluation_data = {
        'nodes_number': number_nodes,
        'number_leaves': number_leaves,
        'leaf_ordering_kolo': optimal_leaf_ordering,
        'execution_time_kolo': elapsed_time_kolo,
        'optimal_leaf_ordering': optimal_leaf_ordering,
    }
    evaluation_data.update(radial_visualization_data)

    return evaluation_data


def run_evaluation_suites(recreate_data=False):
    if recreate_data:
        NexusDataPreprocess.preprocess()

    final_data_paths = sorted(os.listdir(EVALUATION_DATA_PATH))

    for index, directory in enumerate(final_data_paths):
        json_file = open(os.path.join(FINAL_DATA_PATH, directory, 'data.json'), 'r')
        data_json = json.load(json_file)
        nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
        try:
            evaluated_data = evaluation_suite(phylogenetic_newick_string, distance_matrix, radial_visualization_method=constants.RADIAL_LAYOUT_LEAF_COUNT)
            writeToJson(evaluated_data, os.path.join(EVALUATION_DATA_PATH, directory))
        except Exception:
            continue


def run_single_evaluation_suite(suite_name: str):
    json_file = open(os.path.join(FINAL_DATA_PATH, suite_name, 'data.json'), 'r')
    data_json = json.load(json_file)
    nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
    evaluation_suite(phylogenetic_newick_string, distance_matrix, radial_visualization_method=constants.RADIAL_LAYOUT_LEAF_COUNT)



if __name__ == '__main__':
    run_evaluation_suites()