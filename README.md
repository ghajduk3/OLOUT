# OLOUT - Optimal leaf ordering of phylogenetic trees
##### Author: Gojko Hajdukovic, 11.2021

Table of contents:
1. [Project description](#description)
2. [Goals](#goals)
3. [Solution](#solutions)
4. [Data](#data)


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
    - We aim to introduce and explore two postprocessing algorithms applied to the Radial Layout so that the quality of the visualization layout is improved.

<a name="data"></a>
## Data
To achieve the above described goals and to test and evaluate existing and newly presented algorithms
we collected the publicly available data from the online phylogenetic tree database, [TreeBase](https://treebase.org/treebase-web/home.html).
We collected 1952 available publication data in Nexus format out of which we processed 369 phylogenetic
trees that follow the standard Newick format notation. The source data collected in Nexus format is available in the [source data](data/source_data) directory. 

## Data transformation pipeline

    
<a name="solutions"></a>
## Implemented algorithms 

## Project structure 

## Setup 

## Usage 

## Examples