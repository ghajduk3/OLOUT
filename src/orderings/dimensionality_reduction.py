import numpy as np
import typing
from abc import ABCMeta,abstractmethod
from sklearn.decomposition import PCA
from sklearn.manifold import MDS,TSNE
from src.orderings.tsne import get_tsne_embedding


class Dro(metaclass=ABCMeta):
    """
      Abstract base class that represents leaf ordering of phylogenetic trees using Dimensionality reduction methods.
      It takes initial similarity matrix and mapping between phylogenetic node labels and similarity matrix indexes.
      ```
      Attributes
      ----------
      similarity_matrix : np.ndarray
          represents similarities between leaf nodes of phylogenetic tree
      node_mappings : typing.Dict[int, typing.AnyStr]
          represents mapping between similarity matrix indexes and phylogenetic tree leaf node labels.

      Methods
      -------
      _get_first_component() -> np.ndarray
          returns similarity matrix reduced to the first component by applying specific
          dimensionality reduction method.
      get_leaf_ordering() -> np.ndarray
          performs sorting of the first component coordinates and
           induces leaf ordering of phylogenetic tree.

    """
    def __init__(self, similarity_matrix: np.ndarray, node_mapping: typing.Dict):
        self.similarity_matrix = similarity_matrix
        self.node_mapping = node_mapping

    @abstractmethod
    def _get_first_component(self) -> np.ndarray:
        pass

    @abstractmethod
    def get_leaf_ordering(self) -> typing.List:
        pass


class DroPca(Dro):
    """
      Class that induces leaf ordering of phylogenetic tree using PCA as a dimensionality reduction method.
    """
    def __init__(self, similarity_matrix: np.ndarray, node_mapping: typing.Dict):
        super().__init__(similarity_matrix, node_mapping)

    def _get_first_component(self) -> np.ndarray:
        pca = PCA(n_components=1)
        return pca.fit_transform(self.similarity_matrix)

    def get_leaf_ordering(self) -> typing.List:
        first_component = self._get_first_component()
        row, cols = first_component.shape
        leaf_ordering = first_component.reshape(1, row)[0].argsort()[::-1]
        return [self.node_mapping.get(leaf_node, '') for leaf_node in leaf_ordering]


class DroMDS(Dro):
    """
      Class that induces leaf ordering of phylogenetic tree using MDS as a dimensionality reduction method.
    """
    def __init__(self, similarity_matrix: np.ndarray, node_mapping: typing.Dict):
        super().__init__(similarity_matrix, node_mapping)

    def _get_first_component(self) -> np.ndarray:
        mds = MDS(n_components=1)
        return mds.fit_transform(self.similarity_matrix)

    def get_leaf_ordering(self) -> typing.List:
        first_component = self._get_first_component()
        row, cols = first_component.shape
        leaf_ordering = first_component.reshape(1, row)[0].argsort()[::-1]
        return [self.node_mapping.get(leaf_node, '') for leaf_node in leaf_ordering]


class DroTSNE(Dro):
    """
      Class that induces leaf ordering of phylogenetic tree using TSNE as a dimensionality reduction method.
    """
    def __init__(self, similarity_matrix: np.ndarray, node_mapping: typing.Dict):
        super().__init__(similarity_matrix, node_mapping)

    def _get_first_component(self) -> np.ndarray:
        two_components = get_tsne_embedding(self.similarity_matrix)
        pca = PCA(n_components=1)
        return pca.fit_transform(two_components)

    def get_leaf_ordering(self) -> typing.List:
        first_component = self._get_first_component()
        row, cols = first_component.shape
        leaf_ordering = first_component.reshape(1, row)[0].argsort()[::-1]
        return [self.node_mapping.get(leaf_node, '') for leaf_node in leaf_ordering]



#
if __name__ == "__main__":
    dis = np.array([[0, 5, 4, 7, 6, 8],
                    [5, 0, 7, 10, 9, 11],
                    [4, 7, 0, 7, 6, 8],
                    [7, 10, 7, 0, 5, 9],
                    [6, 9, 6, 5, 0, 8],
                    [8, 11, 8, 9, 8, 0]])

    reweighted_similarities = np.array([[0, 5, 8, 14, 12, 16],
                    [5, 0, 14, 20, 18, 22],
                    [8, 14, 0, 14, 12, 16],
                    [14, 20, 14, 0, 5, 18],
                    [12, 18, 12, 5, 0, 16],
                    [16, 22, 16, 18, 16, 0]])

    pca = DroPca(reweighted_similarities, {})
    ordering_pca = pca.get_leaf_ordering()
    print(ordering_pca)
    mds = DroMDS(reweighted_similarities, {})
    ordering_mds = mds.get_leaf_ordering()
    print(ordering_mds)
    tsne = DroTSNE(reweighted_similarities, {})
    ordering_tsne = tsne.get_leaf_ordering()
    print(ordering_tsne)
