import typing
import pandas as pd
import os, rootpath, json
import Orange.evaluation as orange_evaluation
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")


EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')
BRANCH_LENGTH_BASE = '[BRANCH-LENGTH]'
LEAF_COUNT_BASE = '[LEAF-COUNT]'
BRANCH_LENGTH_PREFIX = BRANCH_LENGTH_BASE + '-'
LEAF_COUNT_PREFIX = LEAF_COUNT_BASE + '-'
EVALUATION_RESULTS_PATH = os.path.join(EVALUATION_DATA_PATH, 'evaluation_csv_data.csv')

def parse_json_evaluation_result(data: typing.Dict, filename):
    return [
        filename,
        data.get('number_leaves'),
        data.get('nodes_number'),
        data.get('execution_time_kolo'),
        data.get('unordered_tree_stress'),
        data.get('ordered_tree_stress'),
        data.get('ordered_tree_fixed_angle_correction_stress'),
        data.get('ordered_tree_adj_based_corrections_stress'),
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
                                                                     BRANCH_LENGTH_PREFIX + 'unordered_tree_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_fixed_angle_correction_stress',
                                                                     BRANCH_LENGTH_PREFIX + 'ordered_tree_adj_based_corrections_stress',
                                                                     LEAF_COUNT_PREFIX + 'nodes_number',
                                                                     LEAF_COUNT_PREFIX + 'execution_time_kolo',
                                                                     LEAF_COUNT_PREFIX + 'unordered_tree_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_fixed_angle_correction_stress',
                                                                     LEAF_COUNT_PREFIX + 'ordered_tree_adj_based_corrections_stress',
                                                                     ])

    evaluation_dataframe.to_csv(EVALUATION_RESULTS_PATH, index=False)


def evaluate_single_heuristic_visualization_methods(visualization_heuristic=BRANCH_LENGTH_PREFIX):
    evaluation_results = pd.read_csv(EVALUATION_RESULTS_PATH)
    result_column_names = [visualization_heuristic + 'unordered_tree_stress', visualization_heuristic + 'ordered_tree_stress',
                            visualization_heuristic + 'ordered_tree_fixed_angle_correction_stress',
                            visualization_heuristic + 'ordered_tree_adj_based_corrections_stress']
    evaluation_results_heuristic = evaluation_results[result_column_names]
    result_ranks = evaluation_results_heuristic.rank(1, ascending=False, method='first')
    result_ranks_average = result_ranks.mean().tolist()
    cd = orange_evaluation.compute_CD(result_ranks_average, 48)
    print(result_column_names)
    print(result_ranks_average)
    orange_evaluation.graph_ranks(result_ranks_average, result_column_names, cd=cd, width=6, textspace=1.5)
    # plt.show()

def evaluate_all_visualization_methods():
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
    result_ranks = evaluation_results_heuristic.rank(1, ascending=False, method='first')
    result_ranks_average = result_ranks.mean().tolist()
    cd = orange_evaluation.compute_CD(result_ranks_average, 48)
    print(result_column_names)
    print(result_ranks_average)
    orange_evaluation.graph_ranks(result_ranks_average, result_column_names, cd=cd, width=6, textspace=1.5)



if __name__ == '__main__':

    evaluate_all_visualization_methods()