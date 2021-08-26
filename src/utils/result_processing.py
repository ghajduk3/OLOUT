import typing
import pandas as pd
import os, rootpath, json

EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')
BRANCH_LENGTH_PREFIX = '[BRANCH-LENGTH]-'
LEAF_COUNT_PREFIX = '[LEAF-COUNT]-'

def parse_json_evaluation_result(data: typing.Dict, filename):
    return [
        filename,
        data.get('number_leaves'),
        data.get('nodes_number'),
        data.get('execution_time_kolo'),
        data.get('unordered_tree_pivot_based_stress'),
        data.get('unordered_tree_adj_node_based_stress'),
        data.get('ordered_tree_pivot_based_stress'),
        data.get('ordered_tree_adj_node_based_stress'),
        data.get('ordered_tree_pivot_based_stress_pivot_correction'),
        data.get('ordered_tree_adj_based_stress_adj_nodes_correction'),

    ]


def get_evaluation_results():
    evaluation_results_branch_length = []
    evaluation_results_leaf_count = []

    for index, directory in enumerate(os.listdir(EVALUATION_DATA_PATH)):
        json_file_branch_length = open(os.path.join(EVALUATION_DATA_PATH, directory, 'data.json'), 'r')
        evaluation_data_row_branch_length = parse_json_evaluation_result(json.load(json_file_branch_length), filename=directory)
        evaluation_results_branch_length.append(evaluation_data_row_branch_length)

        json_file_leaf_count = open(os.path.join(EVALUATION_DATA_PATH, directory, 'data_leaf_count.json'), 'r')
        evaluation_data_row_leaf_count = parse_json_evaluation_result(json.load(json_file_leaf_count), filename=directory)
        evaluation_results_leaf_count.append(evaluation_data_row_leaf_count)
    evaluation_results = [ev_result_br_len + evaluation_results_leaf_count[index][2:] for index, ev_result_br_len in enumerate(evaluation_results_branch_length)]
    evaluation_dataframe = pd.DataFrame(evaluation_results, columns=[
                                                                    'file_name',
                                                                    'number_leaves',
                                                                     'nodes_number',
                                                                     'execution_time_kolo',
                                                                     BRANCH_LENGTH_PREFIX + 'unordered_tree_pivot_based_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'unordered_tree_adj_node_based_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_pivot_based_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_adj_node_based_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_pivot_based_stress_pivot_correction',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_adj_based_stress_adj_nodes_correction',
                                                                     LEAF_COUNT_PREFIX + 'nodes_number',
                                                                     LEAF_COUNT_PREFIX + 'execution_time_kolo',
                                                                     LEAF_COUNT_PREFIX + 'unordered_tree_pivot_based_stress',
                                                                     LEAF_COUNT_PREFIX + 'unordered_tree_adj_node_based_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_pivot_based_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_adj_node_based_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_pivot_based_stress_pivot_correction',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_adj_based_stress_adj_nodes_correction',
                                                                     ])

    evaluation_dataframe.to_csv(os.path.join(EVALUATION_DATA_PATH, 'evaluation_csv_data.csv'), index=False)


if __name__ == '__main__':
    get_evaluation_results()
