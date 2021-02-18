import pandas as pd
import numpy as np
from scipy.spatial.distance import squareform, pdist
from scipy.cluster import hierarchy
from scipy.spatial import distance
from scipy.cluster.hierarchy import linkage
import itertools
import matplotlib.pyplot as plt
import seaborn



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


class OLO(object):


    def __init__(self, linkage_matrix, distance_matrix):
        self.data = linkage_matrix
        self.distances = distance_matrix
    def optimal_ordering(self):
        self.M = {}
        tree = hierarchy.to_tree(self.data)
        tree = self.order_tree(tree, self.distances)
        order = leaves(tree)
        del self.M
        return tree,order

    def optimal_scores(self, v, D, fast=True):

        print(leaves(v),leaves(v.left),leaves(v.right))

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
            L = leaves(v.left)
            R = leaves(v.right)
            LL = leaves(v.left.left, v.left)
            LR = leaves(v.left.right, v.left)
            RL = leaves(v.right.left, v.right)
            RR = leaves(v.right.right, v.right)
            for l in L:
                for r in R:
                    print(l,r,v.left.id,v.right.id)
                    self.M[v.left.id, l, r] = self.optimal_scores(v.left, D, fast=False)
                    self.M[v.right.id, l, r] = self.optimal_scores(v.right, D, fast=False)
                    for u in L:
                        for w in R:
                            print("u,w",u,w,v.id)
                            if fast:

                                m_order = sorted(other(u, LL, LR), key=lambda m: Mfunc(v.left, u, m))
                                k_order = sorted(other(w, RL, RR), key=lambda k: Mfunc(v.right, w, k))

                                C = min([D[m, k] for m in other(u, LL, LR) for k in other(w, RL, RR)])
                                print('orders', m_order, k_order,C)
                                Cmin = 1e10
                                for m in m_order:
                                    if self.M[v.left.id, u, m] + self.M[v.right.id, w, k_order[0]] + C >= Cmin:
                                        break
                                    for k in k_order:
                                        if self.M[v.left.id, u, m] + self.M[v.right.id, w, k] + C >= Cmin:
                                            break
                                        C = score_func(v.left, v.right, u, m, w, k)
                                        if C < Cmin:
                                            Cmin = C
                                self.M[v.id, u, w] = self.M[v.id, w, u] = Cmin
                                print("Result true", self.M[v.id, u, w], v.id, u, w)
                            else:
                                self.M[v.id, u, w] = self.M[v.id, w, u] = \
                                    min([score_func(v.left, v.right, u, m, w, k) \
                                         for m in other(u, LL, LR) \
                                         for k in other(w, RL, RR)])
                                print("Result false",self.M[v.id, u, w] ,v.id,u,w)
                    return self.M[v.id, l, r]

    def order_tree(self, v, D, fM=None, fast=True):
        """ Returns an optimally ordered tree """
        # Generate scores the first pass
        if fM is None:
            fM = 1
            self.optimal_scores(v, D, fast=fast)


        L = leaves(v.left)
        R = leaves(v.right)

        vl = v.left
        vr = v.right

        # if len(L) and len(R):
        #     u,w = min(itertools.product(L,R),key=lambda z:self.M[v.id,z[0],z[1]])


        if len(L) and len(R):
            def getkey(z):  ##added, this is to replace a lambda function
                u, w = z
                return self.M[v.id, u, w]

            if len(L) and len(R):
                print(list(itertools.product(L, R)))
                u, w = min(itertools.product(L, R), key=getkey)  ##updated function
            if w in leaves(v.right.left):
                v.right.right, v.right.left = v.right.left, v.right.right
            if u in leaves(v.left.right):
                v.left.left, v.left.right = v.left.right, v.left.left
            v.left = self.order_tree(v.left, D, fM)
            v.right = self.order_tree(v.right, D, fM)

        return v
if __name__ == "__main__":

    link = np.array([[0.0, 1.0, 50.0, 2.0], [3.0, 4.0, 40.0, 2.0], [6.0, 2.0, 100.0, 3.0], [8.0, 7.0, 150.0, 5.0],
                     [9.0, 5.0, 150.0, 6.0]])
    dis = np.array([[0, 5, 4, 7, 6, 8],
                    [5, 0, 7, 10, 9, 11],
                    [4, 7, 0, 7, 6, 8],
                    [7, 10, 7, 0, 5, 9],
                    [6, 9, 6, 5, 0, 8],
                    [8, 11, 8, 9, 8, 0]])
    olo_data = OLO(link, dis)
    tre, order = olo_data.optimal_ordering()


