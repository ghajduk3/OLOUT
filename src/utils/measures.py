

def adjacent_pair_similarity_ratio(ordering, similarity_matrix):
    """
    Computes adjacent pait similarity ratio according to Jd/Jd_random. Detailed description is in
    Ding, Chris H. Q. 2002. “Analysis of Gene Expression Profiles,” 127–36. https://doi.org/10.1145/565196.565212
    """
    m, n = similarity_matrix.shape
    print(ordering, ordering[1])
    jd = sum([similarity_matrix[ordering[ind], ordering[ind + 1]] for ind in range(n - 1)])
    jd_random = (n - 1) * sum([similarity_matrix[i, j] / n ** 2 for i in range(n) for j in range(n)])
    return jd / jd_random