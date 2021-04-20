import numpy as np
from numpy import linalg as LA
def _compute_node_distance_matrix(num_leaves = 1):
    """
    Constructs the default node distance matrix based on the number of leaves in a tree
    """
    upper = np.array([[i for i in range(up,0,-1)] + [j for j in range(0,num_leaves-up)] for up in range(num_leaves)])
    return upper

def _compute_p_matrix(ordering):
    n = len(ordering)
    return np.apply_along_axis(lambda x : (x - n/2)/ (n/2),0, ordering ).reshape(1,n)



if __name__ == "__main__":
    similarity_matrix = np.array([[0, 5, 9, 9, 8],
                       [5, 0, 10, 10, 9],
                       [9, 10, 0, 8, 7],
                       [9, 10, 8, 0, 3],
                       [8, 9, 7, 3, 0]])
    # print(similarity_matrix,similarity_matrix.shape)
    distance_matrix = _compute_node_distance_matrix(5)
    # print(distance_matrix)
    # print(distance_matrix,distance_matrix.shape)

    a = np.array([0,1,2,3,4])
    p = _compute_p_matrix(a)
    # print(p,p.shape, p.T.shape,p.T)
    subs = distance_matrix - similarity_matrix
    print(p)
    print(np.matmul(0*distance_matrix,np.ones(5).T))
    print(np.matmul(subs,np.ones(5).T))
    # print(subs)
    print(np.matmul(np.matmul(2*p,subs),p.T))
    w,v = LA.eig(subs)
    print(w,v)
    u = v[:,1]
    lam = w[1]

    # print(np.matmul(np.matmul(p,subs),p.T))

    # a.reshape(2,1)

