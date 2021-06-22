import json
from src.orderings.kolo import KOLO
from src.orderings.kolo import KOLO
from src.utils.newick import Parser
import numpy as np
from src.utils.preprocess import get_distance_matrix
import itertools

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
    tree_string_1 = "(F:5.0000,(C:2.000000,(B:4.000000, A:1.000000):1.000000):2.000000,(E:2.000000, D:3.000000):1.000000);"
    tree = Parser.parse_newick_tree(tree_string_1)[0]
    distance = get_distance_matrix(tree)
    print(distance)

    # tree = Parser.parse_newick_tree(tree_string_1)[0]
    # print([child.id for child in tree.children])
    kolo = KOLO(tree_string_1,np.array(distance))

    print(kolo.get_optimal_leaf_ordering())


    def calculate_ordering_cost(ordering, distance):
        return sum([distance[ordering[i]][ordering[i + 1]] for i in range(len(ordering) - 1)])

    def brute_force_optimal_ordering(leaves, distance_matrix):
        orderings = min(
            [(perm, calculate_ordering_cost(perm, distance_matrix)) for perm in itertools.permutations(leaves)],
            key=lambda x: x[1])
        return orderings


    leaves = tree.pre_order()
    print(brute_force_optimal_ordering(leaves, distance))


