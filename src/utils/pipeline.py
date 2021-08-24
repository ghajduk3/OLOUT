from src.orderings.kolo import KOLO
from src.utils.newick import Parser
from src.utils.distance_matrix import ReconstructDistanceMatrix
from src.utils import constants
from src.visualizations import radial
from bokeh.plotting import figure, show
from bokeh.io import export_png

import plotly.graph_objects as go
import plotly.graph_objs.scatter as sc

import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("Qt5Agg")


def leaf_ordering_kolo(phylogenetic_tree : str):
    """

    """
    tree, node_mapping = Parser.parse_newick_tree(phylogenetic_tree)
    distance_matrix = ReconstructDistanceMatrix(tree).get_reconstructed_distance_matrix()
    kolo = KOLO(tree,distance_matrix,node_mapping)
    optimal_ordered_tree, optimal_leaf_ordering = kolo.get_optimal_leaf_ordering()
    return optimal_ordered_tree, optimal_leaf_ordering, node_mapping


def leaf_ordering_alo(phylogenetic_tree : str):
    """

    """
    pass


def leaf_ordering_dimensionality_reduction(phylogenetic_tree : str, reduction_method = constants.DIMENSIONALITY_REDUCTION_METHOD_PCA):
    """

    """
    pass


def radial_visualization(ordered_tree, tree_node_mapping, apply_corrections=True):
    radial_layout = radial.RadialLayoutTreeLength(ordered_tree)
    if apply_corrections:
        radial_points, stress, global_stress = radial_layout.get_radial_layout_coordinates_angle_corrections()
    else:
        radial_points, stress, global_stress = radial_layout.get_radial_layout_coordinates()

    figure_arguments = {
        'title' : f"Phylogenetic tree leaf ordering, stress : {global_stress:.5f}, ordering_stress : {stress:.3f}",
        'x_axis_label' : 'x',
        'y_axis_label' : 'y',
        'plot_width' : 1700,
        'plot_height' : 1700,
        'match_aspect' : True,
        'x_range' : (-10,10),
        'y_range': (-10, 10),
        'tools' : "pan,wheel_zoom, zoom_in, zoom_out, box_select, lasso_select, box_zoom, save, undo, redo, reset, help"
    }
    p = figure(**figure_arguments)
    radial_layout.get_plotted_tree(ordered_tree, radial_points, tree_node_mapping,  p)
    show(p)



