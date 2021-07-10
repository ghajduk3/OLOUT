from openTSNE import TSNE, affinity, initialization, TSNEEmbedding
from openTSNE.callbacks import ErrorLogger
import numpy as np
from typing import List
import matplotlib.pyplot
matplotlib.use("Qt5Agg")



"""
Idea is to use t-sne on input similarity matrix to infer leaf ordering and then visualize it.
"""

def set_tsne(perplexity=30):
    return TSNE(
        perplexity=perplexity,
        initialization="pca",
        metric="cosine",
        callbacks=ErrorLogger(),
        n_jobs=2,
        random_state=42,
    )

def get_global_structure_tsne_embedding(similarity_matrix):

    affinities_multiscale_mixture = affinity.Multiscale(
        similarity_matrix,
        perplexities=[50, 500],
        metric="euclidean",
        n_jobs=8,
        random_state=3,
    )
    init = initialization.pca(similarity_matrix, random_state=42)
    embedding = TSNEEmbedding(
        init,
        affinities_multiscale_mixture,
        negative_gradient_method="fft",
        n_jobs=8,
    )
    embedding = embedding.optimize(n_iter=250, exaggeration=12, momentum=0.5)
    embedding = embedding.optimize(n_iter=750, exaggeration=1, momentum=0.8)


    return embedding
def get_tsne_embedding(similarity_matrix:np.ndarray):
    tsne = set_tsne(perplexity=2)
    embedding = tsne.fit(similarity_matrix)

    return embedding

# def get_leaf_ordering(similarity_matrix:np.ndarray)->List:
#
#     embedding = get_tsne_embedding(similarity_matrix)
#     print(embedding)
#     pos_neg = embedding[:,1] > 0
#     neg_indices = np.where(pos_neg == False)[0]
#     pos_indices = np.where(pos_neg == True)[0]
#     negative_ind = embedding[neg_indices][:,0].argsort()
#     positive_ind = embedding[pos_indices][:,0].argsort()[::-1]
#
#     return np.concatenate((pos_indices[positive_ind],neg_indices[negative_ind]),axis=0)


if __name__ == '__main__':
    dis = np.array([[0, 5, 4, 7, 6, 8],
                    [5, 0, 7, 10, 9, 11],
                    [4, 7, 0, 7, 6, 8],
                    [7, 10, 7, 0, 5, 9],
                    [6, 9, 6, 5, 0, 8],
                    [8, 11, 8, 9, 8, 0]])
    embedding = get_global_structure_tsne_embedding(dis)
    print(embedding)
    # tsne_plot.plot(embedding, [0, 1, 2, 3, 4, 5])
    # matplotlib.pyplot.show()





