import numpy as np
import math
from math import pi, cos, sin
from numpy.linalg import norm


class RadialLayout:

    def __init__(self, tree):
        self.tree = tree
        self.levels = {}
        self.coordinates = {}
        self.omega = {}
        self.tau = {}
        self.distances = {}

    def get_points_radial(self, apply_corrections = False):
        """See Algorithm 1: RADIAL-LAYOUT in:
        Bachmaier, Christian, Ulrik Brandes, and Barbara Schlieper.
        "Drawing phylogenetic trees." Algorithms and Computation (2005): 1110-1121.
        :param rooted_tree:
        :param root:
        :return:
        """
        self.postorder_traverse_radial(self.tree, None, 1)
        root = self.tree.get_id()
        self.coordinates[root] = np.array((0, 0))
        self.omega[root] = 2 * pi
        self.tau[root] = 0
        self.preorder_traverse_radial(self.tree, None, root)
        levels = self.__get_node_levels(self.tree,None, 1,{})

        if apply_corrections:
            x = self.apply_angle_corrections(levels)
            stress = self.calculate_stress_pivot(self.tree,levels,x, self.distances)
            return x, stress

        stress = self.calculate_stress_pivot(self.tree, levels, self.coordinates, self.distances)
        return self.coordinates, stress


    def postorder_traverse_radial(self, tree_node, parent_id, level):
        """
        Traverses the tree recursively in a postorder manner, calculates the number of leaves in each node's subtree and calculates each node's level.
        """

        node_id = tree_node.get_id()
        self.levels[node_id] = (0,level, parent_id)
        if tree_node.is_leaf():
            self.levels[node_id][0] = 1
        else:
            for child in tree_node.get_children():
                child_id = child.get_id()
                self.postorder_traverse_radial(child, node_id, level+1)
                self.levels[node_id][0] += self.levels[child_id][0]

    def preorder_traverse_radial(self, tree_node, parent, root_id):
        tree_node_id = tree_node.get_id()
        if tree_node_id != root_id:
            u = parent
            u_id = u.get_id()
            angle = self.tau[tree_node_id] + self.omega[tree_node_id] / 2
            # print(angle,tau[node_id],omega[node_id],node.get_distance())
            self.coordinates[tree_node_id] = self.coordinates[u_id] + tree_node.get_distance() * np.array((cos(angle), sin(angle)))
            # print(angle, tau[node_id], omega[node_id], node.get_distance(),x[u_id],x[node_id])
        eta = self.tau[tree_node_id]
        for child in tree_node.get_children():
            child_id = child.get_id()
            self.omega[child_id] = 2 * pi * self.levels[child_id][0] / self.levels[root_id][0]
            self.tau[child_id] = eta
            eta += self.omega[child_id]
            self.distances[child_id] = [tree_node_id, child.get_distance()]
            self.preorder_traverse_radial(child, tree_node, root_id)

    def apply_angle_corrections(self, level_matrix):
        """
        Applies angle corrections regarding to distance from the first node in ordering and a level
        """
        leaf_ordering_internal = self.tree.pre_order_internal()
        leaf_ordering_pivot = self.tree.pre_order()[0]
        x = {}
        root = self.tree.get_id()
        dist = self.__get_pair_distance(self.distances, level_matrix, leaf_ordering_pivot, root)
        print("Root distace", np.array((cos(pi / (dist / 2)), sin(pi / (dist / 2)))))
        x[root] = np.array((cos(pi / (dist)), sin(pi / (dist))))
        # Skip root
        for node in leaf_ordering_internal[1:]:
            # Write correction factor and document it as soon as possible
            dist = self.__get_pair_distance(self.distances, level_matrix, leaf_ordering_pivot, node)
            air_dist = self.__get_euclidian_distance(self.x[leaf_ordering_pivot], self.x[node])
            stress = dist / air_dist
            level = level_matrix[node][0]
            if node != leaf_ordering_pivot:
                correction_factor = dist / (level)
            else:
                correction_factor = 2

            angle = self.tau[node] + self.omega[node] / correction_factor
            parent = level_matrix[node][1]
            x[node] = x[parent] + self.distances[node][1] * np.array((cos(angle), sin(angle)))
            print("Angle corrections", node, angle, self.tau[node], self.omega[node], self.distances[node][1], correction_factor, dist,
                  level, parent, x[parent], x[node], stress)
        return x

    def calculate_stress_pivot(self, tree, level_matrix, coordinates, distances):
        print(level_matrix, distances)
        ordering = tree.pre_order()
        pivot = ordering[0]
        stresses = []
        local_stress = 0

        for index in range(1, len(ordering)):
            next_node = ordering[index]
            branch_distance = self.__get_pair_distance(distances, level_matrix, pivot, next_node)
            air_distance = self.__get_euclidian_distance(coordinates[pivot], coordinates[next_node])
            local_stress = math.log2(air_distance / branch_distance)
            print("Stress, node_1 : {} , node_2 : {} , air distance : {} , branch distance : {}, stress : {}".format(
                pivot, next_node, air_distance, branch_distance, local_stress))
            stresses.append(local_stress)
        print("-" * 50)
        return sum(stresses) / len(stresses)

    def __get_node_levels(self, node,parent, level, levels):
        if node:
            levels[node.get_id()] = (level, parent)
        for child in node.get_children():
            self.__get_node_levels(child, node.get_id(), level+1, levels)
        return levels

    def __get_euclidian_distance(self, x, y):
        return norm(x - y)

    def __get_pair_distance(self,ancestors_matrix, level_matrix, v1 , v2):
        """
        Calculates branch distance between two nodes
        """
        if level_matrix[v1][0] - 1 > level_matrix[v2][0] - 1:
            v1,v2 = v2, v1
        lvl_diff = (level_matrix[v2][0] - 1) - (level_matrix[v1][0] - 1)
        travel_dis_1 = 0
        travel_dis_2 = 0
        while lvl_diff > 0:
            v2,dist = ancestors_matrix[v2]
            lvl_diff-=1
            travel_dis_2 += dist
        if v1 == v2:
            return travel_dis_1 + travel_dis_2
        while ancestors_matrix[v1][0] != ancestors_matrix[v2][0]:
            v1,dis1 = ancestors_matrix[v1]
            v2,dis2 = ancestors_matrix[v2]
            travel_dis_1+=dis1
            travel_dis_2+=dis2
        travel_dis_1 += ancestors_matrix[v1][1]
        travel_dis_2 += ancestors_matrix[v2][1]
        return travel_dis_1 + travel_dis_2

    @staticmethod
    def plot_tree(node, points, plot):
        node_id = node.get_id()
        for child in node.get_children():
            child_id = child.get_id()
            plot.plot((points[node_id][0], points[child_id][0]), (points[node_id][1], points[child_id][1]), 'k')
            plot.annotate(child_id, xy=(points[child_id][0] + 0.05, points[child_id][1] + 0.05))
            RadialLayout.plot_tree(child, points, plot)
    @staticmethod
    def construct_distances(node, distances):
        for child in node.get_children():
            distances[child.get_id()] = [node.get_id(), child.get_distance()]
            RadialLayout.construct_distances(child, distances)