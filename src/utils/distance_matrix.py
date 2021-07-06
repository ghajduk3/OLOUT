import numpy as np
from src.utils.tree import TreeNode

class ReconstructDistanceMatrix:
    def __init__(self, tree):
        self.tree = tree
        self.levels = {}
        self.distances = {}

    def get_reconstructed_distance_matrix(self):
        root_node_id = self.tree.get_id()
        self.distances[root_node_id] = [None, 0]
        tree_children_number = TreeNode.get_children_number(self.tree)
        self.__construct_distances_levels(self.tree, 1)
        return np.array([[self.__get_pair_distance(i, j) for j in range(tree_children_number)] for i in range(tree_children_number)])

    def __construct_distances_levels(self, tree_node  , level):
        node_id = tree_node.get_id()
        self.levels[node_id] = level
        for child in tree_node.get_children():
            child_id = child.get_id()
            self.__construct_distances_levels(child, level+1)
            self.distances[child_id] = [node_id,child.get_distance()]

    def __get_pair_distance(self, node_1, node_2):
        if self.levels[node_1] - 1 > self.levels[node_2] - 1:
            node_1, node_2 = node_2, node_1
        lvl_diff = (self.levels[node_2] - 1) - (self.levels[node_1] - 1)
        travel_dis_1 = 0
        travel_dis_2 = 0
        while lvl_diff > 0:
            node_2 , distance = self.distances[node_2]
            lvl_diff-=1
            travel_dis_2 += distance

        if node_1 == node_2:
            return travel_dis_1 + travel_dis_2

        while self.distances[node_1][0] != self.distances[node_2][0]:
            node_1, distance_1 = self.distances[node_1]
            node_2, distance_2 = self.distances[node_2]
            travel_dis_1 += distance_1
            travel_dis_2 += distance_2
        travel_dis_1 += self.distances[node_1][1]
        travel_dis_2 += self.distances[node_2][1]
        return travel_dis_1 + travel_dis_2