import json

def read_json_trees(input_path):
    with open(input_path, 'r') as input_file:
        data = json.load(input_file)
    return data


if __name__ == "__main__":
    data = read_json_trees("../data/phylogenetic_trees/S10942/data.json")
    # for tree in data:
    print(data[0]['NEWICK_TREE'])
