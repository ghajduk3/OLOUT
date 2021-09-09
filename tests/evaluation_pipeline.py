import json
import os
import time
import typing

import numpy as np
import rootpath

from src.utils import constants
from src.utils import pipeline
from src.utils.preprocess import NexusDataPreprocess
from src.utils.utilities import write_to_json

FINAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'final_data')
EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')


def evaluation_suite(phylogenetic_tree: str, distance_matrix: np.ndarray, radial_visualization_method=constants.RADIAL_LAYOUT_BRANCH_LENGTH) -> typing.Dict:
    """
    Sets up evaluation suite for phylogenetic tree. Evaluation suite consits of 1. obtaining optimal leaf ordering
    of phylogenetic tree, 2. radially visualize optimally ordered tree.

    Parameters
    ----------
    phylogenetic_tree : str
        phylogenetic tree represented as a Newick Tree string.
    distance_matrix : np.ndarray
        represents similarities between leaf nodes of phylogenetic tree
    radial_visualization_method : str
        heuristic method that is to be used with RadialVisualization algorithm

    Returns
    ------
    evaluation_data : Dict
        dictionary that represents a set of evaluation data.
    """
    # kolo
    start_time_kolo = time.time()
    unordered_tree, optimal_ordered_tree, optimal_leaf_ordering, node_mapping=pipeline.leaf_ordering_kolo(phylogenetic_tree)
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


def run_evaluation_suites(recreate_data=False, radial_visualization_method=constants.RADIAL_LAYOUT_LEAF_COUNT, file_name='data') -> None:
    """
    Driver method that runs evaluation suite for each phylogenetic tree from dataset.

    Parameters
    ----------
    recreate_data : bool
        flag that indicates whether the process of parsing and creating evaluation dataset is to be performed.
    radial_visualization_method : str
        heuristic method that is to be used with RadialVisualization algorithm
    """
    if recreate_data:
        NexusDataPreprocess.preprocess()

    final_data_paths = sorted(os.listdir(EVALUATION_DATA_PATH))

    for index, directory in enumerate(final_data_paths):
        json_file = open(os.path.join(FINAL_DATA_PATH, directory, 'data.json'), 'r')
        data_json = json.load(json_file)
        nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
        try:
            evaluated_data = evaluation_suite(phylogenetic_newick_string, distance_matrix, radial_visualization_method=radial_visualization_method)
            write_to_json(evaluated_data, os.path.join(EVALUATION_DATA_PATH, directory), file_name=file_name)
        except Exception:
            continue


def run_single_evaluation_suite(suite_name: str, radial_visualization_method=constants.RADIAL_LAYOUT_LEAF_COUNT) -> None:
    """
    Driver method that runs single evaluation suite.

    Parameters
    ----------
    recreate_data : bool
        flag that indicates whether the process of parsing and creating evaluation dataset is to be performed.
    radial_visualization_method : str
        heuristic method that is to be used with RadialVisualization algorithm
    """
    json_file = open(os.path.join(FINAL_DATA_PATH, suite_name, 'data.json'), 'r')
    data_json = json.load(json_file)
    nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
    evaluation_suite(phylogenetic_newick_string, distance_matrix, radial_visualization_method=radial_visualization_method)

if __name__ == '__main__':
    run_evaluation_suites()