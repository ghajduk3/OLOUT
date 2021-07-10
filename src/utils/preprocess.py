import os
import json
import rootpath
from src.utils.nexus_reader import NexusReader
import re
import numpy as np
from src.utils.newick import Parser
from src.utils.utilities import writeToJson
from src.utils import exceptions
from src.utils.distance_matrix import ReconstructDistanceMatrix
BASE_URL = "http://purl.org/phylo/treebase/phylows/study/TB2:"
BASE_PATH = os.path.join(rootpath.detect(), "data","phylogenetic_trees")

class NexusDataPreprocess:
    NEXUS_SOURCE_DATA_PATH = os.path.join(rootpath.detect(), "data","source_data")
    NEXUS_FINAL_DATA_PATH = os.path.join(rootpath.detect(), "data", "final_data")

    @staticmethod
    def readNexusFile(nexus_file_path):
        try:
            nexus_object, nexus_study_url = NexusReader.from_file(nexus_file_path)
            return nexus_object, nexus_study_url
        except Exception:
            raise exceptions.ParseError(f"Unable to read Nexus file from path : {nexus_file_path}")

    @staticmethod
    def parseNexusFile(nexus_object, nexus_study_url):

        def parseTree(newickTree):
            REGEX_PATTERN = r"\(+.+$"
            return re.search(REGEX_PATTERN, newickTree).group()

        nexus_tree = nexus_object.trees[0]
        if nexus_tree.trees:
            try:
                newick_tree_string = parseTree(nexus_tree[0])
                parsed_tree, parsed_mapping = Parser.parse_newick_tree(newick_tree_string)
                reconstructed_distance_matrix = ReconstructDistanceMatrix(
                    parsed_tree).get_reconstructed_distance_matrix()
            except:
                raise Exception

            return {
                'NEXUS_FILE_URL': nexus_study_url,
                'NEWICK_TREE': newick_tree_string,
                'DISTANCE_MATRIX': reconstructed_distance_matrix,
                'NODE_MAPPING': parsed_mapping
            }

    @staticmethod
    def preprocess():
        for index, file in enumerate(os.listdir(NexusDataPreprocess.NEXUS_SOURCE_DATA_PATH)):
            input_path = os.path.join(NexusDataPreprocess.NEXUS_SOURCE_DATA_PATH, str(index) + ".nex")
            if not os.path.exists(input_path):
                continue
            try:
                nexus, site_url = NexusDataPreprocess.readNexusFile(input_path)
                directory = site_url.split("/")[-1].split(":")[-1]
            except:
                continue
            try:
                data = NexusDataPreprocess.parseNexusFile(nexus, site_url)
                writeToJson(data,os.path.join(NexusDataPreprocess.NEXUS_FINAL_DATA_PATH,directory))
            except:
                continue



