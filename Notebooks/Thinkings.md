##Thoughts
1. Function to be optimized is Simmilarity/Dissimilarity between leaves. If similarity then it should be minimized.




###Problems:
1. NJ algorithms produce tree, not linkage matrix. Tree can be represented in `Newick format` . 
   `(b:7.000000, (c:3.000000, a:6.000000):1.000000, d:3.000000);` .
   Maybe from Newick format I can transform it back to Linkage matrix but that would create extra overhead.
   Maybe I just have to adopt the algorithm in order to use the tree in Newick format.
   