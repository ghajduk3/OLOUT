import json
from src.orderings.kolo import KOLO
import numpy as np

def read_json_trees(input_path):
    with open(input_path, 'r') as input_file:
        data = json.load(input_file)
    return data


if __name__ == "__main__":
    data = read_json_trees("../data/phylo/S10374/data.json")
    # for tree in data:
    tree = data['NEWICK_TREE']
    distance_matrix = data['DISTANCE_MATRIX']
    print(tree)
    kolo = KOLO(tree,np.array(distance_matrix))

    print(kolo.optimal_leaf_ordering())
