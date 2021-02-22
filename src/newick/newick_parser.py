#!/usr/bin/env python

import os, re, sys
import bisect, collections
# if sys.version_info < (3,):
#     from cStringIO import StringIO
# else:
from io import StringIO


def enum(*sequential, **named):
    """creates an Enum type with given values"""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    enums['reverse'] = dict((value, key) for key, value in enums.items())
    return type('Enum', (object, ), enums)


class ParseError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


class LexError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


Item = collections.namedtuple('Item', 'typ val')


class Streamer(object):

    """ Wraps an io.StringIO and iterates a byte at a time,
    instead of a line at a time """

    def __init__(self, stream):
        """ _peek always looks ahead 1 position """
        if isinstance(stream, str):
            stream = StringIO(stream)
        self.stream = stream
        self._peek = self.stream.read(1)

    def __iter__(self):
        return self

    def next(self):
        """ Python 2.x / 3.x compatibility hack """
        return self.__next__()

    def __next__(self):
        char = self._peek

        self._peek = self.stream.read(1)

        if self.stream.closed:
            raise StopIteration

        if char == '':
            self.stream.close()
            raise StopIteration

        return char

    def peek(self):
        return self._peek

    def isclosed(self):
        return self.stream.closed


class Lexer(object):

    """ Breaks newick stream into lexing tokens:
    Works as a state machine, like Rob Pike's Go text template parser """

    tokens = enum('EOF', 'TREE', 'LEAF', 'SUBTREE', 'LABEL', 'LENGTH',
        'SUPPORT', 'ENDSUB', 'ENDTREE')

    def __init__(self, streamer):

        self.streamer = streamer
        self.token = None
        self.token_buffer = bytearray()
        self.state = self.lex_tree

    def buffer(self, char):
        """ Adds a streamed character to the token buffer """
        self.token_buffer.append(ord(char))

    def eat_spaces(self):
        while self.streamer.peek().isspace():
            next(self.streamer)

    def emit(self, item):
        """ Emits the token buffer's contents as a token; clears the buffer """
        self.token = item
        self.empty_buffer()

    def empty_buffer(self):
        """ Clears the token buffer (python 2 has no bytearray.clear()
        method )"""
        self.token_buffer = self.token_buffer[0:0]

    def __iter__(self):
        return self

    def next(self):
        """ Python 2.x / 3.x compatibility hack """
        return self.__next__()

    def __next__(self):
        """ Each iteration returns a token. While a token isn't ready,
        advance the state machine one state. """
        while not self.token:
            self.state = self.state()
        token, self.token = self.token, None
        return token

    def pos(self):
        """ Returns position in input stream
        """
        return self.streamer.stream.tell()

    def stop(self):
        raise StopIteration

    def truncated_string(self, s, length=60, ellipsis='...'):
        """ Returns a string `s` truncated to maximum length `length`.
        If `s` is longer than `length` it is truncated and `ellipsis` is
        appended to the end. The ellipsis is included in the length.
        If `s` is shorter than `length` `s` is returned unchanged.
        """
        l = length - len(ellipsis)
        return s[:l] + (s[l:] and ellipsis)

    def lex_tree(self):
        for x in self.streamer:
            if x == '(':
                break

        if self.streamer.isclosed():
            self.emit(Item(self.tokens.EOF, -1))
            return self.stop

        self.emit(Item(self.tokens.TREE, ''))
        return self.lex_subtree_start

    def lex_subtree_start(self):
        self.eat_spaces()
        char = self.streamer.peek()

        if char == '(':
            self.emit(Item(self.tokens.SUBTREE, next(self.streamer)))
            return self.lex_subtree_start

        else:
            self.emit(Item(self.tokens.LEAF, None))
            return self.lex_label

    def lex_label(self):
        self.eat_spaces()
        char = self.streamer.peek()
        if char in ('"', "'"):
            next(self.streamer) # throw away opening quote
            self._match_delimited(char)
        else:
            despacer = {' ': '_'}
            self._match_run(str.isalnum, accepted_chars='-_|.',
                denied_chars=':,;', replacements=despacer)
        self.emit(Item(self.tokens.LABEL, self.token_buffer.decode()))

        return self.lex_length

    def lex_length(self):
        char = self.streamer.peek()
        if char == ':':
            self.streamer.next() # throw away colon
            self._match_number()
            if len(self.token_buffer) == 0:
                num = None
            else:
                num = float(self.token_buffer)
        else:
            num = None
        self.emit(Item(self.tokens.LENGTH, num))
        return self.lex_subtree_end

    def lex_subtree_end(self):
        self.eat_spaces()
        char = self.streamer.peek()

        if char == ';':
            next(self.streamer)
            self.emit(Item(self.tokens.ENDTREE, ';'))
            return self.lex_tree

        elif char == ',':
            next(self.streamer)
            return self.lex_subtree_start

        elif char == ')':
            next(self.streamer)
            self.emit(Item(self.tokens.ENDSUB, ')'))
            peek = self.streamer.peek() # is a label or a support value next?
            if peek.isdigit() or peek == '.':
                return self.lex_support
            return self.lex_label

        else:
            raise LexError('Don\'t know how to lex this: {0} ({1})'.format(
                char, self.streamer.stream.tell()))

    def lex_support(self):
        self._match_number()
        if len(self.token_buffer) == 0:
            num = 0.0
        else:
            num = float(self.token_buffer)
        self.emit(Item(self.tokens.SUPPORT, num))
        return self.lex_length

    def _match_delimited(self, delimiter):
        pos = self.pos() - 2 # stream is 2 chars ahead of the opening delimiter
        for char in self.streamer:
            if char == delimiter:
                return
            self.buffer(char)

        buf = self.truncated_string(self.token_buffer.decode())
        msg = ''.join((
            'Unterminated {0}-delimited string starting at '.format(delimiter),
            'position {0}:\n{1}{2}'.format(pos, delimiter, buf)
            ))
        raise LexError(msg)

    def _match(self, predicate, accepted_chars='', denied_chars='',
        replacements=None):
        """
        Checks next character in stream. If predicate returns True, or char
        is in `accepted_chars`, advances the stream and returns 1. Else, or if
        the char is in `denied_chars`, doesn't advance the stream and returns 0.
        Replacements is an optional dictionary that can be used to replace the
        streamed character with an alternative (e.g. replace spaces with
        underscores).
        """

        replacements = (replacements or dict())
        char = self.streamer.peek()
        char = replacements.get(char, char)

        if predicate(char) or char in accepted_chars:
            if len(char) == 1:
                self.buffer(char)
            next(self.streamer) # advance stream
            return 1
        elif char in denied_chars:
            return 0
        else:
            return 0

    def _match_run(self, predicate, **kwargs):
        """
        kwargs are `accepted_chars`, `denied_chars` and `replacements`
        """
        nchars = 0
        try:
            while True:
                matched = self._match(predicate, **kwargs)
                nchars += matched
                if matched == 0:
                    return nchars
        except StopIteration:
            raise LexError('Unexpected end of stream')

    def _match_number(self):
        digits = 0
        self._match(lambda x: False, '-+')
        digits += self._match_run(str.isdigit)
        if self._match(lambda x: False, '.'):
            digits += self._match_run(str.isdigit)

        if digits > 0:
            if self._match(lambda x: False, 'eE'):
                self._match(lambda x: False, '-+')
                self._match_run(str.isdigit)

        else:
            self.empty_buffer()


class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = lexer.tokens
        self.trees = list()
        self.stack = list() # top value is the node to add new siblings of
            # the current subtree. Below is the same for previous subtrees

    @classmethod
    def parse_from_file(cls, filename, **kwargs):
        f = open(filename)
        s = Streamer(f)
        l = Lexer(s)
        parser = cls(l)
        try:
            parser.parse(**kwargs)
        except ParseError as err:
            print('Not parsed due to ParseError')
            print(err)
        if not s.isclosed(): # expect it to be closed on reaching EOF
            s.stream.close() # but make explicit check here anyway
        if len(parser.trees) == 1:
            return parser.trees[0]
        return parser.trees

    @classmethod
    def parse_from_string(cls, s, **kwargs):
        s = Streamer(s)
        l = Lexer(s)
        parser = cls(l)
        try:
            parser.parse(**kwargs)
        except ParseError as err:
            print('Not parsed due to ParseError')
            print(err)
        if not s.isclosed(): # expect it to be closed on reaching EOF
            s.stream.close() # but make explicit check here anyway
        if len(parser.trees) == 1:
            return parser.trees[0]
        return parser.trees

    def _get_data(self):
        """
        Get the node data attributes 'label' and 'length'. Assumes these will
        be the next tokens in the stream. Throws ParseError if they are not.
        """
        label = next(self.lexer)
        if label.typ not in (self.tokens.LABEL, self.tokens.SUPPORT):
            raise ParseError(
                'Expected a label or a support value, found {0}'.format(
                    label))

        length = next(self.lexer)
        if length.typ != self.tokens.LENGTH:
            raise ParseError('Expected a length, found {0}'.format(
                length))

        return (label.val, length.val)

    def _add(self):
        if len(self.stack) == 0:
            raise ParseError('No nodes in stack')
        bud = Node(Data(None))
        new = Node(Data(None))
        self.stack[-1].add_next(bud)
        self.stack[-1] = bud
        bud.add_out(new, None)
        return new

    def add_leaf(self, label, length):
        leaf = self._add()
        leaf.data.label = label
        leaf.set_length(length)

    def add_subtree(self):
        subtree = self._add()
        self.stack.append(subtree)

    def close_subtree(self, label, length):
        subtree = self.stack.pop()
        if isinstance(label, float):
            subtree.data.add_attribute('support', label)
        else:
            subtree.data.label = label
        subtree.next.set_length(length)

    def parse(self, allow_duplicates=False):
        seen_leaves = list()
        for token in self.lexer:
            if token.typ == self.tokens.EOF:
                return

            elif token.typ == self.tokens.TREE:
                seed = Node(Data(None))
                self.trees.append(Tree(seed))
                self.stack.append(seed)

            elif token.typ == self.tokens.SUBTREE:
                self.add_subtree()

            elif token.typ == self.tokens.LEAF:
                label, length = self._get_data()
                self.add_leaf(label, length)
                if label:
                    if label in seen_leaves and not allow_duplicates:
                        raise ParseError(
                            'Multiple leaves with the same label: {0}'.format(
                                label))
                    else:
                        seen_leaves.append(label)
                    self.trees[-1].add_taxon(label)

            elif token.typ == self.tokens.ENDSUB:
                label, length = self._get_data()
                self.close_subtree(label, length)

            # labels and lengths should always be dealt with by LEAF and ENDSUB
            # cases, and should not be seen here - ParseError is raised
            elif token.typ == self.tokens.LABEL:
                raise ParseError('Unexpected label token')

            elif token.typ == self.tokens.LENGTH:
                raise ParseError('Unexpected length token')

            elif token.typ == self.tokens.SUPPORT:
                raise ParseError('Unexpected support token')

            elif token.typ == self.tokens.ENDTREE: # trigger for tree-finalising functions
                self.trees[-1].map_taxa_to_binary()


class Tree(object):
    """ Container type for nodes in a tree """

    def __init__(self, node):
        self.seed = node
        self.taxa = list()
        self.taxonmap = dict()

    def add_taxon(self, taxon):
        bisect.insort(self.taxa, taxon)

    def __str__(self):
        return str(self.seed) + ';'

    def minsplit(self, s):
        alt = s ^ self.bitmask
        return min(s, alt)

    def calc_splits(self, relist=False):
        if relist:
            self.relist_taxa()
        for n in self.postorder():

            if n.out is None:
                return

            if n.isleaf():
                taxon = n.data.label
                split = self.taxonmap[taxon]
                n.data.attributes['split'] = split

            n.out.data.attributes['split'] = self.minsplit(
                n.data.attributes['split'] ^ n.out.data.attributes.get(
                    'split', 0))

    def relist_taxa(self):
        self.taxa[:] = list() # clears list
        for n in self.preorder():
            lab = n.data.label
            if n.isleaf() and lab:
                self.add_taxon(lab)
        self.map_taxa_to_binary()

    def map_taxa_to_binary(self):
        self.bitmask = (1 << len(self.taxa)) - 1
        d = dict((taxon, self.minsplit(1 << self.taxa.index(taxon)))
                    for taxon in self.taxa)
        self.taxonmap = d

    def preorder(self):
        return self.seed.preorder_generator()

    def postorder(self):
        return self.seed.postorder_generator()

    def levelorder(self):
        return self.seed.levelorder_generator()


class Node(object):

    reg = re.compile(r'\W') # matches anything that's NOT a-z, A-Z, 0-9 or _

    def __init__(self, data):
        self.data = data
        self.length = 0
        self.prev = None
        self.next = None
        self.back = None
        self.out = None

    def __str__(self):
        label = self.data.label
        if self.reg.search(label):
            label = '"{0}"'.format(label) # quote non-alphanumeric labels
        length = self.length
        if self.isleaf():
            return label + (':'+str(length) if length else '')
        subtree = ','.join(str(ch) for ch in self.children_generator())
        return '({0}){1}{2}'.format(subtree, label,
            (':'+str(length) if length else ''))

    def __repr__(self):
        if not self.data.label is None:
            return 'Node(Data(\'{0}\'))'.format(self.data.label)
        return 'Node(Data({0}))'.format(self.data.label)

    def add_next(self, node):
        node.data = self.data
        if self.next is None:
            self.prev, node.prev = self.next, node.next = node, self
        else:
            following = self.next
            following.prev, node.prev = node, self
            self.next, node.next = node, following

    def detach(self):
        if self.next is None:
            return self
        self.prev.next, self.next.prev = self.next, self.prev
        self.prev, self.next = None, None
        return self

    def add_out(self, node, length):
        (self.out, node.out) = (node, self)
        self.length = node.length = length

    def set_length(self, length):
        self.length = length
        if self.out:
            self.out.length = length

    def isleaf(self):
        return self.next == None

    def preorder_generator(self):

        yield self
        for n in self.loop():
            for val in n.out.preorder_generator():
                yield val

    def postorder_generator(self):

        for n in self.loop():
            for val in n.out.postorder_generator():
                yield val
        yield self

    def levelorder_generator(self):
        q = Queue()
        q.enqueue(self)
        while q:
            node = q.dequeue()
            yield node
            for n in node.loop():
                q.enqueue(n.out)

    def loop(self):
        n = self.next
        if n is None:
            n = self
        while n != self:
            yield n
            n = n.next

    def children_generator(self):
        for n in self.loop():
            yield n.out


class Data(object):

    def __init__(self, label):
        self.label = label
        self.attributes = {'split': 0}

    def add_attribute(self, key, value):
        self.attributes[key] = value


class Queue(object):

    def __init__(self):
        self.queue = collections.deque()

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.queue)

    def next(self):
        """ Python 2.x / 3.x compatibility hack """
        return self.__next__()

    def __next__(self):
        if self.isempty():
            raise StopIteration
        return self.dequeue()

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if self.isempty():
            raise Exception('empty queue')
        return self.queue.popleft()

    def isempty(self):
        return len(self.queue) == 0


class _NodeNamer():
    """
    debugging class
    """

    def __init__(self):
        self.n = 1
        self.d = dict()
    def add(self,node):
        if not node in self.d:
            self.d[node] = str(self.n)
            self.n += 1
    def get(self,node):
        if not node in self.d:
            self.add(node)
        return self.d[node]