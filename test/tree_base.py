import json
from src.orderings.kolo import KOLO
from src.orderings.kolo import KOLO
from src.utils.newick import Parser
import numpy as np
from src.utils.preprocess import get_distance_matrix
from src.visualizations import radial
import itertools
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("Qt5Agg")

def read_json_trees(input_path):
    with open(input_path, 'r') as input_file:
        data = json.load(input_file)
    return data


if __name__ == "__main__":

    dis_1 = np.array([[0, 5, 4, 7, 6, 8],
                    [5, 0, 7, 10, 9, 11],
                    [4, 7, 0, 7, 6, 8],
                    [7, 10, 7, 0, 5, 9],
                    [6, 9, 6, 5, 0, 8],
                    [8, 11, 8, 9, 8, 0]])

    # tree_string_1 = "(5:5.00000,(2:2.000000,(1:4.000000, 0:1.000000):1.000000):2.000000,(4:2.000000, 3:3.000000):1.000000);"
    # tree_string_1 = "((C:2.000000,(B:4.000000, A:1.000000):1.000000):2.000000,(E:2.000000, D:3.000000):1.000000,F:5.0000);"
    tree_string_1 = '(3:2.000000,4:1.000000,(2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000);'
    tree = Parser.parse_newick_tree(tree_string_1)[0]
    distance = get_distance_matrix(tree)
    print(distance)

    # tree = Parser.parse_newick_tree(tree_string_1)[0]
    # print([child.id for child in tree.children])
    kolo = KOLO(tree_string_1,np.array(distance))

    optimal_ordered_tree, optimal_leaf_ordering = kolo.get_optimal_leaf_ordering()


    # def calculate_ordering_cost(ordering, distance):
    #     return sum([distance[ordering[i]][ordering[i + 1]] for i in range(len(ordering) - 1)])
    #
    # def brute_force_optimal_ordering(leaves, distance_matrix):
    #     orderings = min(
    #         [(perm, calculate_ordering_cost(perm, distance_matrix)) for perm in itertools.permutations(leaves)],
    #         key=lambda x: x[1])
    #     return orderings
    #
    #
    # leaves = tree.pre_order()
    # print(brute_force_optimal_ordering(leaves, distance))

    raw_newick, mapping = Parser.parse_newick_tree(tree_string_1)
    # print(raw_newick.children)
    #
    radial_layout_1 = radial.RadialLayout(raw_newick)
    radial_points_raw, stress, stress_glob = radial_layout_1.get_points_radial()

    matplotlib.rc('text')
    # fig,(ax1,ax2, ax3) = plt.subplots(1,3)
    fig = plt.figure(figsize=(15, 5))
    # ax1.xlim((-3.5, 5.5))
    fig.suptitle("Leaf ordering for phylogenetic tree with Bar-Joseph intial leaf order")
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2, sharex=ax1, sharey=ax1)
    ax3 = fig.add_subplot(1, 3, 3, sharex=ax1, sharey=ax1)
    radial_layout_1.plot_tree(raw_newick, radial_points_raw, ax1)
    # ordered_tree, ordered_leaves = kolo_data.optimal_leaf_ordering()
    # print(ordered_leaves,ordered_tree.pre_order_internal())
    ax1.set_title(f"Unordered tree, stress = {stress:.2f}, {stress_glob:.2f}")
    # ax1.set_xlim((-4, 7.5))
    # ax1.set_ylim((-4, 7.5))
    # ax3.set_aspect('equal')
    radial_layout_2 = radial.RadialLayout(optimal_ordered_tree)
    points_ordered, stress_ordered, stress_ordered_glob = radial_layout_2.get_points_radial()
    # points_ordered, stress_ordered = get_points_radial(ordered_tree, correct=False)
    ax2.set_title(f"Ordered tree, stress = {stress_ordered:.2f}, {stress_ordered_glob:.2f}")
    # ax2.set_aspect('equal')
    # ax2.set_xlim((-4, 7.5))
    # ax2.set_ylim((-4, 7.5))
    radial_layout_1.plot_tree(optimal_ordered_tree, points_ordered, ax2)
    points_corrected_ordered, stress_ordered_corrected, stress_ordered_corrected_glob  = radial_layout_2.get_points_radial(apply_corrections=True)
    ax3.set_title(f"Ordered tree with angle corrections, stress = {stress_ordered_corrected:.2f}, {stress_ordered_corrected_glob:.2f}")
    # ax3.set_aspect('equal')
    # ax3.set_xlim((-4, 7.5))
    # ax3.set_ylim((-4, 7.5))
    radial_layout_1.plot_tree(optimal_ordered_tree, points_corrected_ordered, ax3)

    #
    plt.show()

