
from collections import Sequence


class GraphNodeMixin(object):
    '''
    Allow the construction and traversal of a graph of objects.  There is
    assumed to be a close relationship between constructor arguments and
    children - exactly how is deferred to implementations (there is a
    somewhat implicit link between Python object constructors and type 
    constructors in, say, Haskell).
    '''

    def __init__(self):
        super(GraphNodeMixin, self).__init__()
        
    def _children(self, type_=None):
        '''
        Return all children, in order.
        '''
        raise Exception('Not implemented')
    
    def _constructor_args(self):
        '''
        Regenerate the constructor arguments (returns (args, kargs)).
        '''
        raise Exception('Not implemented')


class GraphWalkerMixin(object):
    '''
    Add a 'walk' method.
    '''
    
    def __init__(self):
        super(GraphWalkerMixin, self).__init__()
        self._walker = None
        
    def walk(self, visitor):
        if self._walker is None:
            self._walker = Walker(self)
        return self._walker(visitor)


class ArgAsAttributeMixin(GraphNodeMixin):
    '''
    Constructor arguments are stored as attributes; their names are also
    stored in order so that the arguments can be constructed.  This assumes
    that all names are unique.  '*args' are named "without the *".
    '''
    
    def __init__(self):
        super(ArgAsAttributeMixin, self).__init__()
        self.__arg_names = []
# Don't set these by default because subclasses have other ideas, which means
# they get empty args and kargs atributes. 
#        self._args(args=args)
#        self._kargs(kargs)

    def __arg_as_attribute(self, name, value):
        '''
        Add a single argument as a simple property.
        '''
        setattr(self, name, value)
        return name
            
    def _arg(self, **kargs):
        '''
        Set a single named argument as an attribute (the signature uses kargs
        so that the name does not need to be quoted).  The attribute name is
        added to self.__arg_names.
        '''
        assert len(kargs) == 1
        for name in kargs:
            self.__arg_names.append(self.__arg_as_attribute(name, kargs[name]))
        
    def _kargs(self, kargs):
        '''
        Set **kargs as attributes.  The attribute names are added to 
        self.__arg_names.
        '''
        for name in kargs:
            self.__arg_names.append(self.__arg_as_attribute(name, kargs[name]))
        
    def _args(self, **kargs):
        '''
        Set *arg as an attribute (the signature uses kars so that the 
        attribute name does not need to be quoted).  The name (without '*')
        is added to self.__arg_names.
        '''
        assert len(kargs) == 1
        for name in kargs:
            assert isinstance(kargs[name], Sequence), kargs[name] 
            self.__arg_names.append('*' + self.__arg_as_attribute(name, kargs[name]))
        
    def _constructor_args(self):
        '''
        Regenerate the constructor arguments.
        '''
        args = []
        kargs = {}
        for name in self.__arg_names:
            if name.startswith('*'):
                args.extend(getattr(self, name[1:]))
            else:
                kargs[name] = getattr(self, name)
        return (args, kargs)
    
    def _children(self, type_=None):
        '''
        Return all children, in order.
        '''
        for name in self.__arg_names:
            if name.startswith('*'):
                for arg in getattr(self, name[1:]):
                    if type_ is None or isinstance(arg, type_):
                        yield arg
            else:
                arg = getattr(self, name)
                if type_ is None or isinstance(arg, type_):
                        yield arg


class NamedAttributeMixin(GraphNodeMixin):
    '''
    Constructor arguments are stored as attributes with arbitrary names and 
    reconstructed as simple *args (no **kargs support).  Because the same 
    name may occur more than once, attributes are lists.  For reconstruction
    the args are also stored internally.  An arg with a name of 'None' is
    stored internally, but not set as an attribute. 
    '''
    
    def __init__(self):
        super(NamedAttributeMixin, self).__init__()
        self._args = []
        self._names = set()

    def _arg(self, name, value):
        '''
        Add a single argument as a named attribute.
        '''
        self._add_attribute(name, value)
        self._args.append(value)
        
    def _add_attribute(self, name, value):
        '''
        Add the attribute (as a list).
        '''
        if name:
            if name not in self._names:
                self._names.add(name)
                setattr(self, name, [])
            getattr(self, name).append(value)
            
    def _constructor_args(self):
        '''
        Regenerate the constructor arguments.
        '''
        return (self._args, {})
    
    def _children(self, type_=None):
        '''
        Return all children, in order.
        '''
        for arg in self._args:
            if type_ is None or isinstance(arg, type_):
                yield arg


class Visitor(object):
    '''
    The interface required by the Walker.
    
    'loop' is value returned when a node is re-visited.
    
    'type_' is set with the node type before node() is called.  This
    allows node() itself to be invoked with the Python arguments used to
    construct the original graph.
    '''
    
    def __init__(self):
        self.type_ = None
        self.loop = None
        
    def node(self, *args, **kargs):
        '''
        Called for node instances.  The args and kargs are the values for
        the corresponding child nodes, as returned by this visitor.
        '''
        pass
    
    def arg(self, value):
        '''
        Called for children that are not node instances.
        '''
        pass
    

FORWARD = 1
BACKWARD = 2
NONTREE = 4
ROOT = 8
    
def dfs_edges(node, type_=GraphNodeMixin):
    '''
    Iterative DFS, based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    
    Returns forward and reverse edges.  Also returns root node in correct 
    order for pre- (FORWARD) and post- (BACKWARD) ordering. 
    '''
    stack = [(node, node._children())]
    yield node, node, ROOT | FORWARD
    visited = set([node])
    while stack:
        parent, children = stack[-1]
        try:
            child = next(children)
            if isinstance(child, type_):
                if child in visited:
                    yield parent, child, NONTREE
                else:
                    yield parent, child, FORWARD
                    visited.add(child)
                    stack.append((child, child._children()))
        except StopIteration:
            stack.pop()
            if stack:
                yield stack[-1][0], parent, BACKWARD
    yield node, node, ROOT | BACKWARD
    

def order(node, flag, type_=GraphNodeMixin):
    for parent, child, direction in dfs_edges(node, type_):
        if direction & flag:
            yield child


def preorder(node, type_=GraphNodeMixin):
    return order(node, FORWARD, type_)


def postorder(node, type_=GraphNodeMixin):
    return order(node, BACKWARD, type_)


class Walker(object):
    '''
    (Post order) Depth first tree walker (it handles cyclic graphs by ignoring 
    repeated nodes).
    
    Some processes require bottom-up and then top-down processing.  This can
    be achieved by applying this walker (bottom-up) to return functions which
    are then evaluated top-down.  See the GraphStr visitor for an example.
    
    This is based directly on the catamorphism of the graph.  The visitor 
    encodes the type information.  It may help to see the constructor 
    arguments as type constructors.
    '''
    
    def __init__(self, root):
        self.__root = root
        
    def __call__(self, visitor):
        results = {}
        for node in order(self.__root, BACKWARD | NONTREE):
            visitor.type_ = type(node)
            (args, kargs) = self.__arguments(node, visitor, results)
            results[node] = visitor.node(*args, **kargs)
        return results[self.__root]
    
    def __arguments(self, node, visitor, results):
        (old_args, old_kargs) = node._constructor_args()
        (new_args, new_kargs) = ([], {})
        for arg in old_args:
            new_args.append(self.__value(arg, visitor, results))
        for name in old_kargs:
            new_kargs[name] = self.__value(old_kargs[name], visitor, results)
        return (new_args, new_kargs)
    
    def __value(self, node, visitor, results):
        if isinstance(node, GraphNodeMixin):
            if node in results:
                return results[node]
            else:
                return visitor.loop
        else:
            return visitor.arg(node)
        
                
class ConstructorStr(Visitor):
    '''
    Reconstruct the constructors used to generate the graph as a string
    (useful for repr).
    '''
    
    def __init__(self, line_length=80):
        super(ConstructorStr, self).__init__()
        self.loop = [[0, '<loop>']]
        self.__line_length = line_length
    
    def node(self, *args, **kargs):
        contents = []
        for arg in args:
            if contents: contents[-1][1] += ', '
            contents.extend([indent+1, line] for (indent, line) in arg)
        for name in kargs:
            if contents: contents[-1][1] += ', '
            arg = kargs[name]
            contents.append([arg[0][0]+1, name + '=' + arg[0][1]])
            contents.extend([indent+1, line] for (indent, line) in arg[1:])
        lines = [[0, self.type_.__name__ + '(']] + contents
        lines[-1][1] += ')'
        return lines
    
    def arg(self, value):
        return [[0, repr(value)]]

    def postprocess(self, lines):
        '''
        Ugly, bug-prone and completely ad-hoc, but it seems to work....
        '''
        sections = []
        (scan, indent) = (0, -1)
        while scan < len(lines):
            (i, _) = lines[scan]
            if i > indent:
                indent = i
                sections.append((indent, scan))
            elif i < indent:
                (scan, indent) = self.__compress(lines, sections.pop(-1)[1], scan)
            scan = scan + 1
        while sections:
            self.__compress(lines, sections.pop(-1)[1], len(lines))
        return self.__format(lines)
    
    def __compress(self, lines, start, stop):
        try:
            return self.__all_on_one_line(lines, start, stop)
        except:
            return self.__bunch_up(lines, start, stop)
        
    def __bunch_up(self, lines, start, stop):
        (indent, _) = lines[start]
        while start+1 < stop:
            if indent == lines[start][0] and \
                    (start+1 >= stop or indent == lines[start+1][0]) and \
                    (start+2 >= stop or indent == lines[start+2][0]) and \
                    indent + len(lines[start][1]) + len(lines[start+1][1]) < \
                        self.__line_length:
                lines[start][1] += lines[start+1][1]
                del lines[start+1]
                stop -= 1
            else:
                start += 1
        return (stop, indent-1)

    def __all_on_one_line(self, lines, start, stop):
        (indent, text) = lines[start-1]
        size = indent + len(text) 
        for (_, extra) in lines[start:stop]:
            size += len(extra)
            if size > self.__line_length:
                raise Exception('too long')
            text += extra
        lines[start-1] = [indent, text]
        del lines[start:stop]
        return (start-1, indent)

    def __format(self, lines):
        return '\n'.join(' ' * indent + line for (indent, line) in lines)
                
                
class GraphStr(Visitor):
    '''
    Generate an ASCII graph of the nodes.
    '''
    
    def __init__(self):
        super(GraphStr, self).__init__()
        self.loop = lambda first, rest, name: [first + name + ' <loop>']
    
    def node(self, *args, **kargs):
        def fun(first, rest, name, type_=self.type_):
            spec = []
            for arg in args:
                spec.append((' +- ', ' |  ', '', arg))
            for arg in kargs:
                spec.append((' +- ', ' |  ', arg, kargs[arg]))
            if spec:
                spec[-1] = (' `- ', '    ', spec[-1][2], spec[-1][3])
            yield first + name + (' ' if name else '') + type_.__name__
            for (a, b, c, f) in spec:
                for line in f(a, b, c):
                    yield rest + line
        return fun
    
    def arg(self, value):
        return lambda first, rest, name: \
            [first + name + (' ' if name else '') + repr(value)]
    
    def postprocess(self, f):
        return '\n'.join(f('', '', ''))
    
