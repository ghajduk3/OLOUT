class InvalidChildrenNumberError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class LeafError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class TreeNode(object):
    """
    Class that represents k-ary tree node.

    ```

    Attributes
    ----------
    id : str
        the id of tree node
    distance : float
        represents the branch distance to it's predecessor
    children : list
        represents a list of children nodes of o node

    Methods
    -------

    """
    def __init__(self, id, distance):
        """
        Parameters
        ----------
        id : str
            the id of tree node
        distance : float
            represents the branch distance to it's predecessor
        children : list
            represents a list of children nodes of o node
        """
        self.id = int(id)
        self.distance = distance
        self.children = []

    def get_id(self):
        return self.id

    def get_children(self):
        return self.children

    def get_distance(self):
        return self.distance

    def set_distance(self, distance):
        self.distance = distance

    def is_leaf(self):
        return len(self.children) == 0

    def add_node(self, node):
        if not isinstance(node, TreeNode):
            raise ValueError("Node should be an instance of TreeNode")
        self.children.append(node)

    def get_left(self):
        if len(self.children) > 2:
            raise InvalidChildrenNumberError("There are more than two children")
        elif self.is_leaf():
            return None
        else:
            return self.children[0]

    def get_right(self):
        if len(self.children) > 2:
            raise InvalidChildrenNumberError("There are more than two children")
        elif self.is_leaf():
            return None
        else:
            return self.children[1]


    def pre_order(self):
        """
        Traverses the tree leaf nodes according to pre order.
        """
        stack = [self]
        preorder = []
        while len(stack) > 0:
            nd = stack.pop()
            ndid = nd.id
            if nd.is_leaf():
                preorder.append(ndid)
            else:
                for child in reversed(nd.get_children()):
                    stack.append(child)
        return preorder

    def pre_order_internal(self):
        """
        Traverses all tree nodes according to pre order.
        """
        stack = [self]
        preorder = [self.id]
        while len(stack) > 0:
            flag = 0
            nd = stack[-1]
            if nd.is_leaf():
                pass
            else:
                parent = nd
            children = parent.get_children()
            for index in range(0,len(children)):
                child = children[index]
                if child.id not in preorder:
                    flag = 1
                    stack.append(child)
                    preorder.append(child.id)
                    break
            if flag == 0:
                stack.pop()
        return preorder





if __name__ == '__main__':
    root = TreeNode(0, 2)
    child_1 = TreeNode(1, 3)
    child_1_1 = TreeNode(5, 2)
    child_1_2 = TreeNode(7,3)
    child_1_1_1 = TreeNode(55, 2)
    child_1_2_1 = TreeNode(12,3)
    child_1_1.add_node(child_1_1_1)
    child_1_1.add_node(child_1_2_1)
    child_1.add_node(child_1_1)
    child_1.add_node(child_1_2)
    child_2_1 = TreeNode(6, 3)
    child_2 = TreeNode(2, 4)
    child_2.add_node(child_2_1)
    child_3 = TreeNode(3, 3)
    child_4 = TreeNode(4, 5)
    root.add_node(child_1)
    root.add_node(child_2)
    root.add_node(child_3)
    root.add_node(child_4)

    print(root.pre_order_internal())
