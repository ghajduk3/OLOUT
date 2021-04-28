from openTSNE import TSNE
from openTSNE.callbacks import ErrorLogger
import numpy as np
from typing import List


from sklearn.model_selection import train_test_split
"""
Idea is to use t-sne on input similarity matrix to infer leaf ordering and then visualize it.
"""
def set_tsne(perplexity=30):
    return TSNE(
        perplexity=perplexity,
        metric="euclidean",
        callbacks=ErrorLogger(),
        n_jobs=2,
        random_state=42,
    )

def get_tsne_embedding(similarity_matrix:np.ndarray):
    tsne = set_tsne(perplexity=30)
    embedding = tsne.fit(similarity_matrix)
    # We collect the leaves in clockwise direction, sort the y-values for positive x coords and take it in order
    # Then sort by ascending y values for negative x

    return embedding

def get_leaf_ordering(similarity_matrix:np.ndarray)->List:
    pass

if __name__ == '__main__':
    dis = np.array([[0, 5, 4, 7, 6, 8],
                    [5, 0, 7, 10, 9, 11],
                    [4, 7, 0, 7, 6, 8],
                    [7, 10, 7, 0, 5, 9],
                    [6, 9, 6, 5, 0, 8],
                    [8, 11, 8, 9, 8, 0]])
    embedding = get_tsne_embedding(dis)
    pos_neg = embedding[:,0] > 0
    neg_indices = np.where(pos_neg == False)
    pos_indices = np.where(pos_neg == True)
    negative = embedding[neg_indices]
    negative_ind = embedding[neg_indices][:,1].argsort()

    positive = embedding[pos_indices]
    positive_ind = embedding[pos_indices][:,1].argsort()

    print(embedding, negative,negative_ind, neg_indices )
    print(positive,positive_ind, pos_indices)



