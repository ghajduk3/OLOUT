import numpy as np
from sklearn.decomposition import PCA
"""
PCA
Peform dimensionality reduction with PCA(1 component) on similarity matrix and infer leaf ordering
"""

def get_first_component_pca(similarity_matrix: np.ndarray):
    """
    Projects similarity matrix to 1D.
    """
    pca = PCA(n_components=1)
    return pca.fit_transform(similarity_matrix)


def get_leaf_ordering_pca(similarity_matrix: np.ndarray ):
    """
    Infers linear ordering from projected data.
    """
    first_component = get_first_component_pca(similarity_matrix)
    row,cols = first_component.shape

    return first_component.reshape(1,row)[0].argsort()[::-1]



if __name__ == "__main__":
    dis = np.array([[0, 5, 4, 7, 6, 8],
                    [5, 0, 7, 10, 9, 11],
                    [4, 7, 0, 7, 6, 8],
                    [7, 10, 7, 0, 5, 9],
                    [6, 9, 6, 5, 0, 8],
                    [8, 11, 8, 9, 8, 0]])
    print(get_leaf_ordering_pca(dis))


