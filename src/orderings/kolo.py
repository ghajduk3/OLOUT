import math

from src.utils.newick import Parser
import itertools
from src.utils.tree import TreeNode
import copy
def leaves(t, t2=None):
    try:
        return t.pre_order()
    except AttributeError:
        if t2 is not None:
            return t2.pre_order()
        else:
            return []


def get_permutations(lst, siz):

    def validate(parts, siz):
        for p in parts:
            for i in range(siz - 1):
                if len(p) > i + 1:
                    if p[i] > p[i + 1]:
                        return False
        return True
    outs = []
    print("Inside permutations")
    for c in list(itertools.permutations(lst)):
        parts = [c[:siz], c[siz:]]
        if validate(parts, siz):
            if list(reversed(parts)) not in outs:
                outs.append(parts)
    return outs

class KOLO:

    def __init__(self, newick_tree, distance_matrix, mapping):
        self.newick_tree = copy.deepcopy(newick_tree)
        self.distance_matrix = distance_matrix
        self._mapping = mapping
        self.M = {}
        self.temp = {}
        self.int_dummy_node = 2000
        self.internal_dummy_nodes = list()

    # @property
    # def newick_tree(self):
    #     return self._newick_tree
    #
    # @newick_tree.setter
    # def newick_tree(self, newick_tree_string):
    #     tree, mapping = Parser.parse_newick_tree(newick_tree_string)
    #     self._newick_tree = tree
    #     self._mapping = mapping

    def get_optimal_leaf_ordering(self):
        self.__get_optimal_ordered_tree(self.newick_tree, self.distance_matrix)
        ordered_tree = self.__tree_reorder(self.newick_tree)
        optimal_ordering = [self._mapping[node] for node in ordered_tree.pre_order()]
        return ordered_tree, optimal_ordering

    def __get_optimal_ordered_tree(self,v, distance_matrix):
        print(f"----------- Permuration wrapper, root node is {v.get_id()} with children {[child.get_id() for child in v.get_children()]} ------------")
        v_children = v.get_children()
        children_number = len(v_children)

        if children_number >= 3:
            print(f"There are three children for node {v.get_id()}")
            possible_permutations = get_permutations(list(range(children_number)), math.ceil(children_number/2))
            # Calculate the score for best permutation, left and right nodes
            best_permutation = (10e10, 0, 0)
            print('Possible permutations ', possible_permutations)

            dummy_node_left = TreeNode(self.int_dummy_node,0)
            self.internal_dummy_nodes.append(self.int_dummy_node)
            self.int_dummy_node += 1

            if children_number > 3:
                dummy_node_right = TreeNode(self.int_dummy_node, 0)
                self.internal_dummy_nodes.append(self.int_dummy_node)

                self.int_dummy_node += 1

            v_copy = copy.deepcopy(v)

            for left_indexes, right_indexes in possible_permutations:
                print(f"Current permutation is with left part indexes {left_indexes}, right part indexes {right_indexes}")
                v_variable = copy.deepcopy(v_copy)
                left_nodes = [v_variable.get_children()[index] for index in [*left_indexes]]
                right_nodes = [v_variable.get_children()[index] for index in [*right_indexes]]
                print(f"Nodes within the current permutation are left nodes {[child.get_id() for child in left_nodes]}, right nodes {[child.get_id() for child in right_nodes]}")

                dummy_node_left.children = left_nodes
                v_variable.children = [dummy_node_left]
                if children_number > 3:
                    dummy_node_right.children = right_nodes
                    v_variable.children.append(dummy_node_right)
                else:
                    v_variable.children.insert(1,right_nodes[0])

                print(f"After permutation insertion v with id {v_variable.get_id()} has children {[child.get_id() for child in v_variable.get_children()]}")
                self.__optimal_ordering(v_variable, distance_matrix)

                best_permutation = self.__get_best_permutation(v_variable, left_nodes, right_nodes, best_permutation)

            score,left,right = best_permutation
            print(f"Best permutation is with score {score}, with left nodes {[child.get_id() for child in left]} and with right nodes {[child.get_id() for child in right]}, {leaves(right[0])}")
            dummy_node_left.children = left

            if children_number > 3:
                dummy_node_right.children = right
                v.children = [dummy_node_right]
            else:
                v.children = [right[0]]

            v.children.insert(0,dummy_node_left)
            print(f"After choosing the best permutation v with id {v.get_id()} has children {[child.get_id() for child in v.get_children()]} and leaves {v.pre_order()}")

        else:
            print(f"with children {[child.get_id() for child in v.get_children()]}")
            return self.__optimal_ordering(v, distance_matrix)

    def __optimal_ordering(self, v, distance_matrix):

        # Base case : if v is leaf M[v,v,v] = 0
        if v.is_leaf():
            v_id = v.get_id()
            self.M[v_id, v_id, v_id] = 0
            return 0
        else:
            left_node = v.get_left()
            right_node = v.get_right()
            L = left_node.pre_order()
            R = right_node.pre_order()
            print(f"Node id {v.get_id()}")

            self.__get_optimal_ordered_tree(left_node,distance_matrix)
            self.__get_optimal_ordered_tree(right_node, distance_matrix)
            for i in L:
                for j in R:
                    self.temp[i,j] = min(self.M.get((left_node.get_id(),i,h), 10e10) + self.distance_matrix[h,j] for h in L)
                    self.M[v.get_id(),i,j] = self.M[v.get_id(),j,i] = min(self.temp[i,j] + self.M.get((right_node.get_id(),l,j),10e10) for l in R)

    def __tree_reorder(self, v):
        L = leaves(v.get_left())
        R = leaves(v.get_right())
        if len(L) and len(R):
            def getkey(z):  ##added, this is to replace a lambda function
                u, w = z
                return self.M.get((v.id, u, w),10e10)
            if len(L) and len(R):
                u, w = min(itertools.product(L, R), key=getkey)  ##updated function
            if w in leaves(v.get_right().get_left()):
                v.children[1].children[1], v.children[1].children[0] = v.get_right().get_left(), v.get_right().get_right()
            if u in leaves(v.get_left().get_right()):
                v.children[0].children[0], v.children[0].children[1] = v.get_left().get_right(), v.get_left().get_left()
            v.children[0] = self.__tree_reorder(v.get_left())
            v.children[1] = self.__tree_reorder(v.get_right())
            self.__remove_internal_dummy(v)
        return v

    def __remove_internal_dummy(self, v):
        for child in v.children:
            if child.get_id() in self.internal_dummy_nodes:
                v.children.remove(child)
                v.children.extend(child.get_children())

    def __get_best_permutation(self, v, left_nodes, right_nodes, current_best_permut):
        L = leaves(v.get_left())
        R = leaves(v.get_right())
        if len(L) and len(R):
            def getkey(z):  ##added, this is to replace a lambda function
                u, w = z
                return self.M.get((v.get_id(), u, w),10e10)

            if len(L) and len(R):
                print(list(itertools.product(L, R)))
                u, w = min(itertools.product(L, R), key=getkey)  ##updated function
            if self.M[v.get_id(), u, w] <= current_best_permut[0]:
                print(f"Choice for best permutation for id {v.get_id()} with u : {u}, w : {w}, left nodes {[child.get_id() for child in left_nodes]}, right modes {[child.get_id() for child in right_nodes]}, {L}, {R}")
                return (self.M[v.id, u, w], left_nodes, right_nodes)
            else:
                return current_best_permut

