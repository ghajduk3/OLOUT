import os
import json
import rootpath
def writeToJson(data, outputh_base_path):
    if data:
        if not os.path.exists(outputh_base_path):
            os.mkdir(outputh_base_path)
        output_path = os.path.join(outputh_base_path, "data.json")
        with open(output_path, 'w+') as out_file:
            print("dumping json", output_path)
            json.dump(data, out_file, indent=4)
