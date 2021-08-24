import time

from src.utils.preprocess import NexusDataPreprocess
from src.utils.newick import Parser
from src.orderings.kolo import KOLO
from src.utils.utilities import writeToJson, transform_to_json_serializable
import rootpath, os, json
import numpy as np
from src.visualizations.radial import RadialLayout,RadialLayoutTreeLength
from bokeh.plotting import figure, show
from bokeh.layouts import row

FINAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'final_data')
EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')


def evaluation_suite(phylogenetic_tree, distance_matrix):
    tree, node_mapping = Parser.parse_newick_tree(phylogenetic_tree)
    kolo = KOLO(tree, np.array(distance_matrix), node_mapping)
    number_leaves = len(distance_matrix)
    number_nodes = len(tree.pre_order_internal())
    # kolo
    start_time_kolo = time.time()
    optimal_ordered_tree, optimal_leaf_ordering = kolo.get_optimal_leaf_ordering()
    elapsed_time_kolo = time.time() - start_time_kolo

    # radial_visualization
    radial_layout = RadialLayoutTreeLength(optimal_ordered_tree)
    radial_points_no_correction, stress_no_correction, global_stress_no_correction = radial_layout.get_radial_layout_coordinates()
    figure_arguments = {
        'title': f"Phylogenetic tree leaf ordering, stress : {stress_no_correction:.5f}",
        'x_axis_label': 'x',
        'y_axis_label': 'y',
        'plot_width': 500,
        'plot_height': 500,
        'match_aspect': True,
        'x_range': (-10, 10),
        'y_range': (-10, 10),
        'tools': "pan,wheel_zoom, zoom_in, zoom_out, box_select, lasso_select, box_zoom, save, undo, redo, reset, help"
    }
    p = figure(**figure_arguments)
    radial_layout.get_plotted_tree(tree, radial_points_no_correction, node_mapping, p)

    radial_points_angle_correction, stress_angle_correction, global_stress_angle_correction = radial_layout.get_radial_layout_coordinates_angle_corrections()

    figure_arguments.update({'title': f"Phylogenetic tree leaf ordering, stress : {stress_angle_correction:.5f}"})
    p1 = figure(**figure_arguments)
    radial_layout.get_plotted_tree(tree, radial_points_angle_correction, node_mapping, p1)
    show(row(p,p1))
    print(optimal_leaf_ordering)
    return {
        'nodes_number': number_nodes,
        'number_leaves': number_leaves,
        'leaf_ordering_kolo': optimal_leaf_ordering,
        'execution_time_kolo': elapsed_time_kolo,
        'optimal_leaf_ordering': optimal_leaf_ordering,
        'radial_points_ordered_no_correction': transform_to_json_serializable(radial_points_no_correction),
        'radial_points_ordered_angle_correction': transform_to_json_serializable(radial_points_angle_correction),
        'stress_ordered_no_correction': stress_no_correction,
        'global_stress_ordered_no_correction': global_stress_no_correction,
        'stress_ordered_angle_correction': stress_angle_correction,
        'global_stress_ordered_angle_correction': global_stress_angle_correction,
    }


def run_evaluation_suites(recreate_data=False):
    if recreate_data:
        NexusDataPreprocess.preprocess()

    processed_trees_file = open(os.path.join(rootpath.detect(), 'data', 'processed_trees.txt'), 'w')

    final_data_paths = sorted(os.listdir(FINAL_DATA_PATH))[70:]

    for index, directory in enumerate(final_data_paths):
        json_file = open(os.path.join(FINAL_DATA_PATH, directory, 'data.json'), 'r')
        data_json = json.load(json_file)
        nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
        try:
            evaluated_data = evaluation_suite(phylogenetic_newick_string, distance_matrix)
            writeToJson(evaluated_data, os.path.join(EVALUATION_DATA_PATH, directory))
        except Exception as e:
            continue


def run_single_evaluation_suite(suite_name:str):
    json_file = open(os.path.join(FINAL_DATA_PATH, suite_name, 'data.json'), 'r')
    data_json = json.load(json_file)
    nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
    evaluation_suite(phylogenetic_newick_string, distance_matrix)


if __name__ == '__main__':
    run_evaluation_suites() 
