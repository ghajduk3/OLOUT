import os
import json
import rootpath
from src.utils.nexus_reader import NexusReader
import re
import numpy as np
from src.utils.newick import Parser
from math import pi
from src.utils.tree import TreeNode
from src.visualizations import radial
from src.orderings.kolo import KOLO

BASE_URL = "http://purl.org/phylo/treebase/phylows/study/TB2:"
BASE_PATH = os.path.join(rootpath.detect(), "data","phylogenetic_trees")

def readNexusFile(path):
    try:
        return NexusReader.from_file(path)
    except:
        raise Exception

def parseNexusFile(nexus, study_url)->dict:

    nexus_tree = nexus.trees[0]
    if nexus_tree.trees:
        try:
            newick_tree_string = parseTree(nexus_tree[0])
            parsed_tree, parsed_mapping = Parser.parse_newick_tree(newick_tree_string)
        except:
            raise Exception

        return {
                'NEXUS_FILE_URL': study_url,
                'NEWICK_TREE' : newick_tree_string,
                'DISTANCE_MATRIX' : get_distance_matrix(parsed_tree),
                'NODE_MAPPING' : parsed_mapping
                }


def parseTree(newickTree):
    REGEX_PATTERN = r"\(+.+$"
    return re.search(REGEX_PATTERN, newickTree).group()

def writeToJson(data,directory_name):
    if data:
        base_path = os.path.join(rootpath.detect(), "data","phylo", directory_name)
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        output_path = os.path.join(base_path, "data.json")
        with open(output_path, 'w+') as out_file:
            print("dumping json", output_path)
            json.dump(data, out_file, indent=4)

def get_distance_matrix(tree):
    number_children = TreeNode.get_children_number(tree)
    distances = {}
    radial.construct_distances(tree,distances)
    level_order = radial.reverse_level_order_traversal(tree)
    # print(level_order)
    # print(tree.pre_order())
    # print(distances)
    # print(radial.LCA(distances,level_order, 0 , 5))
    return [[radial.LCA(distances, level_order,i,j) for j in range(number_children)] for i in range(number_children)]

if __name__ == "__main__":
    for index, file in enumerate(os.listdir(os.path.join(rootpath.detect(), "data","nexus"))):
        input_path = os.path.join(rootpath.detect(), "data","nexus", str(index) + ".nex")
        if not os.path.exists(input_path):
            continue
        try:
            nexus, site_url = readNexusFile(input_path)
            directory = site_url.split("/")[-1].split(":")[-1]
        except:
            continue
        try:
            data = parseNexusFile(nexus, site_url)
            writeToJson(data, directory)
        except:
            continue