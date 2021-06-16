import math
import numpy as np
from math import pi,cos,sin
from collections import deque
from numpy.linalg import norm


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

def LCA(ancestors_matrix, level_matrix, v1 , v2):
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

def reverse_level_order_traversal(tree):
    """
    Returns deque node,lvl
    """
    q = deque()
    q.append((tree,1,None))
    levels = {}
    while q:
        node,lvl,parent = q.popleft()
        if node is None:
            continue
        levels[node.get_id()] = (lvl,parent)
        for child in node.get_children():
            q.append((child,lvl+1,node.get_id()))
    return levels

def preorder_traverse_radial(node, parent, root_id, x, l, omega, tau,distances):
    node_id = node.get_id()
    if node.get_id() != root_id:
        u = parent
        u_id = u.get_id()
        angle = tau[node_id] + omega[node_id] / 2
        # print(angle,tau[node_id],omega[node_id],node.get_distance())
        x[node_id] = x[u_id] + node.get_distance() * np.array((cos(angle), sin(angle)))
        # print(angle, tau[node_id], omega[node_id], node.get_distance(),x[u_id],x[node_id])
    eta = tau[node_id]
    for child in node.get_children():
        child_id = child.get_id()
        omega[child_id] = 2 * pi * l[child_id] / l[root_id]
        tau[child_id] = eta
        eta += omega[child_id]
        distances[child_id] = [node_id,child.get_distance()]
        preorder_traverse_radial(child, node, root_id, x, l, omega, tau,distances)

def construct_distances(node,distances):
    for child in node.get_children():
        distances[child.get_id()] = [node.get_id(),child.get_distance()]
        construct_distances(child,distances)



def apply_corrections(tree,level_matrix,omega,tau,distances,coord_orig):
    """
    Applies angle corrections regarding to distance from the first node in ordering and a level
    """
    internal_leaf_ordering = tree.pre_order_internal()
    pivot_order = tree.pre_order()[0]
    x = {}
    root = tree.get_id()
    dist = LCA(distances, level_matrix, pivot_order, root)
    print("Root distace", np.array((cos(pi/(dist/2)), sin(pi/(dist/2)))))
    x[root] = np.array((cos(pi/(dist)), sin(pi/(dist))))
    # Skip root
    for node in internal_leaf_ordering[1:]:
            # Write correction factor and document it as soon as possible
            dist = LCA(distances,level_matrix,pivot_order,node)
            air_dist = _euclidian_distance(coord_orig[pivot_order],coord_orig[node])
            stress = dist/air_dist
            level = level_matrix[node][0]
            if node != pivot_order:
                correction_factor = dist/(level)
            else:
                correction_factor = 2

            angle = tau[node] + omega[node]/correction_factor
            parent = level_matrix[node][1]
            x[node] = x[parent] + distances[node][1] * np.array((cos(angle), sin(angle)))
            print("Angle corrections",node,angle,tau[node],omega[node],distances[node][1],correction_factor,dist,level,parent,x[parent],x[node],stress)
    return x

def _euclidian_distance(x,y):
    return norm(x-y)


def calculate_stress(tree,level_matrix,coordinates,distances):
    ordering = tree.pre_order()

    stresses = []
    local_stress = 0

    for index in range(len(ordering)-1):
        node_1, node_2 = ordering[index], ordering[index+1]
        branch_distance = LCA(distances,level_matrix,node_1,node_2)
        air_distance = _euclidian_distance(coordinates[node_1],coordinates[node_2])
        local_stress = branch_distance/air_distance
        print("Stress, node_1 : {} , node_2 : {} , air distance : {} , branch distance : {}, stress : {}".format(node_1,node_2,air_distance,branch_distance,local_stress))
        stresses.append(local_stress)
    print("-" * 50)

    return sum(stresses)/len(stresses)

def calculate_stress_pivot(tree,level_matrix,coordinates,distances):
    ordering = tree.pre_order()
    pivot = ordering[0]
    stresses = []
    local_stress = 0

    for index in range(1,len(ordering)):
        next_node = ordering[index]
        branch_distance = LCA(distances,level_matrix,pivot,next_node)
        air_distance = _euclidian_distance(coordinates[pivot],coordinates[next_node])
        local_stress = math.log2(air_distance/branch_distance)
        print("Stress, node_1 : {} , node_2 : {} , air distance : {} , branch distance : {}, stress : {}".format(pivot,next_node,air_distance,branch_distance,local_stress))
        stresses.append(local_stress)
    print("-" * 50)
    return sum(stresses)/len(stresses)



def get_points_radial(tree,correct=False):
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
    distances = {}
    postorder_traverse_radial(tree,l)
    root = tree.get_id()
    x[root] = np.array((0, 0))
    omega[root] = 2 * pi
    tau[root] = 0
    preorder_traverse_radial(tree, None, root, x, l, omega, tau,distances)
    reverse_level_order = reverse_level_order_traversal(tree)
    if correct:
        x_corrected = apply_corrections(tree,reverse_level_order,omega,tau,distances,x)
        stress = calculate_stress_pivot(tree,reverse_level_order,x,distances)
        stress_corrected = calculate_stress_pivot(tree,reverse_level_order,x_corrected,distances)
        return x_corrected
    return x

def plot_tree(node,points,plot):
    node_id = node.get_id()
    for child in node.get_children():
        child_id = child.get_id()
        plot.plot((points[node_id][0],points[child_id][0]), (points[node_id][1],points[child_id][1]),'k')
        plot.annotate(child_id,xy=(points[child_id][0]+0.05,points[child_id][1]+0.05))
        plot_tree(child,points,plot)