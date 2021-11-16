import json
from olout.orderings.kolo import KOLO
from olout.orderings.kolo import KOLO
from olout.utils.newick import Parser
import numpy as np
# from olout.utils.preprocess import get_distance_matrix
from olout.utils.distance_matrix import ReconstructDistanceMatrix
import itertools
from olout.visualizations import radial
from olout.utils import constants
from olout.utils import pipeline
import os
from olout.visualizations import radial
from bokeh.layouts import row
from bokeh.plotting import figure, show

from olout.utils.pipeline import leaf_ordering_kolo, radial_visualization
from olout.utils.evaluation_pipeline import run_single_evaluation_suite
import rootpath

FINAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'final_data')
EVALUATION_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'evaluations')
QUARANTINE_EVAL_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'quarantine_evaluations')
QUARANTINE_DATA_PATH = os.path.join(rootpath.detect(), 'data', 'quarantine')

def load_tree_from_data_dir_name(dir_name):
    json_file = open(os.path.join(FINAL_DATA_PATH, dir_name, 'data.json'), 'r')
    data_json = json.load(json_file)
    nexus_file_url, phylogenetic_newick_string, distance_matrix, tree_node_mapping = data_json.values()
    return phylogenetic_newick_string

if __name__ == '__main__':
    phylogenetic_tree_string = load_tree_from_data_dir_name('S148725')
    unordered_tree, optimal_ordered_tree, optimal_leaf_ordering, node_mapping = pipeline.leaf_ordering_kolo(phylogenetic_tree_string)

    layout_unordered = radial.RadialLayoutLeafCount(unordered_tree)
    layout_ordered = radial.RadialLayoutLeafCount(optimal_ordered_tree)
    # layout_unordered = radial.RadialLayoutBranchLength(unordered_tree)
    # layout_ordered = radial.RadialLayoutBranchLength(optimal_ordered_tree)

    radial_points_unordered, stress_unordered = layout_unordered.get_radial_layout_coordinates()
    radial_points_ordered, stress_ordered = layout_ordered.get_radial_layout_coordinates()
    radial_points_angle_based, stress_angle_based, counter_angle_based = layout_ordered.get_radial_layout_coordinates_adj_nodes_based_angle_corrections()
    radial_points_fixed_based, stress_fixed_based, counter_fixed_based = layout_ordered.get_radial_layout_coordinates_fixed_factor_based_angle_corrections()

    figure_arguments = {
        # 'x_axis_label' : 'x',
        # 'y_axis_label' : 'y',
        'plot_width' : 2500,
        'plot_height' : 2500,
        'match_aspect' : True,
        'x_range' : (-10,10),
        'y_range': (-10, 10),
        'tools' : "pan,wheel_zoom, zoom_in, zoom_out, box_select, lasso_select, box_zoom, save, undo, redo, reset, help",
    }

    figure_arguments.update(
        {'title': f"Unordered tree, average stress : {stress_unordered:.5f}"})
    p_1 = figure(**figure_arguments)
    layout_unordered.get_plotted_tree(unordered_tree, radial_points_unordered, node_mapping,  p_1)
    p_1.title.text_font_size = '50pt'
    # p_1.xaxis.axis_label_text_font_size = "20pt"
    # p_1.yaxis.axis_label_text_font_size = "25pt"
    # p_1.yaxis.major_label_text_font_size = "30pt"
    # p_1.xaxis.major_label_text_font_size = "30pt"
    # p_1.axis.visible = False
    p_1.xgrid.visible = False
    p_1.ygrid.visible = False
    p_1.outline_line_color = "black"
    p_1.outline_line_width = 4
    p_1.output_backend = "svg"
    show(p_1)

    figure_arguments.update(
        {'title': f"Optimally ordered tree using KOLO, average stress : {stress_ordered:.5f}"})
    p_2 = figure(**figure_arguments)
    layout_unordered.get_plotted_tree(optimal_ordered_tree, radial_points_ordered, node_mapping,  p_2)
    p_2.title.text_font_size = '50pt'
    # p_1.xaxis.axis_label_text_font_size = "20pt"
    # p_1.yaxis.axis_label_text_font_size = "25pt"
    # p_2.axis.visible = False
    # p_2.yaxis.major_label_text_font_size = "30pt"
    # p_2.xaxis.major_label_text_font_size = "30pt"
    p_2.xgrid.visible = False
    p_2.ygrid.visible = False
    p_2.outline_line_color = "black"
    p_2.outline_line_width = 4
    p_2.output_backend = "svg"
    show(p_2)

    figure_arguments.update(
        {'title': f"Optimally ordered tree using KOLO - ANBC corrections, average stress : {stress_angle_based:.5f}"})
    p_3 = figure(**figure_arguments)
    layout_unordered.get_plotted_tree(optimal_ordered_tree, radial_points_angle_based, node_mapping,  p_3)
    p_3.title.text_font_size = '50pt'
    # p_1.xaxis.axis_label_text_font_size = "20pt"
    # p_1.yaxis.axis_label_text_font_size = "25pt"
    # p_3.yaxis.major_label_text_font_size = "30pt"
    # p_3.xaxis.major_label_text_font_size = "30pt"
    # p_3.axis.visible = False

    p_3.xgrid.visible = False
    p_3.ygrid.visible = False
    p_3.outline_line_color = "black"
    p_3.outline_line_width = 4
    p_3.output_backend = "svg"
    show(p_3)

    figure_arguments.update(
        {'title': f"Optimally ordered tree using KOLO - FFAC corrections, average stress : {stress_fixed_based:.5f}"})
    p_4 = figure(**figure_arguments)
    layout_unordered.get_plotted_tree(optimal_ordered_tree, radial_points_fixed_based, node_mapping,  p_4)
    p_4.title.text_font_size = '50pt'
    # p_1.xaxis.axis_label_text_font_size = "20pt"
    # p_1.yaxis.axis_label_text_font_size = "25pt"
    # p_4.axis.visible = False

    # p_4.yaxis.major_label_text_font_size = "30pt"
    # p_4.xaxis.major_label_text_font_size = "30pt"
    p_4.xgrid.visible = False
    p_4.ygrid.visible = False
    p_4.outline_line_color = "black"
    p_4.outline_line_width = 4
    p_4.output_backend = "svg"
    show(p_4)
