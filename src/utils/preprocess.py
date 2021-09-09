import os
import re

import rootpath

from src.utils import exceptions
from src.utils.distance_matrix import ReconstructDistanceMatrix
from src.utils.exceptions import InvalidNewickTreeReconstruction
from src.utils.newick import Parser
from src.utils.nexus_reader import NexusReader
from src.utils.utilities import write_to_json

BASE_URL = "http://purl.org/phylo/treebase/phylows/study/TB2:"
NEXUS_SOURCE_DATA_PATH = os.path.join(rootpath.detect(), "data", "source_data")
NEXUS_FINAL_DATA_PATH = os.path.join(rootpath.detect(), "data", "final_data")


class NexusDataPreprocess:
    """
      Class that parses nexus files, preprocess and constructs dataset of phylogenetic trees. Additionaly,
      for each phylogenetic tree in Newick string format a distance matrix is constructed.
      NEXUS_FILE_URL, NEWICK_TREE, DISTANCE_MATRIX, NODE_MAPPING are collected for each data file and are extracted into
      the json shaped final data.
    """
    @staticmethod
    def read_nexus_file(nexus_file_path):
        try:
            nexus_object, nexus_study_url = NexusReader.from_file(nexus_file_path)
            return nexus_object, nexus_study_url
        except Exception:
            raise exceptions.ParseError(f"Unable to read Nexus file from path : {nexus_file_path}")

    @staticmethod
    def parse_nexus_file(nexus_object, nexus_study_url):

        def parse_tree(newickTree):
            REGEX_PATTERN = r"\(+.+$"
            return re.search(REGEX_PATTERN, newickTree).group()

        parsed_nexus_data = []

        if nexus_object.trees:
            for nexus_tree in nexus_object.trees:
                if nexus_tree.trees:
                    try:
                        newick_tree_string = parse_tree(nexus_tree[0])
                        parsed_tree, parsed_mapping = Parser.parse_newick_tree(newick_tree_string)
                        reconstructed_distance_matrix = ReconstructDistanceMatrix(parsed_tree).get_reconstructed_distance_matrix()
                        parsed_data = {
                            'NEXUS_FILE_URL': nexus_study_url,
                            'NEWICK_TREE': newick_tree_string,
                            'DISTANCE_MATRIX': reconstructed_distance_matrix.tolist(),
                            'NODE_MAPPING': parsed_mapping
                        }
                        parsed_nexus_data.append(parsed_data)
                    except Exception:
                        continue

        return parsed_nexus_data


    @staticmethod
    def preprocess():
        for index, file in enumerate(sorted(os.listdir(NEXUS_SOURCE_DATA_PATH))[1800:]):
            input_path = os.path.join(NEXUS_SOURCE_DATA_PATH, str(index) + ".nex")
            if not os.path.exists(input_path):
                continue
            try:
                nexus, site_url = NexusDataPreprocess.read_nexus_file(input_path)
                directory = site_url.split("/")[-1].split(":")[-1]
            except:
                continue

            parsed_nexus_data = NexusDataPreprocess.parse_nexus_file(nexus, site_url)

            if parsed_nexus_data:
                for index, nexus_data in enumerate(parsed_nexus_data):
                    write_to_json(nexus_data, os.path.join(NEXUS_FINAL_DATA_PATH, directory+str(index)))
            else:
                continue
if __name__ == '__main__':
    NexusDataPreprocess.preprocess()