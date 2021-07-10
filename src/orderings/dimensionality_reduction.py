import numpy as np
from abc import ABCMeta,abstractmethod
from sklearn.decomposition import PCA
from sklearn.manifold import MDS,TSNE
from .tsne import get_tsne_embedding

"""
PCA
Peform dimensionality reduction with PCA(1 component) on similarity matrix and infer leaf ordering
"""
class Dro(metaclass=ABCMeta):
    def __init__(self, similarity_matrix: np.ndarray):
        self.similarity_matrix = similarity_matrix

    @abstractmethod
    def _get_first_component(self):
        pass

    @abstractmethod
    def get_leaf_ordering(self):
        pass

class DroPca(Dro):
    def __init__(self, similarity_matrix : np.ndarray):
        super().__init__(similarity_matrix)

    def _get_first_component(self):
        pca = PCA(n_components=1)
        return pca.fit_transform(self.similarity_matrix)

    def get_leaf_ordering(self):
        first_component = self._get_first_component()
        row, cols = first_component.shape
        return first_component.reshape(1, row)[0].argsort()[::-1]

class DroMDS(Dro):
    def __init__(self, similarity_matrix : np.ndarray):
        super().__init__(similarity_matrix)

    def _get_first_component(self):
        mds = MDS(n_components=1)
        return mds.fit_transform(self.similarity_matrix)

    def get_leaf_ordering(self):
        first_component = self._get_first_component()
        row, cols = first_component.shape
        return first_component.reshape(1, row)[0].argsort()[::-1]

class DroTSNE(Dro):
    def __init__(self, similarity_matrix : np.ndarray):
        super().__init__(similarity_matrix)

    def _get_first_component(self):
        tsne = TSNE(n_components=2)
        # two_components = tsne.fit_transform(self.similarity_matrix)
        two_components = get_tsne_embedding(self.similarity_matrix)
        pca = PCA(n_components=1)
        return pca.fit_transform(two_components)
    def get_leaf_ordering(self):
        first_component = self._get_first_component()
        row, cols = first_component.shape
        return first_component.reshape(1, row)[0].argsort()[::-1]



#
# if __name__ == "__main__":
#     dis = np.array([[0, 5, 4, 7, 6, 8],
#                     [5, 0, 7, 10, 9, 11],
#                     [4, 7, 0, 7, 6, 8],
#                     [7, 10, 7, 0, 5, 9],
#                     [6, 9, 6, 5, 0, 8],
#                     [8, 11, 8, 9, 8, 0]])
#
#     reweighted_similarities = np.array([[0, 5, 8, 14, 12, 16],
#                     [5, 0, 14, 20, 18, 22],
#                     [8, 14, 0, 14, 12, 16],
#                     [14, 20, 14, 0, 5, 18],
#                     [12, 18, 12, 5, 0, 16],
#                     [16, 22, 16, 18, 16, 0]])
#
#     pca = DroPca(reweighted_similarities)
#     ordering_pca = pca.get_leaf_ordering()
#     print(ordering_pca)
#     mds = DroMDS(reweighted_similarities)
#     ordering_mds = mds.get_leaf_ordering()
#     print(ordering_mds)
#     tsne = DroTSNE(reweighted_similarities)
#     ordering_tsne = tsne.get_leaf_ordering()
#     print(ordering_tsne)
