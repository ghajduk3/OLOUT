import numpy as np
from math import pi,cos,sin
from matplotlib import pyplot as plt
from collections import deque
def postorder_traverse_radial(node, l):
    node_id = node.get_id()
    if node.is_leaf():
        l[node_id] = 1
    else:
        l[node_id] = 0
        for w in node.get_children():
            w_id = w.get_id()
            postorder_traverse_radial(w, l)
            l[node_id] += l[w_id]


# def preorder_traverse_radial(tree, v, parent, root, x, l, omega, tau):
#     if v != root:
#         u = parent
#         angle = tau[v] + omega[v] / 2
#         x[v] = x[u] + get_distance(tree, u, v) * np.array((cos(angle), sin(angle)))
#     eta = tau[v]
#     for w in get_children(tree, v):
#         omega[w] = 2 * pi * l[w] / l[root]
#         tau[w] = eta
#         eta += omega[w]
#         preorder_traverse_radial(tree, w, v, root, x, l, omega, tau)

def preorder_traverse_radial(node, parent, root_id, x, l, omega, tau):
    node_id = node.get_id()
    print("Current node -",node_id)
    if node.get_id() != root_id:
        u = parent
        u_id = u.get_id()
        if node_id == 10000  :
            angle = tau[node_id] + omega[node_id] /10
        else:
            angle = tau[node_id] + omega[node_id] / 5
        print(angle,tau[node_id] + omega[node_id],omega[node_id])
        x[node_id] = x[u_id] + node.get_distance() * np.array((cos(angle), sin(angle)))
    eta = tau[node_id]
    print(eta)
    for child in node.get_children():
        child_id = child.get_id()
        omega[child_id] = 2 * pi * l[child_id] / l[root_id]
        tau[child_id] = eta
        eta += omega[child_id]
        preorder_traverse_radial(child, node, root_id, x, l, omega, tau)
# def bottom_up_traverse_radial(node,bottom_up):
#     for child in node.get_children():
#         bottom_up_traverse_radial(child,bottom_up)
#     bottom_up.append(node.get_id())
def reverse_level_order_traversal(tree):
    """
    Returns deque node,lvl
    """
    q = deque()
    q.append((tree,1))
    levels = {}
    while q:
        node,lvl = q.popleft()
        if node is None:
            continue
        levels[node.get_id()] = lvl
        for child in node.get_children():
            q.append((child,lvl+1))
    return levels
def apply_corrections():
    pass

def get_points_radial(tree):
    """See Algorithm 1: RADIAL-LAYOUT in:
    Bachmaier, Christian, Ulrik Brandes, and Barbara Schlieper.
    "Drawing phylogenetic trees." Algorithms and Computation (2005): 1110-1121.
    :param rooted_tree:
    :param root:
    :return:
    """
    l = {}
    x = {}
    omega = {}
    tau = {}
    print("-------------------------------- POCETAK RADIJALNE VIZUALIZACIJE-----------------------------")
    postorder_traverse_radial(tree,l)
    root = tree.get_id()
    x[root] = np.array((0, 0))
    omega[root] = 2 * pi
    tau[root] = 0
    bottom_up = []

    # print(l)
    preorder_traverse_radial(tree, None, root, x, l, omega, tau)
    reverse_level_order = reverse_level_order_traversal(tree)
    apply_corrections(tree,ordering,reverse_level_order,omega,tau)
    print(tau)
    print(omega)
    print(reverse_level_order_traversal(tree))
    return x

def plot_tree(node,points,plot):
    node_id = node.get_id()
    for child in node.get_children():
        child_id = child.get_id()
        plot.plot((points[node_id][0],points[child_id][0]), (points[node_id][1],points[child_id][1]),'k')
        plot.annotate(child_id,xy=(points[child_id][0]+0.05,points[child_id][1]+0.05))
        plot_tree(child,points,plot)