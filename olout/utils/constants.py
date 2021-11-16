from olout.orderings.dimensionality_reduction import DroPca, DroMDS, DroTSNE
from olout.visualizations.radial import RadialLayoutBranchLength, RadialLayoutLeafCount

DIMENSIONALITY_REDUCTION_METHOD_PCA = 'PCA'
DIMENSIONALITY_REDUCTION_METHOD_MDS = 'MDS'
DIMENSIONALITY_REDUCTION_METHOD_TSNE = 'TSNE'
RADIAL_LAYOUT_BRANCH_LENGTH = 'BRANCH_LENGTH'
RADIAL_LAYOUT_LEAF_COUNT = 'LEAF_COUNT'

DIMENSIONALITY_REDUCTION_METHOD_MAPPINGS = {
    DIMENSIONALITY_REDUCTION_METHOD_PCA: DroPca,
    DIMENSIONALITY_REDUCTION_METHOD_MDS: DroMDS,
    DIMENSIONALITY_REDUCTION_METHOD_TSNE: DroTSNE,
}

RADIAL_VISUALIZATION_METHOD_MAPPINGS = {
    RADIAL_LAYOUT_BRANCH_LENGTH: RadialLayoutBranchLength,
    RADIAL_LAYOUT_LEAF_COUNT: RadialLayoutLeafCount,
}