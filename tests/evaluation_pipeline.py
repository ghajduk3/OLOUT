import time

from src.utils.preprocess import NexusDataPreprocess
from src.utils.newick import Parser
from src.orderings.kolo import KOLO
from src.utils.utilities import writeToJson
import rootpath, os, json
import numpy as np
from src.visualizations.radial import RadialLayout
from bokeh.plotting import figure, show

FINAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'final_data')
EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')


def evaluation_suite(phylogenetic_tree, distance_matrix):
    tree, node_mapping = Parser.parse_newick_tree(phylogenetic_tree)
    kolo = KOLO(tree, np.array(distance_matrix), node_mapping)
    number_leaves = len(distance_matrix)
    number_nodes = len(node_mapping.keys())

    radial_layout = RadialLayout(tree)
    radial_points, stress, global_stress = radial_layout.get_points_radial(False)
    figure_arguments = {
        'title': f"Phylogenetic tree leaf ordering, stress : {global_stress:.5f}",
        'x_axis_label': 'x',
        'y_axis_label': 'y',
        'plot_width': 1700,
        'plot_height': 1700,
        'match_aspect': True,
        'x_range': (-10, 10),
        'y_range': (-10, 10),
        'tools': "pan,wheel_zoom, zoom_in, zoom_out, box_select, lasso_select, box_zoom, save, undo, redo, reset, help"
    }
    p = figure(**figure_arguments)
    radial_layout.get_plotted_tree(tree, radial_points, node_mapping, p)
    # show(p)

    # kolo
    start_time_kolo = time.time()
    optimal_ordered_tree, optimal_leaf_ordering = kolo.get_optimal_leaf_ordering()
    elapsed_time_kolo = time.time() - start_time_kolo

    return {
        'nodes_number': number_nodes,
        'number_leaves': number_leaves,
        'leaf_ordering_kolo': optimal_leaf_ordering,
        'execution_time_kolo': elapsed_time_kolo

    }


def run_evaluation_suites(recreate_data=False):
    if recreate_data:
        NexusDataPreprocess.preprocess()

    for index, directory in enumerate(os.listdir(FINAL_DATA_PATH)):
        json_file = open(os.path.join(FINAL_DATA_PATH, directory, 'data.json'), 'r')
        data_json = json.load(json_file)
        nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
        evaluated_data = evaluation_suite(phylogenetic_newick_string, distance_matrix)
        writeToJson(evaluated_data, os.path.join(EVALUATION_DATA_PATH, directory))


if __name__ == '__main__':
    run_evaluation_suites()
