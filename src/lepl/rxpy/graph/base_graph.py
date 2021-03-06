#LICENCE

'''
Base classes for the graph of opcodes used to represent a regular expression.
'''

from lepl.rxpy.graph.support import edge_iterator
from lepl.rxpy.support import RxpyError
from lepl.support.lib import unimplemented


class AutoClone(object):
    '''
    Support automatic cloning for subclasses that follow the conventions:
    - Constructors take named arguments
    - Public attributes map to named arguments
    - The "fixed" attribute contains names of attributes that should be ignored
    '''

    def __init__(self, fixed=None):
        if fixed is None:
            fixed = []
        self.fixed = set(fixed)

    def clone(self):
        '''
        Duplicate this node (necessary when replacing a numbered repeat with
        explicit, repeated, instances, for example).

        This copies all "public" attributes as constructor kargs.
        '''
        try:
            return self.__class__(**self._kargs())
        except TypeError as e:
            raise RxpyError('Error cloning {0}: {1}'.format(self.__class__.__name__, e))

    def _kargs(self):
        '''
        Generate a list of arguments used for cloning.  Subclasses can
        over-ride this if necessary, but probably shouldn't (instead, they
        should have attributes that correspond to kargs).
        '''
        return dict((name, getattr(self, name))
                     for name in self.__dict__
                     if not name.startswith('_') and name not in self.fixed)


class BaseNode(AutoClone):
    '''
    Subclasses are nodes in a graph that describes a regular expression.  They
    are also "opcodes", or ordered actions, (typically, matches) that must be
    made when matching the input.

    Nodes accessible from this instance (ie opcodes for following operations)
    are visible in `.next`.

    For automatic cloning, subclasses should have a public attribute for each
    constructor karg (and no additional public attributes).  Note that graph
    nodes are not exposed as part of the public API - they are purely internal
    to the graph/parser stage.
    '''

    def __init__(self, consumes=None, size=None):
        '''
        Subclasses should pay attention to the relationship between
        constructor kargs and attributes assumed in `.clone()`.

        `consumes` - a tri-state flag indicating whether this node consumes
        input (None means unknown).  This is used to detect non-consuming
        loops (see `consumer()`).

        `size` - the amount of input consumed (None means unknown).
        '''
        # cloning comes before assembly; other values are fixed by
        # constructors or derived from other input
        super(BaseNode, self).__init__(fixed=['next', 'consumes', 'size', 'fixed'])
        if consumes is None or size is None:
            assert consumes is size, 'Inconsistent uncertainty'
        self.next = []
        self.consumes = consumes
        self.size = size

    def consumer(self, lenient):
        '''
        Does this node consume data from the input string?  This is used to
        detect errors (if False, repeating with * or + would not terminate)
        during *assembly* and, as such, relies on container classes to
        inspect contents.

        `lenient` - the default value if behaviour is unknown (so when lenient,
        uncertain nodes consume; when conservative uncertain nodes do not).
        '''
        if self.consumes is None:
            return lenient
        else:
            return self.consumes

    def length(self, groups, known=None):
        '''
        The number of characters matched by this and subsequent nodes, if
        known, otherwise None.  Nodes must give a single, fixed number or
        None, so any loops should return None.  This is used at *runtime*
        when some groups are known.

        `groups` - current groups.

        `known` - a set of visited nodes, used to detect loops.
        '''
        if known is None:
            known = set()
        if len(self.next) == 1 and self not in known and self.size is not None:
            known.add(self)
            other = self.next[0].length(groups, known)
            if other is not None:
                return self.size + other

    def __repr__(self):
        '''
        Generate a description of this node and accessible children which can
        be used to plot the graph in GraphViz.
        '''
        indices = {}
        reverse = {}
        def index(node):
            '''Map from node to index, adding nodes as needed.'''
            if node not in indices:
                n = len(indices)
                indices[node] = n
                reverse[n] = node
            return str(indices[node])
        def escape(node):
            '''Escape text for Graphviz.'''
            text = str(node)
            text = text.replace('\n','\\n')
            return text.replace('\\', '\\\\')
        edge_indices = [(index(start), index(end))
                        for (start, end) in edge_iterator(self)]
        edges = [' ' + start + ' -> ' + end for (start, end) in edge_indices]
        nodes = [' ' + str(index) + ' [label="{0!s}"]'.format(escape(reverse[index]))
                 for index in sorted(reverse)]
        return 'digraph {{\n{0!s}\n{1!s}\n}}'.format(
                        '\n'.join(nodes), '\n'.join(edges))

    @unimplemented
    def __str__(self):
        '''
        Subclasses must implement something useful here, which will be
        displayed in the graphviz node (see repr).
        '''

    #noinspection PyUnusedLocal
    def join(self, final, _state):
        self.next.insert(0, final)
        return self

    def deep_eq(self, other):
        '''
        Recursive equality; used only for testing.
        '''
        for ((a, b), (c, d)) in zip(edge_iterator(self), edge_iterator(other)):
            if not a._node_eq(c) or not b._node_eq(d):
                return False
        return True

    def _node_eq(self, other):
        return type(self) == type(other) and self._kargs() == other._kargs()


class BaseGroupReference(BaseNode):
    '''
    Extra support for nodes that reference groups.
    '''

    def __init__(self, number, **kargs):
        super(BaseGroupReference, self).__init__(**kargs)
        self.number = number

    def resolve(self, state):
        self.number = state.index_for_name_or_count(self.number)


class BaseLabelledNode(BaseNode):
    '''
    A node with a label (used for display).
    '''

    def __init__(self, label, **kargs):
        super(BaseLabelledNode, self).__init__(**kargs)
        self.label = label

    def __str__(self):
        return self.label


class BaseLineNode(BaseNode):
    '''
    A flag that indicates whether multiple lines are possible.
    '''

    def __init__(self, multiline, **kargs):
        super(BaseLineNode, self).__init__(**kargs)
        self.multiline = multiline


class BaseEscapedNode(BaseNode):
    '''
    An escaped character, possible inverted (eg \s, \S).
    '''

    def __init__(self, character, inverted=False, **kargs):
        super(BaseEscapedNode, self).__init__(**kargs)
        self._character = character
        self.inverted = inverted

    def __str__(self):
        return '\\' + (self._character.upper()
                       if self.inverted else self._character.lower())

