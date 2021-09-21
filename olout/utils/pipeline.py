import typing

import matplotlib
from bokeh.layouts import row
from bokeh.plotting import figure, show

from olout.orderings.kolo import KOLO
from olout.utils import constants
from olout.utils.distance_matrix import ReconstructDistanceMatrix
from olout.utils.newick import Parser
from olout.utils.tree import TreeNode
from olout.utils.utilities import transform_to_json_serializable

matplotlib.use("Qt5Agg")


def leaf_ordering_kolo(phylogenetic_tree: str) -> typing.Union[TreeNode, typing.List, typing.Dict]:
    """
    Parses input phylogenetic to the TreeNode object. Constructs the distance matrix and calculates optimal
    leaf ordering using KOLO for the given tree string.
    Returns optimally ordered tree, list of the nodes in a optimal leaf ordering and a node mapping.

    Parameters
    ----------
    phylogenetic_tree : str
        phylogenetic tree represented as a Newick Tree string.

    Returns
    ------
    tree : TreeNode
        represents an unordered tree object.
    optimal_ordered_tree : TreeNode
        represents an optimal ordered tree object.
    optimal_leaf_ordering : typing.List
        list that contains optimal ordering of leaf nodes
    node_mapping : typing.Dict
        represents mapping between similarity matrix indexes and phylogenetic tree leaf node labels.
    """
    tree, node_mapping = Parser.parse_newick_tree(phylogenetic_tree)
    distance_matrix = ReconstructDistanceMatrix(tree).get_reconstructed_distance_matrix()
    kolo = KOLO(tree,distance_matrix,node_mapping)
    optimal_ordered_tree, optimal_leaf_ordering = kolo.get_optimal_leaf_ordering()
    return tree, optimal_ordered_tree, optimal_leaf_ordering, node_mapping


def leaf_ordering_alo(phylogenetic_tree: str):
    """

    """
    pass


def leaf_ordering_dimensionality_reduction(phylogenetic_tree: str, reduction_method=constants.DIMENSIONALITY_REDUCTION_METHOD_PCA) -> typing.Union[TreeNode, typing.List, typing.Dict]:
    """
    Parses input phylogenetic to the TreeNode object. Constructs the distance matrix and calculates
    leaf ordering using specified dimensionality reduction method for the given tree string.
    Returns ordered tree, list of the nodes in a leaf ordering and a node mapping.

    Parameters
    ----------
    phylogenetic_tree : str
        phylogenetic tree represented as a Newick Tree string.
    reduction_method : str
        reduction method that is to be applied to order leaves. Available methods: PCA, TSNE, MDS

    Returns
    ------
    ordered_tree : TreeNode
        represents an ordered tree object.
    optimal_leaf_ordering : typing.List
        list that contains ordering of leaf nodes
    node_mapping : typing.Dict
        represents mapping between similarity matrix indexes and phylogenetic tree leaf node labels.
    """
    tree, node_mapping = Parser.parse_newick_tree(phylogenetic_tree)
    distance_matrix = ReconstructDistanceMatrix(tree).get_reconstructed_distance_matrix()
    dimensionality_reduction = constants.DIMENSIONALITY_REDUCTION_METHOD_MAPPINGS[reduction_method]
    leaf_ordering = dimensionality_reduction(distance_matrix, node_mapping).get_leaf_ordering()
    return None, leaf_ordering, node_mapping


def radial_visualization(ordered_tree: TreeNode, unordered_tree: TreeNode, tree_node_mapping: typing.Dict, radial_visualization_method=constants.RADIAL_LAYOUT_BRANCH_LENGTH, show_flag=False) -> typing.Dict:
    """
    Visualizes phylogenetic trees with Radial visualization. It creates a pipeline to evaluate and perform
    radial visualization on unordered tree, ordered tree and to perform angle correction methods on ordered tree.

    Parameters
    ----------
    ordered_tree : TreeNode
        TreeNode object that represents ordered phylogenetic tree.
    unordered_tree : TreeNode
        TreeNode object that represents unordered phylogenetic tree.
    node_mapping : typing.Dict
        represents mapping between similarity matrix indexes and phylogenetic tree leaf node labels.
    radial_visualization_method : typing.Str
        heuristic method that is to be used with RadialVisualization algorithm
    show_flag : bool
        flag that indicates whether to show Radial visualization figures.

    Returns
    ------
    evaluation_data : typing.Dict
        dictionary that represents a set of radial visualization data.
    """

    radial_layout = constants.RADIAL_VISUALIZATION_METHOD_MAPPINGS[radial_visualization_method]

    # Ordered tree
    radial_layout_ordered_tree = radial_layout(ordered_tree)
    radial_points, stress = radial_layout_ordered_tree.get_radial_layout_coordinates()
    radial_points_angle_based, stress_angle_based = radial_layout_ordered_tree.get_radial_layout_coordinates_adj_nodes_based_angle_corrections()
    radial_points_pivot_based, stress_pivot_based = radial_layout_ordered_tree.get_radial_layout_coordinates_fixed_factor_based_angle_corrections()

    # Unordered tree
    radial_layout_unordered_tree = radial_layout(unordered_tree)
    radial_points_unordered, stress_unordered = radial_layout_unordered_tree.get_radial_layout_coordinates()

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
        {'title': f"Unordered tree, stress : {stress_unordered:.3f}"})
    p_1 = figure(**figure_arguments)
    radial_layout_unordered_tree.get_plotted_tree(unordered_tree, radial_points_unordered, tree_node_mapping,  p_1)

    figure_arguments.update(
        {'title': f"Ordered tree no corrections,stress : {stress:.3f}"})
    p_2 = figure(**figure_arguments)
    radial_layout_ordered_tree.get_plotted_tree(ordered_tree, radial_points, tree_node_mapping,  p_2)

    figure_arguments.update(
        {'title': f"Ordered tree fixed factor corrections,stress : {stress_pivot_based:.3f}"})
    p_3 = figure(**figure_arguments)

    radial_layout_ordered_tree.get_plotted_tree(ordered_tree, radial_points_pivot_based, tree_node_mapping,  p_3)

    figure_arguments.update(
        {'title': f"Ordered tree adjacent node corrections,stress : {stress_angle_based:.3f}"})
    p_4 = figure(**figure_arguments)

    radial_layout_ordered_tree.get_plotted_tree(ordered_tree, radial_points_angle_based, tree_node_mapping,  p_4)

    if show_flag:
        show(row(p_1, p_2, p_3, p_4, sizing_mode='scale_both'))

    evaluation_data = {
                        'radial_points_unordered': transform_to_json_serializable(radial_points_unordered),
                        'radial_points_ordered_no_correction': transform_to_json_serializable(radial_points),
                        'radial_points_ordered_pivot_based_angle_correction': transform_to_json_serializable(radial_points_pivot_based),
                        'radial_points_ordered_adjacent_node_based_angle_correction': transform_to_json_serializable(radial_points_angle_based),
                        'unordered_tree_stress': stress_unordered,
                        'ordered_tree_stress': stress,
                        'ordered_tree_fixed_angle_correction_stress': stress_angle_based,
                        'ordered_tree_adj_based_corrections_stress': stress_pivot_based,
    }
    return evaluation_data




