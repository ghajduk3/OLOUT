import os
import json
from nexus_reader import NexusReader
import re

BASE_URL = "http://purl.org/phylo/treebase/phylows/study/TB2:"
BASE_PATH = "../../data/phylogenetic_trees"

def readNexusFile(path):
    return NexusReader.from_file(path)

def parseNexusFile(nexus, study_id)->dict:
    study_url = BASE_URL + study_id
    data = [{'TREE_URL' : study_url} for i in range(len(nexus.trees))]

    for index, tree in enumerate(nexus.trees):
        if tree.trees:
            data[index]['NEWICK_TREE'] = parseTree(tree[0])
    return data

def parseTree(newickTree):
    REGEX_PATTERN = r"\(+.+$"
    return re.search(REGEX_PATTERN, newickTree).group()

def writeToJson(data,directory_name):
    output_path = os.path.join(BASE_PATH, directory_name , "data.json")
    with open(output_path, 'w+') as out_file:
        print("dumping json", output_path)
        json.dump(data, out_file, indent=4)

if __name__ == "__main__":
    for directory in os.listdir(BASE_PATH):
        nexus = readNexusFile(os.path.join(BASE_PATH, directory, 'data.nex'))
        data = parseNexusFile(nexus, directory)
        writeToJson(data,directory)











# if __name__ == "__main__":
#     nex = readNexusFile("../../data/phylogenetic_trees/S10589/data.nex")
#     for tree in nex.trees:
#         print(tree.trees)

