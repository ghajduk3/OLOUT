import json
import os
import time
import typing

import numpy as np
import rootpath
import shutil
import pandas as pd
from collections import namedtuple

from olout.utils import constants
from olout.utils import pipeline
from olout.utils.newick import Parser
from olout.utils.preprocess import NexusDataPreprocess
from olout.utils.utilities import write_to_json

FINAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'final_data')
EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')

def tree_children_number(tree_node):
    if tree_node.is_leaf():
        return 0

    children = tree_node.get_children()

    num_children = len(children)
    for child in children:
        num_children += tree_children_number(child)
    return num_children

def get_average_children_per_tree(phylogenetic_tree):
    children_number = tree_children_number(phylogenetic_tree)
    number_nodes = len(phylogenetic_tree.pre_order_internal()) - len(phylogenetic_tree.pre_order())
    return children_number / number_nodes

def collect_stats_all_data():
    data_directories = os.listdir(EVALUATION_DATA_PATH)
    stat_data = []
    for index, data_directory_name in enumerate(data_directories):
        if data_directory_name != 'evaluation_csv_data.csv':
            try:
                data_path = open(os.path.join(FINAL_DATA_PATH, data_directory_name , 'data.json'),'r')
                json_data = json.load(data_path)
                nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = json_data.values()
                parsed_tree, tree_node_mapping = Parser.parse_newick_tree(phylogenetic_newick_string)
                avg_children = get_average_children_per_tree(parsed_tree)
                stat_data.append((data_directory_name, avg_children))
            except:
                continue
    return stat_data

def get_evaluation_results():
    return pd.read_csv(os.path.join(EVALUATION_DATA_PATH, 'evaluation_csv_data.csv'))


if __name__ == '__main__':
    stat = sorted(collect_stats_all_data(), key=lambda x:x[1])
    # print(len(stat))

    branch_df = pd.DataFrame(stat, columns=['file_name', 'avg_branch_factor'])
    evaluation_data_df = get_evaluation_results()
    merged_df = pd.merge(branch_df, evaluation_data_df, on='file_name')
    merged_df.to_csv(os.path.join(EVALUATION_DATA_PATH, 'evaluation_csv_data_br_factor.csv'), index=False)

