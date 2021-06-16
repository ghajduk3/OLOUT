import numpy as np
from newick import Parser
from math import pi
from src.utils.tree import TreeNode
from src.visualizations import radial
from src.orderings.kolo import KOLO
#Distance matrix reconstruction

def get_distance_matrix(tree):
    number_children = TreeNode.get_children_number(tree)
    l = {}
    x = {}
    omega = {}
    tau = {}
    distances = {}
    radial.postorder_traverse_radial(tree, l)
    root = tree.get_id()
    x[root] = np.array((0, 0))
    omega[root] = 2 * pi
    tau[root] = 0
    radial.preorder_traverse_radial(tree, None, root, x, l, omega, tau, distances)
    level_order = radial.reverse_level_order_traversal(tree)
    print(level_order)
    return [[radial.LCA(distances, level_order,i,j) for j in range(1,number_children+1)] for i in range(1,number_children+1)]




if __name__ == "__main__":
    dis_2 = np.array([[0, 5, 9, 9, 8],
                       [5, 0, 10, 10, 9],
                       [9, 10, 0, 8, 7],
                       [9, 10, 8, 0, 3],
                       [8, 9, 7, 3, 0]])
    tree_string_2 = '(4:1.000000,(2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000,3:2.000000);'
                    # '(4:1.000000,(2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000,3:2.000000);'

    # tree = Parser.parse_newick_tree(tree_string_2)
    # print(get_distance_matrix(tree))

    tree_string_1 = '(((((((((3:197.0,4:126.0):101.0,(5:223.0,6:322.0):102.0):103.0,(7:157.0,8:101.0):250.0):120.0,(((9:158.0,10:180.0):87.0,11:172.0):121.0,(((12:156.0,13:188.0):90.0,((14:123.0,15:188.0):55.0,16:160.0):73.0):90.0,(17:280.0,18:206.0):151.0):70.0):80.0):129.0,(((((((((19:55.0,20:54.0):21.0,21:57.0):77.0,(28:70.0,29:59.0):75.0):25.0,((22:55.0,23:62.0):43.0,((24:65.0,25:53.0):36.0,(26:34.0,27:28.0):55.0):75.0):22.0):56.0,(50:63.0,51:59.0):148.0):35.0,((((30:0.0,31:0.0):128.0,33:137.0):27.0,(((35:54.0,36:74.0):37.0,(37:95.0,38:129.0):16.0):55.0,((((((((39:43.0,40:57.0):18.0,41:46.0):18.0,43:70.0):16.0,42:42.0):41.0,45:44.0):18.0,44:76.0):28.0,46:96.0):43.0,((47:28.0,48:28.0):42.0,49:69.0):62.0):79.0):28.0):26.0,((32:86.0,(52:174.0,53:151.0):106.0):39.0,34:159.0):26.0):27.0):111.0,((54:6.0,55:0.0):209.0,((56:4.0,57:9.0):10.0,58:10.0):247.0):120.0,((60:234.0,61:307.0):139.0,62:255.0):229.0,59:344.0):105.0,63:367.0):114.0,(((68:27.0,69:34.0):160.0,(((71:55.0,72:55.0):35.0,((73:17.0,74:17.0):99.0,75:51.0):31.0):154.0,76:188.0):102.0):77.0,70:162.0):170.0,(((64:106.0,65:119.0):115.0,66:163.0):122.0,67:348.0):185.0):136.0):143.0,(((((((((((80:53.0,81:40.0):96.0,82:83.0):30.0,83:113.0):39.0,84:129.0):64.0,(86:110.0,87:77.0):104.0):60.0,85:142.0):71.0,88:155.0):71.0,(((77:97.0,78:98.0):108.0,79:179.0):108.0,((94:14.0,95:12.0):191.0,(((96:22.0,97:21.0):126.0,98:122.0):97.0,99:133.0):123.0):158.0):98.0,((((90:38.0,91:43.0):228.0,92:200.0):96.0,93:227.0):87.0,((100:229.0,101:231.0):144.0,102:293.0):139.0):115.0):70.0,89:218.0):100.0,(((103:6.0,104:7.0):122.0,((105:52.0,106:38.0):42.0,107:74.0):58.0):125.0,(((108:56.0,109:70.0):93.0,110:154.0):58.0,111:165.0):59.0):102.0):85.0,112:217.0):160.0):151.0,(117:187.0,(((((118:149.0,119:214.0):99.0,(121:359.0,122:278.0):113.0):86.0,(120:220.0,132:290.0):99.0):120.0,((((123:120.0,124:99.0):108.0,125:180.0):114.0,((128:193.0,129:292.0):158.0,130:247.0):177.0):116.0,(126:136.0,127:165.0):181.0):87.0):153.0,131:277.0):177.0):183.0):190.0,((114:184.0,115:216.0):208.0,116:284.0):166.0):201.0,((1:254.0,2:246.0):217.0,113:284.0):204.0);'
    tree1 = Parser.parse_newick_tree(tree_string_1)
    print(tree1)

    # distance_matrix = get_distance_matrix(tree1)
    #
    # kolo = KOLO(tree_string_1,distance_matrix)
    # print(kolo.optimal_leaf_ordering())

    # print("Number of children", TreeNode.get_children_number(tree1))