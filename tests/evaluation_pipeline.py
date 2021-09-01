import time

from src.utils.preprocess import NexusDataPreprocess
from src.utils.newick import Parser
from src.utils import constants
from src.orderings.kolo import KOLO
from src.utils.utilities import writeToJson, transform_to_json_serializable
import rootpath, os, json
import numpy as np
from src.visualizations.radial import RadialLayoutLeafCount, RadialLayoutBranchLength
from bokeh.plotting import figure, show
from bokeh.layouts import row

FINAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'final_data')
EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')


def evaluation_suite(phylogenetic_tree:str, distance_matrix, radial_visualization=constants.RADIAL_LAYOUT_BRANCH_LENGTH):

    if radial_visualization == constants.RADIAL_LAYOUT_BRANCH_LENGTH:
        radial_layout = RadialLayoutBranchLength
    else:
        radial_layout = RadialLayoutLeafCount
    # Parses newick string to tree object
    tree, node_mapping = Parser.parse_newick_tree(phylogenetic_tree)

    kolo = KOLO(tree, np.array(distance_matrix), node_mapping)
    number_leaves = len(distance_matrix)
    number_nodes = len(tree.pre_order_internal())
    # kolo
    start_time_kolo = time.time()
    optimal_ordered_tree, optimal_leaf_ordering = kolo.get_optimal_leaf_ordering()
    elapsed_time_kolo = time.time() - start_time_kolo

    figure_arguments = {
        'x_axis_label': 'x',
        'y_axis_label': 'y',
        'plot_width': 500,
        'plot_height': 500,
        'match_aspect': True,
        'x_range': (-10, 10),
        'y_range': (-10, 10),
        'tools': "pan,wheel_zoom, zoom_in, zoom_out, box_select, lasso_select, box_zoom, save, undo, redo, reset, help"
    }
    #Radial visualization  of unordered tree
    radial_layout_unordered = radial_layout(tree)
    radial_points_unordered_tree, stress_all_node_pairs_unordered = radial_layout_unordered.get_radial_layout_coordinates()
    figure_arguments.update({'title' : f'Unordered tree, stress : {stress_all_node_pairs_unordered:.3f}'})
    fig_1 = figure(**figure_arguments)
    radial_layout_unordered.get_plotted_tree(tree, radial_points_unordered_tree, node_mapping, fig_1)


    # Ordered tree radial visualization
    radial_layout_ordered_tree = radial_layout(optimal_ordered_tree)
    radial_points_no_correction, stress_all_node_pairs_ordered = radial_layout_ordered_tree.get_radial_layout_coordinates()
    figure_arguments.update({'title': f"Ordered tree stress : {stress_all_node_pairs_ordered:.3f}"})
    fig_2 = figure(**figure_arguments)
    radial_layout_ordered_tree.get_plotted_tree(optimal_ordered_tree, radial_points_no_correction, node_mapping, fig_2)

    # Ordered tree pivot base angle corrections
    radial_points_ordered_pivot_based_angle_correction, stress_all_node_pairs_ordered_fixed_corrections = radial_layout_ordered_tree.get_radial_layout_coordinates_pivot_based_angle_corrections()
    figure_arguments.update({'title': f"Ordered tree pivot angle corrections , stress : {stress_all_node_pairs_ordered_fixed_corrections:.3f}"})
    fig_3 = figure(**figure_arguments)
    radial_layout_ordered_tree.get_plotted_tree(optimal_ordered_tree, radial_points_ordered_pivot_based_angle_correction, node_mapping, fig_3)

    # Ordered tree adjacent node based angle corrections
    radial_points_ordered_adjacent_node_based_angle_correction, stress_all_node_pairs_ordered_adj_node_corr = radial_layout_ordered_tree.get_radial_layout_coordinates_adj_nodes_based_angle_corrections()
    figure_arguments.update(
        {'title': f"Ordered tree adjacent node corrections,stress : {stress_all_node_pairs_ordered_adj_node_corr:.3f}"})
    fig_4 = figure(**figure_arguments)
    radial_layout_ordered_tree.get_plotted_tree(optimal_ordered_tree, radial_points_ordered_adjacent_node_based_angle_correction, node_mapping, fig_4)


    show(row(fig_1, fig_2, fig_3, fig_4, sizing_mode='scale_both'))
    print("Node mappings", node_mapping)
    print('-------------------- POSTORDER', optimal_ordered_tree)

    return {
        'nodes_number': number_nodes,
        'number_leaves': number_leaves,
        'leaf_ordering_kolo': optimal_leaf_ordering,
        'execution_time_kolo': elapsed_time_kolo,
        'optimal_leaf_ordering': optimal_leaf_ordering,
        'radial_points_unordered': transform_to_json_serializable(radial_points_unordered_tree),
        'radial_points_ordered_no_correction': transform_to_json_serializable(radial_points_no_correction),
        'radial_points_ordered_pivot_based_angle_correction': transform_to_json_serializable(radial_points_ordered_pivot_based_angle_correction),
        'radial_points_ordered_adjacent_node_based_angle_correction' : transform_to_json_serializable(radial_points_ordered_adjacent_node_based_angle_correction),
        'unordered_tree_stress': stress_all_node_pairs_unordered,
        'ordered_tree_stress': stress_all_node_pairs_ordered,
        'ordered_tree_fixed_angle_correction_stress': stress_all_node_pairs_ordered_fixed_corrections,
        'ordered_tree_adj_based_corrections_stress': stress_all_node_pairs_ordered_adj_node_corr,
    }


def run_evaluation_suites(recreate_data=False):
    if recreate_data:
        NexusDataPreprocess.preprocess()

    final_data_paths = sorted(os.listdir(EVALUATION_DATA_PATH))

    for index, directory in enumerate(final_data_paths):
        json_file = open(os.path.join(FINAL_DATA_PATH, directory, 'data.json'), 'r')
        data_json = json.load(json_file)
        nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
        try:
            evaluated_data = evaluation_suite(phylogenetic_newick_string, distance_matrix, radial_visualization=constants.RADIAL_LAYOUT_BRANCH_LENGTH)
            writeToJson(evaluated_data, os.path.join(EVALUATION_DATA_PATH, directory))
        except Exception as e:
            continue


def run_single_evaluation_suite(suite_name:str):
    json_file = open(os.path.join(FINAL_DATA_PATH, suite_name, 'data.json'), 'r')
    data_json = json.load(json_file)
    nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
    evaluation_suite(phylogenetic_newick_string, distance_matrix, radial_visualization=constants.RADIAL_LAYOUT_BRANCH_LENGTH)



if __name__ == '__main__':
    run_evaluation_suites()