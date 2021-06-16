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

    def __get_leaf_label(self):
        label = ''
        token = self.stream.read_next()
        while True:
            if token != ":":
                label += token
                next(self.stream)
                token = self.stream.read_next()
            else:
                break
        return label

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
            # print("USAO U LEAF", token)
            self.token = Token('LEAF',None)
        return self.tree_label

    def tree_label(self):
        self.remove_spaces()
        token = self.stream.read_next()

        label = self.__get_leaf_label()
        self.token = Token('LABEL',label)
        # next(self.stream)
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
                # print(token.type, token.value)
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
    tree_big = '((((((((((((((((1:7.0,2:2.0):1.0,(3:5.0,4:13.0):3.0):0.0,26:2.0):0.0,8:0.0):0.0,59:1.0):0.0,58:1.0):0.0,36:0.0):0.0,38:0.0):0.0,(29:0.0,30:4.0):0.0):0.0,25:4.0):2.0,6:0.0):1.0,(((65:1.0,67:0.0):1.0,77:1.0):2.0,110:5.0):2.0):1.0,(((((((((40:0.0,((44:3.0,(49:3.0,52:1.0):0.0):0.0,55:1.0):0.0):0.0,102:0.0):0.0,53:1.0):0.0,46:6.0):1.0,(43:2.0,56:4.0):0.0):2.0,47:9.0):3.0,(((((((41:2.0,48:3.0):0.0,51:1.0):0.0,57:1.0):0.0,54:1.0):0.0,50:8.0):0.0,45:2.0):0.0,105:1.0):4.0):0.0,42:4.0):1.0,66:6.0):0.0):4.0,(9:6.0,(62:0.0,63:9.0):5.0):2.0):0.0,(((((5:2.0,23:0.0):0.0,((((7:0.0,(100:2.0,101:0.0):0.0):0.0,60:0.0):0.0,(28:3.0,86:6.0):0.0):1.0,(((((((10:4.0,109:0.0):1.0,((12:0.0,(((((((69:0.0,94:7.0):0.0,73:0.0):0.0,79:0.0):0.0,((70:1.0,(82:1.0,87:2.0):0.0):0.0,76:0.0):0.0):0.0,81:0.0):0.0,75:0.0):0.0,72:0.0):0.0):1.0,78:4.0):0.0):0.0,(((33:0.0,61:1.0):0.0,84:2.0):1.0,85:3.0):0.0):0.0,(80:1.0,83:0.0):2.0):1.0,(((((11:1.0,(13:1.0,14:0.0):0.0):0.0,15:0.0):1.0,(98:1.0,104:0.0):1.0):2.0,103:0.0):1.0,(95:3.0,96:2.0):2.0):0.0):1.0,27:0.0):0.0,(16:0.0,((((((18:2.0,(74:0.0,99:3.0):1.0):0.0,106:1.0):0.0,89:0.0):0.0,90:0.0):0.0,93:0.0):1.0,((((((24:3.0,35:6.0):0.0,37:0.0):0.0,97:0.0):0.0,88:0.0):2.0,91:4.0):1.0,(((68:1.0,71:0.0):0.0,107:4.0):3.0,92:1.0):1.0):0.0):0.0):0.0):0.0):0.0):2.0,108:5.0):2.0,(22:10.0,(34:3.0,64:4.0):0.0):0.0):0.0,((17:6.0,(19:0.0,31:1.0):3.0):0.0,21:23.0):1.0):2.0):0.0,((20:2.0,39:3.0):21.0,32:17.0):2.0);'
    stream = Stream(tree_big)

    lexer = Lex(stream)
    parser = Parser(lexer)
    tree = parser.parse()


