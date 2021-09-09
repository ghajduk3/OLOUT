import json
import os
import typing

import numpy


def write_to_json(data, outputh_base_path, file_name='data'):
    if data:
        if not os.path.exists(outputh_base_path):
            os.mkdir(outputh_base_path)
        output_path = os.path.join(outputh_base_path, file_name + ".json")
        with open(output_path, 'w+') as out_file:
            print("dumping json", output_path)
            json.dump(data, out_file, indent=4)


def transform_to_json_serializable(data: typing.Dict[typing.AnyStr, numpy.array]):
    return {k: v.tolist() for k, v in data.items()}
