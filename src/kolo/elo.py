import numpy as np
from numpy import linalg as LA
def _compute_node_distance_matrix(num_leaves = 1):
    """
    Constructs the default node distance matrix based on the number of leaves in a tree
    """
    upper = np.array([[i for i in range(up,0,-1)] + [j for j in range(0,num_leaves-up)] for up in range(num_leaves)])
    return upper

def _compute_distance_sim_matrix(ordering,similarities):
    final_matrix = []
    for i in range(len(ordering)):
        sub_list = np.zeros(len(ordering))
        sub_list[i] = sum(similarities[i])
        final_matrix.append(sub_list)
    return np.array(final_matrix)

def _compute_p_matrix(ordering):
    n = len(ordering)
    return np.apply_along_axis(lambda x : (x - n/2)/ (n/2),0, ordering ).reshape(1,n)

def _reweight_similarity_matrix(similarities,siblings):
    alpha = 1

    for i in range(len(similarities)):
        for j in range(len(similarities)):
            delta = 1 if siblings[i] == j else 0
            similarities[i,j] = similarities[i,j] * (1 + alpha*delta)
    return similarities

def _compute_leaf_ordering(distance_matrix,similarity_matrix):
    order_len = len(distance_matrix[0,:])
    final_matrix = np.identity(order_len) - np.matmul(LA.inv(distance_matrix),weigh_similarity_matrix)
    eig_values,eig_vectors = LA.eig(final_matrix)
    second_min_ind = np.argsort(eig_values)[1]
    second_min_vector = eig_vectors[:,second_min_ind]
    return np.argsort(second_min_vector)[::-1]

"""
    1. Make wrapper function to get an ordering from 
    2. Generate siblings dictionary from tree parser
     
"""

if __name__ == "__main__":
    similarity_matrix = np.array([[0, 5, 9, 9, 8],
                       [5, 0, 10, 10, 9],
                       [9, 10, 0, 8, 7],
                       [9, 10, 8, 0, 3],
                       [8, 9, 7, 3, 0]])
    siblings = {3: 4, 2: None, 1: 0, 4: 3, 0: 1}

    # Computes distance matrix
    weigh_similarity_matrix = _reweight_similarity_matrix(similarity_matrix,siblings)
    initial_ordering = np.array([0, 1, 2, 3, 4])
    distance_matrix = _compute_distance_sim_matrix(initial_ordering,weigh_similarity_matrix)
    ordering = _compute_ordering(distance_matrix,weigh_similarity_matrix)
    print(ordering)

    # # print(distance_matrix,distance_matrix.shape)
    # p = _compute_p_matrix(initial_ordering)
    # print(np.matmul(np.matmul(p, distance_matrix-similarity_matrix), p.T))
    # z = np.array([ -0.045795, -5.059e-4, -0.15515, -0.69869, 1])
    # print(np.matmul(np.matmul(z,distance_matrix),np.ones(5).T))
    # # print(p,p.shape, p.T.shape,p.T)
    # print(distance_matrix)
    #
    # print(final_matrix)
    # print(LA.eig(final_matrix))
    # print(np.matmul(np.matmul(z,distance_matrix),np.ones(5)))
    # u = v[:,1]
    # lam = w[1]

    # print(np.matmul(np.matmul(p,subs),p.T))

    # a.reshape(2,1)

