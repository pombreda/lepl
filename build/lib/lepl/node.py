
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Support for structuring results.
'''

from collections import deque

from lepl.trace import LogMixin


class Node(LogMixin):
    '''
    A base class for AST nodes.  This is designed to be applied to a list of 
    results, via ``>``.  If the list contains labelled pairs ``(str, value)`` 
    then these are added as (list) attributes; similarly for Node subclasses.
    '''
    
    def __init__(self, args):
        '''
        Expects a single list of arguments, as will be received if invoked with
        the ``>`` operator.
        '''
        super(Node, self).__init__()
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
        
    def __dir__(self):
        '''
        The names of all the attributes constructed from the results.
        
        I realise that this may break some assumptions necessary for 
        introspection, but I can't find any other appropriate way to expose
        this information (I want to avoid using a named method as that will
        obscure a similarly named child).
        '''
        return list(self.__named_args.keys())
    
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
        
    def __len__(self):
        return len(self.__args)


def make_dict(contents):
    '''
    Construct a dict from a list of named pairs (other values in the list
    will be discarded).  Invoke with ``>`` after creating named pairs with
    ``> string``.
    '''
    return dict(entry for entry in contents
                 if isinstance(entry, tuple) 
                 and len(entry) == 2
                 and isinstance(entry[0], str))


def join_with(separator=''):
    '''
    Join results together (via separator.join()) into a single string.
    
    Invoke as ``> join_with(',')``, for example.
    '''
    def fun(results):
        return separator.join(results)
    return fun
    

def make_error(msg):
    '''
    Create an error node using a format string.
    
    Invoke as ``** make_error('bad results: {results}')``, for example.
    '''
    def fun(stream_in, stream_out, core, results):
        return Error(results,
            *_syntax_error_args(msg, stream_in, stream_out, core, results))
    return fun


def _syntax_error_args(msg, stream_in, stream_out, core, results):
    '''
    Helper function for constructing format dictionary.
    '''
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
    '''
    As `lepl.node.make_error()`, but also raise the result.
    '''
    def fun(stream_in, stream_out, core, results):
        error = make_error(msg)(stream_in, stream_out, core, results)
        raise error
    return fun


class Error(Node, SyntaxError):
    '''
    Subclass `lepl.node.Node` and Python's SyntaxError to provide an AST
    node that can be raised as an error via `lepl.node.throw`.
    
    Create with `lepl.node.make_error()`.
    '''
    
    def __init__(self, results, msg, location):
        Node.__init__(self, results)
        SyntaxError.__init__(self, msg, location)
        
    def __str__(self):
        return SyntaxError.__str__(self)


class AstWalker():
    '''
    A tree walker base class.  Override one or more of ``_before``, ``_visit``
    or ``_after``.
    '''
    
    def __init__(self, dfs=True):
        '''
        By default, the traversal is depth-first.  Set ``dfs`` to ``False`` for
        breadth-first.  
        '''
        self.__queue = None
        self.__dfs = dfs
    
    def __call__(self, root):
        '''
        Traverse the given tree (which may be a list or `lepl.node.Node`).
        '''
        self._before(root)
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

    def _before(self, node):
        '''Called before each node (and its children).'''
        pass
    
    def _visit(self, node):
        '''Called for each node.'''
        pass

    def _after(self, root):
        '''Called after each node (and its children).'''
        return root


class RaiseError(AstWalker):
    '''
    A tree walker that raises the first node it finds that subclasses
    ``Exception``.
    '''
    
    def _visit(self, node):
        if isinstance(node, Exception):
            raise node

def throw(node):
    '''
    Raise an error, if one exists in the results (AST trees are traversed).
    Otherwise, the results are returned (so to avoid problems with extra lists,
    invoke with ``>>``).
    '''
    return RaiseError()(node)

