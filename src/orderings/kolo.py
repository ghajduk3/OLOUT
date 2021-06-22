import copy

import numpy as np
from scipy.cluster import hierarchy
import itertools
import itertools
import numpy as np
from scipy.cluster import hierarchy
from src.utils.newick import Parser
from src.utils.tree import TreeNode
from random import *
# from visualization import get_points_radial,plot_tree
# import matplotlib
from itertools import permutations
from matplotlib import pyplot as plt
# matplotlib.use("Qt5Agg")
def leaves(t, t2=None):
    try:
        return t.pre_order()
    except AttributeError:
        if t2 is not None:
            return t2.pre_order()
        else:
            return []


def other(x, V, W):
    # For an element x, returns the set that x isn't in
    if x in V:
        return W
    else:
        return V


def get_leaves(t, t2=None):
    try:
        return t.pre_order()
    except AttributeError:
        if t2 is not None:
            return t2.pre_order()
        else:
            return []


class KOLO(object):

    def __init__(self, newick_tree, distance_matrix):
        self.newick_tree = newick_tree
        self.distances = distance_matrix
        self.M = dict()
        self.int_dummy_node = 2000
        self.internal_dummy_nodes = list()

    def optimal_leaf_ordering(self):
        tree, mapping  = self._parse_newick_tree()
        print("mappinb", mapping)
        optimal_ordered_tree = self._get_optimal_ordered_tree(tree)
        optimal_ordering = [mapping[node] for node in optimal_ordered_tree.pre_order()]
        return optimal_ordered_tree, optimal_ordering

    def _get_optimal_ordered_tree(self, tree):
        """
            1. Produces optimal scores -- Matrix M
            2. Reorders tree leaves according to the optimal scores
        """
        self._produce_optimal_scores(tree,self.distances)
        return self._reorder_tree(tree,self.distances)



    def _get_permutations(self, lst, siz):

        def validate(parts, siz):
            for p in parts:
                for i in range(siz - 1):
                    if len(p) > i + 1:
                        if p[i] > p[i + 1]:
                            return False
            return True

        outs = []
        for c in list(permutations(lst)):
            parts = [c[:siz], c[siz:]]
            if validate(parts, siz):
                if list(reversed(parts)) not in outs:
                    outs.append(parts)
        return outs

    def _produce_optimal_scores(self, v, D, fast=True):
        print("--------------- PRODUCE OPTIMAL SCORES----------------" ,v.id)
        """
            Wrapper for recursive function. Produces new nodes according to k-ary ordering problem.
        """
        # Check if there are more then two children of
        v_children = v.get_children()
        num_children = len(v_children)

        #### Partition 1.case - 3 children
        if num_children > 2:
            best_permut = (100000000,0,0)
            if num_children > 3:
                dummy_node_right = TreeNode(self.int_dummy_node, 0)
                self.internal_dummy_nodes.append(self.int_dummy_node)
                self.int_dummy_node += 1
            dummy_node = TreeNode(self.int_dummy_node, 0)
            self.internal_dummy_nodes.append(self.int_dummy_node)
            self.int_dummy_node+=1
            node_permut = self._get_permutations(list(range(num_children)),2)
            v_cop = copy.deepcopy(v)
            for permut in node_permut:
                v1 = copy.deepcopy(v_cop)
                left_part, right_part = permut
                left_indexes = [*left_part]
                right_indexes = [*right_part]
                left_nodes = [v1.children[ind] for ind in left_indexes]
                dummy_node.children = left_nodes
                if len(right_indexes) == 1:
                    right_node = v1.children[right_indexes[0]]
                    v1.children = [right_node]
                else:
                    right_nodes = [v1.children[ind] for ind in right_indexes]
                    dummy_node_right.children = right_nodes
                    v1.children.insert(0,dummy_node_right)
                v1.children.insert(0,dummy_node)

                print("-------------------------PERMUTIACIJA -------------------")
                print([child.id for child in v1.children])
                print(left_indexes, right_indexes,left_part,*right_part, right_node.id)

                print("Node childs",[child.id for child in v1.children])
                self._optimal_scores(v1, D, fast)

                L = leaves(v1.get_left())
                R = leaves(v1.get_right())
                if len(L) and len(R):
                    def getkey(z):  ##added, this is to replace a lambda function
                        u, w = z
                        return self.M[v1.id, u, w]

                    if len(L) and len(R):
                        print(list(itertools.product(L, R)))
                        u, w = min(itertools.product(L, R), key=getkey)  ##updated function
                    print("permut scores",v1.id, u, w, L, R, self.M[v1.id,u,w])
                    if self.M[v1.id,u,w] <= best_permut[0]:
                        best_permut = (self.M[v1.id,u,w],left_nodes,right_node)
                print("------------------ KONEC PERMUTACIJE----------------------------")

            score,left,right = best_permut
            dummy_node.children = left
            v.children = [right]
            v.children.insert(0,dummy_node)
            print(v.id, [child.id for child in v.children])
            print("CHANGED V ---------------------",right.id,[node.id for node in best_permut[1]], best_permut)
        else:
            return self._optimal_scores(v, D, fast)

    def _optimal_scores(self, v, D, fast=True):

        print(leaves(v), leaves(v.get_left()), leaves(v.get_right()))

        def score_func(left, right, u, m, w, k):
            print("SCORE FUNC ------------ U,M,W,K",u, m,w,k)
            return Mfunc(left, u, m) + Mfunc(right, w, k) + D[m, k]

        def Mfunc(v, a, b):
            if a == b:
                self.M[v.id, a, b] = 0
            return self.M[v.id, a, b]

        if v.is_leaf():
            n = v.get_id()
            self.M[v.id, n, n] = 0
            return 0
        else:
            print("Leaf id",v.id)
            print([child.id for child in v.get_children()])
            # print(v.get_right().children)
            L = leaves(v.get_left())
            R = leaves(v.get_right())
            LL = leaves(v.get_left().get_left(), v.get_left())
            LR = leaves(v.get_left().get_right(), v.get_left())
            RL = leaves(v.get_right().get_left(), v.get_right())
            RR = leaves(v.get_right().get_right(), v.get_right())
            for l in L:
                for r in R:
                    print("------- LEFT, RIGHT",l, r, v.get_left().id, v.get_right().id)
                    self.M[v.get_left().id, l, r] = self._produce_optimal_scores(v.get_left(), D, fast=False)
                    self.M[v.get_right().id, l, r] = self._produce_optimal_scores(v.get_right(), D, fast=False)
                    for u in L:
                        for w in R:
                            print("u,w", u, w, v.id)
                            if fast:
                                m_order = sorted(other(u, LL, LR), key=lambda m: Mfunc(v.get_left(), u, m))
                                k_order = sorted(other(w, RL, RR), key=lambda k: Mfunc(v.get_right(), w, k))
                                print(m_order, k_order)
                                C = min([D[m, k] for m in other(u, LL, LR) for k in other(w, RL, RR)])
                                print('orders', m_order, k_order, C)
                                Cmin = 1e10
                                for m in m_order:
                                    if self.M[v.get_left().id, u, m] + self.M[v.get_right().id, w, k_order[0]] + C >= Cmin:
                                        break
                                    for k in k_order:
                                        if self.M[v.get_left().id, u, m] + self.M[v.get_right().id, w, k] + C >= Cmin:
                                            break
                                        C = score_func(v.get_left(), v.get_right(), u, m, w, k)
                                        if C < Cmin:
                                            Cmin = C
                                self.M[v.id, u, w] = self.M[v.id, w, u] = Cmin
                                print("Result true", self.M[v.id, u, w], v.id, u, w)
                            else:
                                self.M[v.id, u, w] = self.M[v.id, w, u] = \
                                    min([score_func(v.get_left(), v.get_right(), u, m, w, k) \
                                         for m in other(u, LL, LR) \
                                         for k in other(w, RL, RR)])
                                print("Score func", [score_func(v.get_left(), v.get_right(), u, m, w, k) \
                                                     for m in other(u, LL, LR) \
                                                     for k in other(w, RL, RR)])
                                print("Result false", self.M[v.id, u, w], v.id, u, w)
                    print(self.M)
            return self.M[v.id, l, r]

    def _reorder_tree(self,v,D):
        
        print([child.id for child in v.get_children()])
        L = leaves(v.get_left())
        R = leaves(v.get_right())

        vl = v.get_left()
        vr = v.get_right()
        if len(L) and len(R):
            def getkey(z):  ##added, this is to replace a lambda function
                u, w = z
                return self.M[v.id, u, w]
            if len(L) and len(R):
                print(list(itertools.product(L, R)))
                u, w = min(itertools.product(L, R), key=getkey)  ##updated function
            print(v.id,u,w,L,R)
            if w in leaves(v.get_right().get_left()):
                v.children[1].children[1], v.children[1].children[0] = v.get_right().get_left(), v.get_right().get_right()
            if u in leaves(v.get_left().get_right()):
                v.children[0].children[0], v.children[0].children[1] = v.get_left().get_right(), v.get_left().get_left()
            v.children[0] = self._reorder_tree(v.get_left(), D)
            v.children[1] = self._reorder_tree(v.get_right(), D)
            print('--------------------',v.id,v.pre_order_internal())
            self._remove_internal_dummy(v)
        return v

    def _remove_internal_dummy(self,v,):
        for index,child in enumerate(v.children):
            if child.id in self.internal_dummy_nodes:
                print(child.id,v.pre_order_internal(),[ch.id for ch in child.children],'------ DUMMY')
                v.children.remove(child)
                left_great_child,right_great_child = child.children

                v.children.append(left_great_child)
                v.children.append(right_great_child)
                print(child,left_great_child.id,right_great_child.id,v.children)

    def _parse_newick_tree(self):
        return Parser.parse_newick_tree(self.newick_tree)





if __name__ == "__main__":
    dis = np.array([[0, 5, 4, 7, 6, 8],
                    [5, 0, 7, 10, 9, 11],
                    [4, 7, 0, 7, 6, 8],
                    [7, 10, 7, 0, 5, 9],
                    [6, 9, 6, 5, 0, 8],
                    [8, 11, 8, 9, 8, 0]])
    dis1 = np.array([[0, 5, 9, 9, 8],
                       [5, 0, 10, 10, 9],
                       [9, 10, 0, 8, 7],
                       [9, 10, 8, 0, 3],
                       [8, 9, 7, 3, 0]])

    tree_string = "(5:5.00000,(2:2.000000,(1:4.000000, 0:1.000000):1.000000):2.000000,(4:2.000000, 3:3.000000):1.000000);"
    tree_string_1 = '(4:1.000000,(2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000,3:2.000000);'
    kolo_data = KOLO(tree_string_1,dis1)
    ordered_tree, ordered_leaves = kolo_data.optimal_leaf_ordering()
    print(ordered_leaves)
    # raw_newick = Parser.parse_newick_tree(tree_string_1)
    # print(raw_newick.children)
    #
    # radial_points_raw = get_points_radial(raw_newick)
    # fig,(ax1,ax2) = plt.subplots(1,2)
    # # plot_tree(raw_newick,radial_points_raw,ax1)
    # ordered_tree, ordered_leaves = kolo_data.optimal_leaf_ordering()
    # print(ordered_leaves,ordered_tree.pre_order_internal())
    # plot_tree(ordered_tree,get_points_radial(ordered_tree),ax2)
    #
    # plt.show()
    # fig.show()
    #
