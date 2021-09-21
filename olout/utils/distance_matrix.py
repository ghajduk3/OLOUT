import typing
import numpy as np

from olout.utils.tree import TreeNode


class ReconstructDistanceMatrix:
    """
      Class that reconstructs distance matrix from phylogenetic TreeNode object
      ```
      Attributes
      ----------
      tree : TreeNode
          TreeNode object that represents phylogenetic tree
      levels : typing.Dict
          dictionary that represents level of each node in a tree
      distances : typing.Dict
          dictionary that represents distances between tree nodes.
      Methods
      -------
      get_reconstructed_distance_matrix() -> np.ndarray
          reconstructs and calculates distance between all pairs of leaf nodes.
          Composes and returns distance matrix
      _construct_distances_levels(tree_node: TreeNode, level: int) -> None
          recursive function that traverses tree and calculates levels and distances.
      _get_pair_distance(node_1: str, node_2: str) -> typing.Float
          helper function that calculates the distance between two nodes.
      """
    def __init__(self, tree: TreeNode):
        self.tree = tree
        self.levels = {}
        self.distances = {}

    def get_reconstructed_distance_matrix(self) -> np.ndarray:
        root_node_id = self.tree.get_id()
        self.distances[root_node_id] = [None, 0]
        tree_children_number = TreeNode.get_children_number(self.tree)
        self._construct_distances_levels(self.tree, 1)
        return np.array([[self._get_pair_distance(i, j) for j in range(tree_children_number)] for i in range(tree_children_number)])

    def _construct_distances_levels(self, tree_node: TreeNode, level: int) -> None:
        node_id = tree_node.get_id()
        self.levels[node_id] = level
        for child in tree_node.get_children():
            child_id = child.get_id()
            self._construct_distances_levels(child, level+1)
            self.distances[child_id] = [node_id,child.get_distance()]

    def _get_pair_distance(self, node_1: typing.AnyStr, node_2: typing.AnyStr) -> float:
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