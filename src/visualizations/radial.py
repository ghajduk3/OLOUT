import copy

import numpy as np
import math
from math import pi, cos, sin

from bokeh.models import ColumnDataSource, LabelSet
from numpy.linalg import norm

class RadialLayoutLeafCount:
    def __init__(self, tree):
        """
        Class that represents RadialLayoutAlgorithm

        ```

        Attributes
        ----------
        tree : str
            Phylogenetic tree to be visualized with RadialLayout algorithm.
        levels: Dict
             For each tree node holds values of number of leaves that are in nodes subtrees, node level, and the parent id.


        Methods
        -------
        closed()
            indicates whether the stream is open
        read_next()
            emits next stream token
        close()
            closes the stream

        """
        self.tree = copy.deepcopy(tree)
        self.levels = {}
        self.coordinates = {}
        self.omega = {}
        self.tau = {}
        self.distances = {}

        self.calculate_radial_layout_coordinates()

    def calculate_radial_layout_coordinates(self):
        self._postorder_traversal(self.tree, None, 1)
        root = self.tree.get_id()
        self.coordinates[root] = np.array((0, 0))
        self.omega[root] = 2 * pi
        self.tau[root] = 0
        self._preorder_traversal(self.tree, None, root)

    def get_radial_layout_coordinates(self):
        stress_all_node_pairs = self._calculate_stress_all_node_pairs(self.coordinates)
        return self.coordinates, stress_all_node_pairs

    def get_radial_layout_coordinates_pivot_based_angle_corrections(self):
        corrected_coordinates = self._apply_angle_corrections_fixed_correction_factor()
        stress_all_node_pairs = self._calculate_stress_all_node_pairs(corrected_coordinates)
        return corrected_coordinates, stress_all_node_pairs

    def get_radial_layout_coordinates_adj_nodes_based_angle_corrections(self):
        corrected_coordinates = self._apply_angle_corrections_adjacent_node_based()
        stress_all_node_pairs = self._calculate_stress_all_node_pairs(corrected_coordinates)
        return corrected_coordinates, stress_all_node_pairs

    def _postorder_traversal(self, tree_node, parent_node_id, level):
        """
        Traverses the tree recursively in a postorder manner, calculates the number of leaves in each node's subtree and calculates each node's level.

        Arguments:
            tree_node
            parent_node_id
            current_level
        """

        node_id = tree_node.get_id()
        self.levels[node_id] = [0, level, parent_node_id, 0]
        if tree_node.is_leaf():
            self.levels[node_id][0] = 1
            self.levels[node_id][3] = tree_node.get_distance()
        else:
            for child in tree_node.get_children():
                child_id = child.get_id()
                self._postorder_traversal(child, node_id, level + 1)
                self.levels[node_id][0] += self.levels[child_id][0]
                self.levels[node_id][3] += self.levels[child_id][3]
                self.distances[child_id] = [node_id, child.get_distance()]

    def _preorder_traversal(self, tree_node, parent, root_id):
        tree_node_id = tree_node.get_id()
        if tree_node_id != root_id:
            u = parent
            u_id = u.get_id()
            angle = self.tau[tree_node_id] + self.omega[tree_node_id] / 2
            self.coordinates[tree_node_id] = self.coordinates[u_id] + tree_node.get_distance() * np.array((cos(angle), sin(angle)))
        eta = self.tau[tree_node_id]
        for child in tree_node.get_children():
            child_id = child.get_id()
            self.omega[child_id] = 2 * pi * self.levels[child_id][0] / self.levels[root_id][0]
            self.tau[child_id] = eta
            eta += self.omega[child_id]
            # self.distances[child_id] = [tree_node_id, child.get_distance()]
            self._preorder_traversal(child, tree_node, root_id)

    def _apply_angle_corrections_fixed_correction_factor(self):
        levels = sorted([(k,v[1]) for k,v in self.levels.items() if k != 1000], key=lambda x: x[1])

        all_stresses = []
        # # Skip root
        correction_factors = [1, 1.5, 2, 2.5, 3, 5, 10, 100]
        for correction_factor in correction_factors:
            corrected_coordinates = self._calculate_angle_correction_coordinates(copy.deepcopy(self.coordinates), correction_factor, levels, self.tree.get_id())
            stress = self._calculate_stress_all_node_pairs(corrected_coordinates)
            all_stresses.append(stress)
        best_correction_factor = correction_factors[all_stresses.index(min(all_stresses, key=lambda x:abs(x)))]
        print(all_stresses, best_correction_factor)
        # print("Interlen leaf ordering ------------------------", leaf_ordering_internal)
        return self._calculate_angle_correction_coordinates(copy.deepcopy(self.coordinates), best_correction_factor, levels, self.tree.get_id())


    def _calculate_angle_correction_coordinates(self, coordinates, correction_factor, level_order, root):
        coordinates[root] = np.array((0, 0))
        for node, level in level_order:
            angle = self.tau[node] + self.omega[node] / correction_factor
            parent = self.levels[node][2]
            coordinates[node] = coordinates[parent] + self.distances[node][1] * np.array(
                (cos(angle), sin(angle)))
        return coordinates


    def _apply_angle_corrections_pivot_based(self):
        corrected_coordinates = copy.deepcopy(self.coordinates)
        leaf_ordering_internal = self.tree.post_order_internal()
        leaf_ordering_pivot = self.tree.pre_order()[0]
        root = self.tree.get_id()
        pivot_root_distance = self._get_pair_distance(leaf_ordering_pivot, root)
        # self.corrected_coordinates[root] = np.array((cos(pi / (pivot_root_distance)), sin(pi / (pivot_root_distance))))
        corrected_coordinates[root] = np.array((0,0))
        # Skip root
        for node in leaf_ordering_internal[:-1]:
            print("current node", node, leaf_ordering_pivot)
            dist = self._get_pair_distance(leaf_ordering_pivot, node)
            air_dist = RadialLayoutLeafCount._get_euclidian_distance(corrected_coordinates[leaf_ordering_pivot], corrected_coordinates[node])
            stress = dist / air_dist
            level = self.levels[node][1]
            if node != leaf_ordering_pivot:
                correction_factor = 2
            else:
                correction_factor = 2

            angle = self.tau[node] + self.omega[node] / correction_factor
            parent = self.levels[node][2]
            corrected_coordinates[node] = corrected_coordinates[parent] + self.distances[node][1] * np.array((cos(angle), sin(angle)))
        print("Interlan leaf ordering ------------------------", leaf_ordering_internal)
        return corrected_coordinates

    def _apply_angle_corrections_adjacent_node_based(self):
        leaf_ordering = self.tree.pre_order()
        corrected_coordinates = copy.deepcopy(self.coordinates)

        for index, node in enumerate(leaf_ordering[1:]):
            previous_node = leaf_ordering[index-1]
            dist = self._get_pair_distance(node, previous_node)
            correction_factors = np.arange(1, 10, 0.2)
            stresses = []
            for correction_factor in correction_factors:
                angle = self.tau[node] + self.omega[node] / correction_factor
                parent = self.levels[node][2]
                corrected_coordinates[node] = corrected_coordinates[parent] + self.distances[node][
                    1] * np.array((cos(angle), sin(angle)))
                air_dist = RadialLayoutLeafCount._get_euclidian_distance(corrected_coordinates[previous_node],
                                                                corrected_coordinates[node])
                stresses.append(dist / air_dist)
            minimum_stress_factor = correction_factors[stresses.index(min(stresses, key=lambda x:abs(x)))]
            angle = self.tau[node] + self.omega[node] / minimum_stress_factor
            parent = self.levels[node][2]
            corrected_coordinates[node] = corrected_coordinates[parent] + self.distances[node][
                1] * np.array(
                (cos(angle), sin(angle)))
        return corrected_coordinates

    def _get_pair_distance(self, v1 , v2):
        """
        Calculates branch distance between two nodes
        """
        if self.levels[v1][1] - 1 > self.levels[v2][1] - 1:
            v1,v2 = v2, v1
        lvl_diff = (self.levels[v2][1] - 1) - (self.levels[v1][1] - 1)
        travel_dis_1 = 0
        travel_dis_2 = 0
        while lvl_diff > 0:
            v2,dist = self.distances[v2]
            lvl_diff-=1
            travel_dis_2 += dist
        if v1 == v2:
            return travel_dis_1 + travel_dis_2
        while self.distances[v1][0] != self.distances[v2][0]:
            v1,dis1 = self.distances[v1]
            v2,dis2 = self.distances[v2]
            travel_dis_1 += dis1
            travel_dis_2 += dis2
        travel_dis_1 += self.distances[v1][1]
        travel_dis_2 += self.distances[v2][1]
        return travel_dis_1 + travel_dis_2

    @staticmethod
    def _get_euclidian_distance(x, y):
        return norm(x - y)

    def _calculate_stress_all_node_pairs(self, coordinates):
        internal_leaf_ordering = self.tree.pre_order_internal()

        all_stresses = []
        # can be done in a more optimal way
        for node in internal_leaf_ordering:
            for adj_node in internal_leaf_ordering:
                if node != adj_node:
                    branch_distance = self._get_pair_distance(node, adj_node)
                    air_distance = RadialLayoutLeafCount._get_euclidian_distance(coordinates[node], coordinates[adj_node])
                    stress = math.log2(air_distance / branch_distance)
                    if math.isnan(stress):
                        stress = 0
                    all_stresses.append(stress)
        return sum(all_stresses) / len(all_stresses)

    def _calculate_stress_all_leaf_node_pairs(self, coordinates):
        leaf_ordering = self.tree.pre_order()

        all_stresses = []
        # can be done in a more optimal way
        for node in leaf_ordering:
            for adj_node in leaf_ordering:
                if node != adj_node:
                    branch_distance = self._get_pair_distance(node, adj_node)
                    air_distance = RadialLayoutLeafCount._get_euclidian_distance(coordinates[node], coordinates[adj_node])
                    all_stresses.append(math.log2(air_distance / branch_distance))

        return sum(all_stresses) / len(all_stresses)


    @staticmethod
    def get_plotted_tree(tree, points, tree_node_mapping, figure):
        tree_data = []
        RadialLayoutLeafCount.plot_tree_bokeh(tree, points, figure, tree_data, root_id = tree.get_id())
        x_coordinates, y_coordinates, node_labels = list(zip(*tree_data))
        node_labels = [tree_node_mapping.get(node, node) for node in node_labels]
        source = ColumnDataSource(data=dict(x=x_coordinates,
                                            y=y_coordinates,
                                            labels=node_labels))
        labels = LabelSet(x='x', y='y', text='labels',
                          x_offset=0, y_offset=0, source=source, render_mode='canvas')
        figure.add_layout(labels)

    @staticmethod
    def plot_tree_bokeh(node, points, figure, tree_data, root_id = None):
        node_id = node.get_id()
        node_x_coordinate, node_y_coordinate = points[node_id]
        if root_id and root_id == node_id:
            tree_data.append((node_x_coordinate, node_y_coordinate, node_id))
        for child in node.get_children():
            child_id = child.get_id()
            child_x_coordinate, child_y_coordinate = points[child_id]
            tree_data.append((child_x_coordinate, child_y_coordinate, child_id))
            figure.line(x=[node_x_coordinate, child_x_coordinate], y=[node_y_coordinate, child_y_coordinate])
            RadialLayoutLeafCount.plot_tree_bokeh(child, points, figure, tree_data)


class RadialLayoutBranchLength(RadialLayoutLeafCount):

    def __init__(self, tree):
        super().__init__(tree)


    def _preorder_traversal(self, tree_node, parent, root_id):
        tree_node_id = tree_node.get_id()
        if tree_node_id != root_id:
            u = parent
            u_id = u.get_id()
            angle = self.tau[tree_node_id] + self.omega[tree_node_id] / 2
            self.coordinates[tree_node_id] = self.coordinates[u_id] + tree_node.get_distance() * np.array(
                (cos(angle), sin(angle)))
        eta = self.tau[tree_node_id]
        for child in tree_node.get_children():
            print(f"Tree node {tree_node_id} children {[childs.get_id() for childs in tree_node.get_children()]}")
            child_id = child.get_id()
            print(f"Child node {child_id}, child branch lengths {self.levels[child_id][3]}, parent {root_id}, parent lengths {self.levels[root_id][3]}")
            self.omega[child_id] = 2 * pi * self.levels[child_id][3] / self.levels[root_id][3]
            self.tau[child_id] = eta
            print("Omega", self.omega[child_id])
            eta += self.omega[child_id]
            self.distances[child_id] = [tree_node_id, child.get_distance()]
            self._preorder_traversal(child, tree_node, root_id)

    def _apply_angle_corrections_pivot_based(self):
        """
        Applies angle corrections to each adjacent members
        """
        corrected_coordinates = copy.deepcopy(self.coordinates)
        levels = sorted([(k,v[1]) for k,v in self.levels.items() if k != 1000], key=lambda x: x[1])

        # leaf_ordering_internal = self.tree.post_order_internal()
        leaf_ordering_pivot = self.tree.pre_order()[0]
        root = self.tree.get_id()
        print(levels)
        # pivot_root_distance = self._get_pair_distance(leaf_ordering_pivot, root)
        # # self.corrected_coordinates[root] = np.array((cos(pi / (pivot_root_distance)), sin(pi / (pivot_root_distance))))
        corrected_coordinates[root] = np.array((0, 0))
        # # Skip root
        for node,level in levels:
            dist = self._get_pair_distance(leaf_ordering_pivot, node)
            air_dist = RadialLayoutLeafCount._get_euclidian_distance(corrected_coordinates[leaf_ordering_pivot], corrected_coordinates[node])
            stress = dist / air_dist
            level = self.levels[node][1]

            if node != leaf_ordering_pivot:
                correction_factor = dist / level
            else:
                correction_factor = 2

            angle = self.tau[node] + self.omega[node] / correction_factor

            parent = self.levels[node][2]
            print(f"Node : {node}, pivot {leaf_ordering_pivot} Distance {dist}, corr fact {correction_factor}, Angle {angle}, Tau {self.tau[node]}, Omega {self.omega[node]},"
                  f" Parent coors bef {corrected_coordinates[parent]}, node cords bef {corrected_coordinates[node]}")
            corrected_coordinates[node] = corrected_coordinates[parent] + self.distances[node][1] * np.array((cos(angle), sin(angle)))
        print(self.levels)
        # print("Interlen leaf ordering ------------------------", leaf_ordering_internal)
        return corrected_coordinates













