import typing
import pandas as pd
import os, rootpath, json

EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')


def parse_json_evaluation_result(data: typing.Dict, filename):
    return [
        filename,
        data.get('number_leaves'),
        data.get('nodes_number'),
        data.get('stress_ordered_no_correction'),
        data.get('global_stress_ordered_no_correction'),
        data.get('stress_ordered_angle_correction'),
        data.get('global_stress_ordered_angle_correction'),
        data.get('execution_time_kolo'),
    ]


def get_evaluation_results():
    evaluation_results = []
    for index, directory in enumerate(os.listdir(EVALUATION_DATA_PATH)):
        json_file = open(os.path.join(EVALUATION_DATA_PATH, directory, 'data.json'), 'r')
        evaluation_data_row = parse_json_evaluation_result(json.load(json_file), filename=directory)
        evaluation_results.append(evaluation_data_row)

    evaluation_dataframe = pd.DataFrame(evaluation_results, columns=[
                                                                    'file_name',
                                                                    'number_leaves',
                                                                     'nodes_number',
                                                                     'stress_ordered_no_correction',
                                                                     'global_stress_ordered_no_correction',
                                                                     'stress_ordered_angle_correction',
                                                                     'global_stress_ordered_angle_correction',
                                                                     'execution_time_kolo',
                                                                     ])

    evaluation_dataframe.to_csv(os.path.join(EVALUATION_DATA_PATH, 'evaluation_csv_data.csv'), index=False)


if __name__ == '__main__':
    get_evaluation_results()
