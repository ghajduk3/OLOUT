class TreeNode(object):
    def __init__(self,id,distance):
        self.id = id
        self.distance = distance
        self.children = []
        # self.left
        # self.right

    def get_id(self):
        return self.id

    def get_children(self):
        return self.children

    def get_distance(self):
        return self.distance

    def is_leaf(self):
        return len(self.children) == 0

    def add_node(self,node):
        if not isinstance(node,TreeNode):
            raise ValueError("Node should be instance of TreeNode")
        self.children.append(node)

    def get_left(self):
        return self.children.pop(0)

    def get_right(self):
        return self.children.pop()

    def pre_order(self):
        stack = [self]
        preorder = []
        while len(stack) > 0 :
            nd = stack.pop()
            ndid = nd.id
            if nd.is_leaf():
                preorder.append(ndid)
            else:
                for child in reversed(nd.get_children()):
                    stack.append(child)
        return preorder


if __name__ == '__main__':
    root = TreeNode(0,2)
    child_1 = TreeNode(1,3)
    child_1_1 = TreeNode(5,2)
    child_1.add_node(child_1_1)
    child_2_1 = TreeNode(6,3)
    child_2 = TreeNode(2,4)
    child_2.add_node(child_2_1)
    child_3 = TreeNode(3,3)
    child_4 = TreeNode(4,5)
    root.add_node(child_1)
    root.add_node(child_2)
    root.add_node(child_3)
    root.add_node(child_4)

    print(root.pre_order())