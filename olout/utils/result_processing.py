import json
import os
import typing

import matplotlib
import pandas as pd
import rootpath

matplotlib.use("Qt5Agg")


EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')
BRANCH_LENGTH_BASE = '[BRANCH-LENGTH]'
LEAF_COUNT_BASE = '[LEAF-COUNT]'
BRANCH_LENGTH_PREFIX = BRANCH_LENGTH_BASE + '-'
LEAF_COUNT_PREFIX = LEAF_COUNT_BASE + '-'
EVALUATION_RESULTS_PATH= os.path.join(EVALUATION_DATA_PATH, 'evaluation_csv_data.csv')
EVALUATION_RESULTS_PATH_ADJ = os.path.join(EVALUATION_DATA_PATH, 'evaluation_csv_data_adj.csv')

def parse_json_evaluation_result(data: typing.Dict, filename):
    """
        Parses [FILENAME,NUMBER_LEAVES, NUMBER_NODES, EXECUTION_TIME, UNORDERED_STRESS, ORDERED_STRESS,
         ORDERED_ANGLE_CORRECTIONS_STRESS, ORDERED_FIXED_ANGLE_CORRECTIONS_STRESS] from  evaluation json object.
    """
    return [
        filename,
        data.get('number_leaves'),
        data.get('nodes_number'),
        data.get('execution_time_kolo'),
        data.get('ffac_best_correction_factor'),
        data.get("execution_time_radial_layout"),
        data.get("execution_time_corrections_adj_based"),
        data.get("execution_time_corrections_fixed_based"),
        data.get('unordered_tree_stress'),
        data.get('ordered_tree_stress'),
        data.get('ordered_tree_fixed_angle_correction_stress'),
        data.get('ordered_tree_adj_based_corrections_stress'),
    ]


def get_evaluation_results():
    """
        Parses all evaluation results and forms a single csv file for all evaluation results.
    """

    evaluation_results_branch_length = []
    evaluation_results_leaf_count = []

    for index, directory in enumerate(os.listdir(EVALUATION_DATA_PATH)):
        try:
            json_file_branch_length = open(os.path.join(EVALUATION_DATA_PATH, directory, 'data_branch_length.json'), 'r')
            evaluation_data_row_branch_length = parse_json_evaluation_result(json.load(json_file_branch_length), filename=directory)
            evaluation_results_branch_length.append(evaluation_data_row_branch_length)

            json_file_leaf_count = open(os.path.join(EVALUATION_DATA_PATH, directory, 'data_leaf_count.json'), 'r')
            evaluation_data_row_leaf_count = parse_json_evaluation_result(json.load(json_file_leaf_count), filename=directory)
            evaluation_results_leaf_count.append(evaluation_data_row_leaf_count)
        except:
            continue
    evaluation_results = [ev_result_br_len + evaluation_results_leaf_count[index][2:] for index, ev_result_br_len in enumerate(evaluation_results_branch_length)]
    evaluation_dataframe = pd.DataFrame(evaluation_results, columns=[
                                                                    'file_name',
                                                                    'number_leaves',
                                                                     'nodes_number',
                                                                     'execution_time_kolo',
                                                                     BRANCH_LENGTH_PREFIX + 'ffac_best_correction_factor',
                                                                        BRANCH_LENGTH_PREFIX + 'execution_time_radial_layout',
                                                                        BRANCH_LENGTH_PREFIX + 'execution_time_corrections_adj_based',
                                                                        BRANCH_LENGTH_PREFIX + 'execution_time_corrections_fixed_based',
                                                                     BRANCH_LENGTH_PREFIX + 'unordered_tree_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_fixed_angle_correction_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_adj_based_corrections_stress',
                                                                     LEAF_COUNT_PREFIX + 'nodes_number',
                                                                     LEAF_COUNT_PREFIX + 'execution_time_kolo',
                                                                     LEAF_COUNT_PREFIX + 'ffac_best_correction_factor',
                                                                        LEAF_COUNT_PREFIX + 'execution_time_radial_layout',
                                                                        LEAF_COUNT_PREFIX + 'execution_time_corrections_adj_based',
                                                                        LEAF_COUNT_PREFIX + 'execution_time_corrections_fixed_based',
                                                                     LEAF_COUNT_PREFIX + 'unordered_tree_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_fixed_angle_correction_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_adj_based_corrections_stress',
                                                                     ])
    evaluation_dataframe.to_csv(EVALUATION_RESULTS_PATH, index=False)


def evaluate_single_heuristic_visualization_methods(visualization_heuristic=BRANCH_LENGTH_PREFIX):
    """
        Calculates rank average of all methods for a specific visualization heuristic.
    """
    evaluation_results = pd.read_csv(EVALUATION_RESULTS_PATH)
    result_column_names = [visualization_heuristic + 'unordered_tree_stress', visualization_heuristic + 'ordered_tree_stress',
                            visualization_heuristic + 'ordered_tree_fixed_angle_correction_stress',
                            visualization_heuristic + 'ordered_tree_adj_based_corrections_stress']
    evaluation_results_heuristic = evaluation_results[result_column_names]
    result_ranks = evaluation_results_heuristic.rank(1, ascending=True, method='min')
    result_ranks_average = result_ranks.mean().tolist()
    return result_column_names, result_ranks_average


def evaluate_all_visualization_methods():
    """
        Calculates rank average of all methods across both visualization heuristics.
    """
    evaluation_results = pd.read_csv(EVALUATION_RESULTS_PATH)
    result_column_names = [BRANCH_LENGTH_PREFIX + 'unordered_tree_stress',
                           BRANCH_LENGTH_PREFIX + 'ordered_tree_stress',
                           BRANCH_LENGTH_PREFIX + 'ordered_tree_fixed_angle_correction_stress',
                           BRANCH_LENGTH_PREFIX + 'ordered_tree_adj_based_corrections_stress',
                           LEAF_COUNT_PREFIX + 'unordered_tree_stress',
                           LEAF_COUNT_PREFIX + 'ordered_tree_stress',
                           LEAF_COUNT_PREFIX + 'ordered_tree_fixed_angle_correction_stress',
                           LEAF_COUNT_PREFIX + 'ordered_tree_adj_based_corrections_stress']
    evaluation_results_heuristic = evaluation_results[result_column_names]

    result_ranks = evaluation_results_heuristic.rank(1, ascending=True, method='average')
    result_ranks_average = result_ranks.mean().tolist()

    return result_column_names, result_ranks_average



if __name__ == '__main__':
    get_evaluation_results()
    # col_name, col_avg = evaluate_single_heuristic_visualization_methods(visualization_heuristic=LEAF_COUNT_PREFIX)
    col_name, col_avg = evaluate_all_visualization_methods()
    print(col_name)
    print(col_avg)