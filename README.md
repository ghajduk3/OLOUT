# OLOUT - Optimal leaf ordering of phylogenetic trees
##### Author: Gojko Hajdukovic, 11.2021

Table of contents:
1. [Project description](#description)
2. [Goals](#goals)
3. [Data](#data)
4. [Data transformation pipeline](#datatransform)


<a name="description"></a>
## Project description
This project includes all the data and the code necessary for the reproduction of the results described
and generated while working on the Master Thesis with title "Optimal leaf ordering of phylogenetic trees" at the Faculty of Computer and Information Science, University of Ljubljana.

<a name="goals"></a>
## Goals
This Thesis focuses on exploring and evaluating approaches for inducing optimal linear leaf ordering,
generalized for phylogenetic `k-ary` trees, and the visual representation of such optimally ordered phylogenetic trees in 2-dimensional space.
For this purpose, we divide the problem into two subproblems:
- We aim to explore and evaluate a selected algorithm that induces a linear leaf ordering for phylogenetic trees - `KOLO`, introduced in [Bar-Joseph et al.](https://academic.oup.com/bioinformatics/article/19/9/1070/284974?login=true).
- We aim to explore and experimentally evaluate the Radial Layout algorithm introduced in 
  `Bachmaier et al.` for visualizing phylogenetic trees in 2-dimensional space, which takes into account the induced linear leaf order
    - We aim to present an evaluation metric to measure the quality of the layout in 2-dimensional space.
    - We aim to present and explore an alternative heuristic for the Radial Layout that takes into account the specifics of phylogenetic trees.
    - We aim to present two postprocessing algorithms applied to the Radial Layout so that the quality of the visualization layout is improved.

<a name="data"></a>
## Data
To achieve the above described goals and to test and evaluate existing and newly presented algorithms
we collected the publicly available data from the online phylogenetic tree database, [TreeBase](https://treebase.org/treebase-web/home.html).
We collected 1952 available publication data in Nexus format out of which we processed 369 phylogenetic
trees that follow the standard Newick format notation. The source data collected in Nexus format is available in the [source data](data/source_data) directory. 

<a name="datatransform"></a>
## Data transformation pipeline
As described in the Thesis, publicly available phylogenetic databases
usually store the phylogenetic trees as Newick Formatted strings without providing the original distance matrix neither the algorithm used for the construction of the phylogenetic trees. 
The algorithms that infer the optimal linear leaf ordering base their procedure on the evolutionary distance between leaf nodes,
therefore they need to reconstruct the distance matrix first.
To tackle the above described problems, as a first contribution of the thesis we construct a
data transformation pipeline that extracts, transforms and loads the raw phylogenetic data available from the database, [TreeBase](https://treebase.org/treebase-web/home.html).

The transformation pipeline that constructs the final transformed dataset and is stored in [preprocess](olout/utils/preprocess.py) python module.
The pipeline consists of several steps:
- Parses the raw Nexus files.
- Extracts the phylogenetic tree in the Newick format along with the node-label mapping.
- Extracts the URL of the publication data available at [TreeBase](https://treebase.org/treebase-web/home.html)
- Reconstructs original distance matrix.
- Stores the extracted and constructed data as `JSON` formatted files in the [final_data](data/final_data) directory.

All the data for the 369 processed phylogenetic trees that follow the standard Newick format notation is available in the [final_data](data/final_data) directory.
Each processed publication `JSON` file from the `final data` consists from following fields:
  ```
  {
    "NEXUS_FILE_URL": "...",
    "NEWICK_TREE": "...",
    "DISTANCE_MATRIX": [[]],
    "NODE_MAPPING" : [[]]
  }
```
<a name="solutions"></a>
## Implemented algorithms 

## Project structure 

## Setup 

## Usage 

## Examples