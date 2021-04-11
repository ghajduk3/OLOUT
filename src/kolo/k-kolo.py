import numpy as np
from scipy.cluster import hierarchy
import itertools
import itertools
import numpy as np
from scipy.cluster import hierarchy
from newick import Parser
from tree import TreeNode
from random import *
from visualization import get_points_radial,plot_tree
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("Qt5Agg")
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
        tree = self._parse_newick_tree()
        optimal_ordered_tree = self._get_optimal_ordered_tree(tree)
        return optimal_ordered_tree,optimal_ordered_tree.pre_order()

    def _get_optimal_ordered_tree(self, tree):
        """
            1. Produces optimal scores -- Matrix M
            2. Reorders tree leaves according to the optimal scores
        """
        self._produce_optimal_scores(tree,self.distances)
        return self._reorder_tree(tree,self.distances)

    def _produce_optimal_scores(self, v, D, fast=True):
        """
            Wrapper for recursive function. Produces new nodes according to k-ary ordering problem.
        """
        # Check if there are more then two children of
        v_children = v.get_children()
        print("----------- WRAPPER----------", v.id)
        if len(v_children) > 2:
            while len(v.children) >2:
            # for index,child in enumerate(v.get_children()):
                new_node = TreeNode(self.int_dummy_node,0)
                self.internal_dummy_nodes.append(self.int_dummy_node)
                self.int_dummy_node+=1
                new_node.add_node(v.children[0])
                new_node.add_node(v.children[1])
                print(v.id,v.children)
                v.children = v.children[2:]
                print(v.id, v.children)
                v.children.insert(0,new_node)
                print(v.id, v.children,v.children[0].id)
                res = self._optimal_scores(new_node,D,fast)
                print("----------- WRAPPER OPTIMAL ----------", v.id,v.get_children(),v.get_children()[0].id)
                if len(v.children) == 2:
                    self._optimal_scores(v,D,fast)
            return res

        else:
            return self._optimal_scores(v, D, fast)

    def _optimal_scores(self, v, D, fast=True):

        print(leaves(v), leaves(v.get_left()), leaves(v.get_right()))

        def score_func(left, right, u, m, w, k):
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
                            print("u,w", u, w, v.id,)
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
                print(child.id,v.pre_order_internal(),'------ DUMMY')
                v.children.remove(child)
                left_great_child,right_great_child = child.children
                v.children.insert(0,left_great_child)
                v.children.insert(1,right_great_child)
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

    tree_string = "((2:2.000000,(1:4.000000, 0:1.000000):1.000000):2.000000, (4:2.000000, 3:3.000000):1.000000,5:5.00000);"
    tree_string_1 = '(3:2.000000,4:1.000000,(2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000);'
    kolo_data = KOLO(tree_string,dis)
    # ordered_tree, ordered_leaves = kolo_data.optimal_leaf_ordering()
    # print(ordered_leaves)
    # raw_newick = Parser.parse_newick_tree(tree_string_1)
    # print(raw_newick.children)
    #
    # radial_points_raw = get_points_radial(raw_newick)
    fig,(ax1,ax2) = plt.subplots(1,2)
    # plot_tree(raw_newick,radial_points_raw,ax1)
    ordered_tree, ordered_leaves = kolo_data.optimal_leaf_ordering()
    print(ordered_leaves,ordered_tree.pre_order_internal())
    plot_tree(ordered_tree,get_points_radial(ordered_tree),ax2)

    plt.show()
    fig.show()

