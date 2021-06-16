import os
import json
from nexus_reader import NexusReader
import re
import numpy as np
from newick import Parser
from math import pi
from src.utils.tree import TreeNode
from src.visualizations import radial
from src.orderings.kolo import KOLO

BASE_URL = "http://purl.org/phylo/treebase/phylows/study/TB2:"
BASE_PATH = "../../data/phylogenetic_trees"

def readNexusFile(path):
    return NexusReader.from_file(path)

def parseNexusFile(nexus, study_id)->dict:
    study_url = BASE_URL + study_id
    data = [{'TREE_URL' : study_url} for i in range(len(nexus.trees))]

    for index, tree in enumerate(nexus.trees):
        if tree.trees:
            newick_tree_string = parseTree(tree[0])
            print(study_id,newick_tree_string)
            # tree = Parser.parse_newick_tree(newick_tree_string)
            data[index]['NEWICK_TREE'] = newick_tree_string
            print(tree.translators)
            # data[index]['DISTANCE_MATRIX'] = get_distance_matrix(tree)
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
    print(number_children)
    l = {}
    x = {}
    omega = {}
    tau = {}
    distances = {}
    radial.postorder_traverse_radial(tree, l)
    root = tree.get_id()
    x[root] = np.array((0, 0))
    omega[root] = 2 * pi
    tau[root] = 0
    radial.preorder_traverse_radial(tree, None, root, x, l, omega, tau, distances)
    level_order = radial.reverse_level_order_traversal(tree)
    return [[radial.LCA(distances, level_order,i,j) for j in range(1,number_children+1)] for i in range(1,number_children+1)]

if __name__ == "__main__":
    for directory in os.listdir(BASE_PATH):
        nexus = readNexusFile(os.path.join(BASE_PATH, directory, 'data.nex'))
        data = parseNexusFile(nexus, directory)
        writeToJson(data,directory)











# if __name__ == "__main__":
#     nex = readNexusFile("../../data/phylogenetic_trees/S10589/data.nex")
#     for tree in nex.trees:
#         print(tree.trees)

