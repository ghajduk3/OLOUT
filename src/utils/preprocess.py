import os
import json
import rootpath
from nexus_reader import NexusReader
import re
import numpy as np
from newick import Parser
from math import pi
from src.utils.tree import TreeNode
from src.visualizations import radial
from src.orderings.kolo import KOLO

BASE_URL = "http://purl.org/phylo/treebase/phylows/study/TB2:"
BASE_PATH = os.path.join(rootpath.detect(), "data","phylogenetic_trees")

def readNexusFile(path):
    return NexusReader.from_file(path)

def parseNexusFile(nexus, study_id)->dict:
    study_url = BASE_URL + study_id
    data = [{'NEXUS_FILE_URL': study_url} for i in range(len(nexus.trees))]

    for index, tree in enumerate(nexus.trees):
        if tree.trees:
            newick_tree_string = parseTree(tree[0])
            print(study_id,newick_tree_string)
            try:
                parsed_tree, parsed_mapping = Parser.parse_newick_tree(newick_tree_string)
            except:
                continue

            data[index]['NEWICK_TREE'] = newick_tree_string
            print(parsed_mapping)
            data[index]['DISTANCE_MATRIX'] = get_distance_matrix(parsed_tree)
            data[index]['NODE_MAPPING'] = parsed_mapping
    return data

def parseTree(newickTree):
    REGEX_PATTERN = r"\(+.+$"
    return re.search(REGEX_PATTERN, newickTree).group()

def writeToJson(data,directory_name):
    output_path = os.path.join(BASE_PATH, directory_name , "data.json")
    with open(output_path, 'w+') as out_file:
        print("dumping json", output_path)
        json.dump(data, out_file, indent=4)

def get_distance_matrix(tree):
    number_children = TreeNode.get_children_number(tree)
    distances = {}
    radial.construct_distances(tree,distances)
    level_order = radial.reverse_level_order_traversal(tree)
    print(level_order)
    print(tree.pre_order())
    return [[radial.LCA(distances, level_order,i,j) for j in range(number_children)] for i in range(number_children)]

if __name__ == "__main__":
    for directory in os.listdir(BASE_PATH):
        nexus = readNexusFile(os.path.join(BASE_PATH, directory, 'data.nex'))
        data = parseNexusFile(nexus, directory)
        writeToJson(data,directory)











# if __name__ == "__main__":
#     nex = readNexusFile("../../data/phylogenetic_trees/S10589/data.nex")
#     for tree in nex.trees:
#         print(tree.trees)

