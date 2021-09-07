from src.orderings.kolo import KOLO
from src.orderings import dimensionality_reduction as dimensionality_reduction_orderings
from src.utils.newick import Parser
from src.utils.distance_matrix import ReconstructDistanceMatrix
from src.utils import constants
from src.visualizations import radial
from bokeh.plotting import figure, show
from bokeh.io import export_png

import plotly.graph_objects as go
import plotly.graph_objs.scatter as sc
from bokeh.layouts import row

import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("Qt5Agg")


def leaf_ordering_kolo(phylogenetic_tree: str):
    """

    """
    tree, node_mapping = Parser.parse_newick_tree(phylogenetic_tree)
    distance_matrix = ReconstructDistanceMatrix(tree).get_reconstructed_distance_matrix()
    kolo = KOLO(tree,distance_matrix,node_mapping)
    optimal_ordered_tree, optimal_leaf_ordering = kolo.get_optimal_leaf_ordering()
    return optimal_ordered_tree, optimal_leaf_ordering, node_mapping


def leaf_ordering_alo(phylogenetic_tree: str):
    """

    """
    pass


def leaf_ordering_dimensionality_reduction(phylogenetic_tree: str, reduction_method=constants.DIMENSIONALITY_REDUCTION_METHOD_PCA):
    """

    """
    tree, node_mapping = Parser.parse_newick_tree(phylogenetic_tree)
    distance_matrix = ReconstructDistanceMatrix(tree).get_reconstructed_distance_matrix()
    dimensionality_reduction = constants.DIMENSIONALITY_REDUCTION_METHOD_MAPPINGS[reduction_method]
    optimal_leaf_ordering = dimensionality_reduction(distance_matrix, node_mapping).get_leaf_ordering()
    return None, optimal_leaf_ordering, node_mapping


def radial_visualization(ordered_tree, tree_node_mapping):
    radial_layout = radial.RadialLayoutBranchLength(ordered_tree)

    radial_points, stress = radial_layout.get_radial_layout_coordinates()
    radial_points_angle_based, stress_angle_based = radial_layout.get_radial_layout_coordinates_adj_nodes_based_angle_corrections()
    radial_points_pivot_based, stress_pivot_based = radial_layout.get_radial_layout_coordinates_pivot_based_angle_corrections()

    figure_arguments = {
        'x_axis_label' : 'x',
        'y_axis_label' : 'y',
        'plot_width' : 1700,
        'plot_height' : 1700,
        'match_aspect' : True,
        'x_range' : (-10,10),
        'y_range': (-10, 10),
        'tools' : "pan,wheel_zoom, zoom_in, zoom_out, box_select, lasso_select, box_zoom, save, undo, redo, reset, help"
    }
    figure_arguments.update(
        {'title': f"Ordered tree corrections,stress : {stress:.3f}"})
    p_1 = figure(**figure_arguments)

    radial_layout.get_plotted_tree(ordered_tree, radial_points, tree_node_mapping,  p_1)

    figure_arguments.update(
        {'title': f"Ordered tree pivot corrections,stress : {stress_pivot_based:.3f}"})
    p_2 = figure(**figure_arguments)

    radial_layout.get_plotted_tree(ordered_tree, radial_points_pivot_based, tree_node_mapping,  p_2)

    figure_arguments.update(
        {'title': f"Ordered tree adjacent node corrections,stress : {stress_angle_based:.3f}"})
    p_3 = figure(**figure_arguments)

    radial_layout.get_plotted_tree(ordered_tree, radial_points_angle_based, tree_node_mapping,  p_3)

    show(row(p_1, p_2, p_3, sizing_mode='scale_both'))





