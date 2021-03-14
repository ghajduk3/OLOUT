import collections,sys
from io import StringIO
from tree import TreeNode
# https://github.com/golang/go/blob/master/src/text/template/parse/lex.go

class ParseError(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(message)


""" Represents a token or text string returned from the scanner"""
Item = collections.namedtuple('Item', ['type','value'])
class StreamIterator:
    def __init__(self,stream):
        self._stream = stream
    def __next__(self):
        char = self._stream.read(1)
        if self._stream.closed:
            raise StopIteration
        if char == '':
            self._stream.close()
            raise StopIteration
        return char


class Stream(object):
    def __init__(self,stream):
        self._stream = StringIO(stream)
        self._next = self._stream.read(1)
    def __next__(self):
        char = self._stream.read(1)
        self._next = char
        if self._stream.closed:
            raise StopIteration
        if char == '':
            self._stream.close()
            raise StopIteration
        return char

    def __iter__(self):
        return self
    def closed(self):
        return self._stream.closed
    def read_next(self):
        return self._next
    def close(self):
        return self._stream.close()


class Token(object):
    def __init__(self,type,value=None):
        self.type = type
        self.value = value

class Lex(object):

    def __init__(self,stream):
        self.stream = stream
        self.token = None
        self.state = self.start_tree

    def __iter__(self):
        return self
    def __next__(self):
        if not self.token:
            self.state = self.state()
        token, self.token = self.token, None
        return token

    def remove_spaces(self):
        while self.stream.read_next().isspace():
            next(self.stream)

    def _get_leaf_distance(self):
        distance = ''
        token = self.stream.read_next()
        while True:
            if str.isdigit(token) or token == '.':
                distance += token
                next(self.stream)
                token = self.stream.read_next()
            else:
                break
        return distance

    def start_tree(self):
        if self.stream.closed():
            return sys.exit()
        for token in self.stream:
            if token == '(':
                break
        self.token = Token('TREE','')
        return self.start_subtree

    def start_subtree(self):
        self.remove_spaces()
        token = self.stream.read_next()
        if token == '(':
            self.token = Token('SUBTREE')
            next(self.stream)
            return self.start_subtree
        else:
            self.token = Token('LEAF',None)
        return self.tree_label

    def tree_label(self):
        self.remove_spaces()
        token = self.stream.read_next()
        self.token = Token('LABEL',token)
        next(self.stream)
        return self.label_length

    def label_length(self):
        token = self.stream.read_next()
        if token == ":":
            next(self.stream)
            dist = float(self._get_leaf_distance())
        elif token == ";":
            return self.end_subtree
        else:
            dist = None
        self.token = Token('DISTANCE',dist)
        return self.end_subtree

    def end_subtree(self):
        self.remove_spaces()
        token = self.stream.read_next()
        if token == ';':
            self.token = Token('ENDTREE','EOF')
            self.stream.close()
            return self.start_tree
        elif token == ',':
            next(self.stream)
            return self.start_subtree
        elif token == ')':
            self.token = Token('ENDSUBTREE')
            next(self.stream)
            return self.label_length

class Parser(object):
    def __init__(self,lex):
        self.lex = lex
        self.stack = list()
        self.trees = list()
        self.internal_nodes = list()


    @classmethod
    def parse_newick_tree(cls,tree_string):
        stream = Stream(tree_string)
        lex = Lex(stream)
        parser = cls(lex)
        return parser.parse()

    def parse(self):
        seen_tokens = []
        for token in self.lex:
            if token != None:
                seen_tokens.append(token)
                # Check for tree start
                # print(token.type)
                if token.type == 'TREE':
                    internal_id = 999
                    self.internal_nodes.append(internal_id)
                    root = TreeNode(internal_id,0)
                    self.trees.append(root)
                    self.stack.append(root)
                elif token.type == 'SUBTREE':
                    self._subtree_start()
                elif token.type == 'LEAF':
                    self._add_leaf()
                elif token.type == 'DISTANCE' and seen_tokens[-2].type == 'ENDSUBTREE':
                    self._subtree_close(token.value)
                elif token.type == 'ENDTREE':
                    return self.trees[0]



    def _subtree_start(self):
        internal_node = self.internal_nodes[-1] + 1
        self.internal_nodes.append(internal_node)
        subtree_root = TreeNode(internal_node,0)
        self.stack.append(subtree_root)
        self.trees.append(subtree_root)

    def _add_leaf(self):
        label = next(self.lex)
        if label.type != 'LABEL':
            raise ParseError("Label expected")
        value = next(self.lex)
        leaf = TreeNode(int(label.value),value)
        self.stack[-1].add_node(leaf)

    def _subtree_close(self,distance):
        subtree = self.stack.pop()
        subtree.set_distance(distance)
        self.trees.pop()
        self.trees[-1].add_node(subtree)


if __name__ == "__main__":

    tree_string = "((2:2.000000,(1:4.000000, 0:1.000000, 9:3.5):1.000000):2.000000, (4:2.000000, 3:3.000000):1.000000,5:5.00000);"
    tree = Parser.parse_newick_tree(tree_string)
    print(tree.pre_order_internal())