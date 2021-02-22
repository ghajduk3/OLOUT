import collections
from io import StringIO

# https://github.com/golang/go/blob/master/src/text/template/parse/lex.go

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
            print("Usao")
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
        for token in self.stream:
            if token == '(':
                break
        if self.stream.closed():
            self.token = Token('EOF',-1)
        self.token = Token('TREE','')
        return self.start_subtree

    def start_subtree(self):
        self.remove_spaces()
        token = self.stream.read_next()
        if token == '(':
            self.token = Token('SUBTREE')
            next(self.stream)
        else:
            self.token = Token('LEAF',None)
            next(self.stream)
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
        else:
            dist = None
        self.token = Token('DISTANCE',dist)
        return self.end_subtree

    def end_subtree(self):
        self.remove_spaces()
        token = self.stream.read_next()

        if token == ';':
            self.token = Token('EOF','ENDTREE')
            next(self.stream)
            return self.start_tree()






    # def make_tokens(self):
    #     for token in self.stream:
    #         if token == '(':
    #             self.tokens.append()


if __name__ == "__main__":
    it = Item("Gojko",3)
    stream  = StringIO("((2:2.000000,(1:4.000000, 0:1.000000):1.000000):1.000000, (4:2.000000, 3:3.000000):1.000000,5:5.00000);")
    s = Stream("((2:2.000000, (1:4.000000, 0:1.000000):1.000000):1.000000, (4:2.000000, 3:3.000000):1.000000,5:5.00000);")
    l = Lex(s)

    for i in l:
        if i != None:
            print(i.type)
    # print(next(l.stream))
    # print(next(l.stream))
    # print(next(l.stream))
    # print(l.stream.read_next())
    # print(l.stream.read_next())