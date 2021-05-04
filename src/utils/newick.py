import collections,sys
from io import StringIO
from typing import Callable, List
from tree import TreeNode
# https://github.com/golang/go/blob/master/src/text/template/parse/lex.go

class InvalidTokenType(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
class ParseError(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(message)


""" Represents a token or text string returned from the scanner"""
Item = collections.namedtuple('Item', ['type','value'])


class Stream(object):
    """
    Class that represents stream.

    Converts input string to stream. Implements methods for stream manipulation.

    ```

    Attributes
    ----------
    stream : str
        input string that is to be converted to stream

    Methods
    -------
    closed()
        indicates whether the stream is open
    read_next()
        emits next stream token
    close()
        closes the stream

    """
    def __init__(self,stream):
        """
        Parameters
        ----------
        stream : str
            input string that is to be converted to stream.
        """
        self._stream = StringIO(stream)
    def __next__(self):
        """
        Emits next stream token

        Raises
        ------
        StopIteration
            if the stream is closed or the next token is an empty char.
        """
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
        """
        Indicates whether the stream is open.
        """
        return self._stream.closed
    def read_next(self):
        """
        Emits next stream token.
        """
        return self._next
    def close(self):
        """
        Closes the stream.
        """
        return self._stream.close()


class Token(object):
    """
    Class that represents token.

    Token consists of type and value.

    ```

    Attributes
    ----------
    type : str
        type of the token. Each token can be one of the following types : TREE, SUBTREE, LEAF, LABEL, DISTANCE, ENDTREE, ENDSUBTREE.
    value : any
        token value.

    """
    token_types = ('TREE', 'SUBTREE' , 'LEAF', 'LABEL', 'DISTANCE', 'ENDTREE', 'ENDSUBTREE')

    def __init__(self,type,value=None):
        self.type = type
        self.value = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self,value:str):
        if value not in self.token_types:
            raise InvalidTokenType("Token type is not valid!")
        else:
            self._type = value



class Lex(object):
    """
    Class that represents lexer.

    Lexer behaves like a state machine, lexing string elements.
    ```

    Attributes
    ----------
    stream : Stream
        stream object of input string
    token : Token
        current token in lexer
    state : Callable
        current state of the lexer state machine

    """
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
    """
    Class that represents parsing of Lexer tree into the TreeNode phylogenetic tree hierarchy.

    ```
    Attributes
    ----------
    lex : Lex
        represents lexed phylogenetic tree to be parsed
    stack : List

    trees : List

    current_internal : int
        first id of internal nodes. Each succesive internal node is incremented by one.
    """
    def __init__(self,lex):
        self.lex = lex
        self.stack = list()
        self.trees = list()
        self.current_internal = 999


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
                if token.type == 'TREE':
                    pass
                elif token.type == 'SUBTREE':
                    self._subtree_start()
                elif token.type == 'LEAF':
                    self._add_leaf()
                elif token.type == 'DISTANCE' and seen_tokens[-2].type == 'ENDSUBTREE':
                    self._subtree_close(token.value)
                elif token.type == 'ENDTREE':
                    return self.trees[0]



    def _subtree_start(self):
        self.current_internal +=1
        subtree_root = TreeNode(self.current_internal,0)
        self.stack.append(subtree_root)
        self.trees.append(subtree_root)

    def _add_leaf(self):
        label = next(self.lex)
        if label.type != 'LABEL':
            raise ParseError("Label expected")
        value = next(self.lex).value
        leaf = TreeNode(label.value,value)
        self.stack[-1].add_node(leaf)

    def _subtree_close(self,distance):
        subtree = self.stack.pop()
        subtree.set_distance(distance)
        self.trees.pop()
        self.trees[-1].add_node(subtree)


if __name__ == "__main__":
    # print(token.type)
    # tree_string = "((2:2.000000,(1:4.000000, 0:1.000000, 9:3.5):1.000000):2.000000, (4:2.000000, 3:3.000000):1.000000,5:5.00000);"
    tree_string_1 = '(3:2.000000,(2:4.000000, (1:3.000000, 0:2.000000):3.000000):2.000000, 4:1.000000);'
    stream = Stream(tree_string_1)
    tree = Parser.parse_newick_tree(tree_string_1)
    print(type(tree.id))
    #
