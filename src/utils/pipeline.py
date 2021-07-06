from src.orderings.kolo import KOLO
from src.utils.newick import Parser
from src.utils.distance_matrix import ReconstructDistanceMatrix
from src.utils import constants

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

def radial_visualization(ordered_tree, tree_node_mapping):
    pass