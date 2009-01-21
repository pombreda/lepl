
from collections import Iterable, Mapping, deque

from lepl.trace import LogMixin

'''
A base class for AST nodes.  This is designed to be applied to a list of 
results, via ">".  If the list contains labelled pairs "(str, value)" then
these are added as (list) attributes; similarly for Node subclasses.
'''

class Node(LogMixin):
    
    def __init__(self, args):
        super().__init__()
        self.__args = args
        self.__named_args = {}
        for arg in args:
            try:
                if isinstance(arg, Node):
                    name = arg.__class__.__name__
                    value = arg
                else:
                    (name, value) = arg
                if name not in self.__named_args:
                    self.__named_args[name] = []
                self.__named_args[name].append(value)
            except:
                pass
        self._info('{0}'.format(self))
    
    def __getattr__(self, name):
        if name in self.__named_args:
            return self.__named_args[name]
        else:
            raise KeyError(name)
        
    def __getitem__(self, index):
        return self.__args[index]
    
    def __iter__(self):
        return iter(self.__args)
    
    def __str__(self):
        return '\n'.join(self._node_str('', ' '))
    
    def __repr__(self):
        return self.__class__.__name__ + '(...)'
    
    def _node_str(self, first, rest):
        args = [[rest + '+- ', rest + '|   ', arg] for arg in self.__args]
        args[-1][0] = rest + '`- '
        args[-1][1] = rest + '    '
        lines = [first + self.__class__.__name__]
        for (f, r, a) in args:
            lines += self.__arg_str(f, r, a)
        return lines
    
    def __arg_str(self, first, rest, arg):
        try:
            if isinstance(arg, Node):
                return arg._node_str(first, rest)
            else:
                (name, value) = arg
                return [first + name + ' ' + repr(value)]
        except:
            return [first + repr(arg)]


def make_dict(contents):
    return dict(entry for entry in contents
                 if isinstance(entry, tuple) 
                 and len(entry) == 2
                 and isinstance(entry[0], str))


def join_with(separator=''):
    def fun(results):
        return separator.join(results)
    return fun
    

def make_error(msg):
    def fun(stream_in, stream_out, core, results):
        return Error(results,
            *_syntax_error_args(msg, stream_in, stream_out, core, results))
    return fun


def _syntax_error_args(msg, stream_in, stream_out, core, results):
    try:
        filename = core.source
        (lineno, offset) = stream_in.location()
        offset += 1 # appears to be 1-based?
        line = stream_in.line()
    except:
        filename = '<unknown> - use stream for better error reporting'
        lineno = -1
        offset = -1
        try:
            line = '...' + stream_in
        except:
            line = ['...'] + stream_in
    kargs = {'stream_in': stream_in, 'stream_out': stream_out, 
             'core': core, 'results': results, 'filename': filename, 
             'lineno': lineno, 'offset':offset, 'line':line}
    try:
        return (msg.format(**kargs), (filename, lineno, offset, line))
    except:
        return (msg, (filename, lineno, offset, line))


def raise_error(msg):
    def fun(stream_in, stream_out, core, results):
        error = make_error(msg)(stream_in, stream_out, core, results)
        raise error
    return fun


class Error(Node, SyntaxError):
    
    def __init__(self, results, msg, location):
        Node.__init__(self, results)
        SyntaxError.__init__(self, msg, location)


class AstWalker():
    
    def __init__(self, dfs=True):
        self.__queue = None
        self.__dfs = dfs
    
    def __call__(self, root):
        print(root)
        self._before()
        self.__queue = deque()
        self.__queue.append(root)
        while self.__queue:
            node = self.__queue.pop() if self.__dfs else self.__queue.popleft()
            self._visit(node)
            # avoid strings, maps too...
            if isinstance(node, Node) or isinstance(node, list):
                for child in node:
                    self.__queue.append(child)
        return self._after(root)

    def _before(self):
        pass
    
    def _visit(self, node):
        pass

    def _after(self, root):
        return root


class RaiseError(AstWalker):
    
    def _visit(self, node):
        if isinstance(node, Exception):
            raise node

def throw(node):
     RaiseError()(node)
