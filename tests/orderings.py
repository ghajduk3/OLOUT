import numpy as np
from src.orderings.kolo import KOLO
from src.orderings.alo import ALO
from src.orderings.dimensionality_reduction import DroTSNE,DroMDS,DroPca
from src.utils.measures import adjacent_pair_similarity_ratio
from src.utils.newick import Parser

if __name__ == "__main__":
    dis_1 = np.array([[0, 5, 4, 7, 6, 8],
                    [5, 0, 7, 10, 9, 11],
                    [4, 7, 0, 7, 6, 8],
                    [7, 10, 7, 0, 5, 9],
                    [6, 9, 6, 5, 0, 8],
                    [8, 11, 8, 9, 8, 0]])

    tree_string_1 = "(5:5.00000,(2:2.000000,(1:4.000000, 0:1.000000):1.000000):2.000000,(4:2.000000, 3:3.000000):1.000000);"

    dis_2 = np.array([[0, 5, 9, 9, 8],
                       [5, 0, 10, 10, 9],
                       [9, 10, 0, 8, 7],
                       [9, 10, 8, 0, 3],
                       [8, 9, 7, 3, 0]])
    tree_string_2 = '(4:1.000000,(2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000,3:2.000000);'

    # KOLO  - TREE 1
    tree_kolo = KOLO(tree_string_1, dis_1)
    tree_1, tree_ordering_1 = np.array(tree_kolo.optimal_leaf_ordering())
    similarity_ratio_1 = adjacent_pair_similarity_ratio(tree_ordering_1, dis_1)
    # Adjacent pair similarity ratio
    print("*"*30)
    print(similarity_ratio_1)
    print("*"*30)

    # ALO - TREE 1
    tree = Parser.parse_newick_tree(tree_string_1)
    tree_alo = ALO(tree_string_1,dis_1)
    ordering = tree_alo.get_optimal_leaf_ordering()
    similarity_ratio = adjacent_pair_similarity_ratio(ordering, dis_1)
    # Adjacent pair similarity ratio
    print("*"*30)
    print(similarity_ratio, ordering)
    print("*"*30)


    # DIMENSIONALITY REDUCTION - TREE 1
    pca = DroPca(similarity_matrix=dis_1)
    tsne = DroTSNE(similarity_matrix=dis_1)
    mds = DroMDS(similarity_matrix=dis_1)

    ordering_pca = pca.get_leaf_ordering()
    ordering_mds = mds.get_leaf_ordering()
    ordering_tsne = tsne.get_leaf_ordering()
    # similarity_ratio = adjacent_pair_similarity_ratio(ordering, dis_1)
    ratio_pca = adjacent_pair_similarity_ratio(ordering_pca, dis_1)
    ratio_mds = adjacent_pair_similarity_ratio(ordering_mds, dis_1)
    ratio_tsne = adjacent_pair_similarity_ratio(ordering_tsne, dis_1)
    print("*"*30)
    print(f"PCA - ordering : {ordering_pca} with ratio {ratio_pca}")
    print(f"MDS - ordering : {ordering_mds} with ratio {ratio_mds}")
    print(f"TSNE - ordering : {ordering_tsne} with ratio {ratio_tsne}")
    print("*"*30)









