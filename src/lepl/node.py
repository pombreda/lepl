
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
Base classes for AST nodes (and associated functions).
'''

from collections import Iterable, Mapping, deque

from lepl.graph import SimpleGraphNode, SimpleWalker, GraphStr, postorder, POSTORDER
from lepl.support import LogMixin


class Node(SimpleGraphNode, LogMixin):
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
        self.__postorder = SimpleWalker(self)
        self.__children = []
        self.__names = []
        for arg in args:
            if isinstance(arg, Node):
                self.__add_attribute(arg.__class__.__name__, arg)
            else:
                try:
                    (name, value) = arg
                    self.__add_attribute(name, value)
                except:
                    pass
            self.__children.append(arg)
#        self._info('{0}'.format(self))
        
    def __add_attribute(self, name, value):
        if name not in self.__names:
            self.__names.append(name)
            setattr(self, name, [])
        getattr(self, name).append(value)
        
    def _children(self):
        return iter(self)
        
    def __dir__(self):
        '''
        The names of all the attributes constructed from the results.
        
        I realise that this may break some assumptions necessary for 
        introspection, but I can't find any other appropriate way to expose
        this information (I want to avoid using a named method as that will
        obscure a similarly named child).
        '''
        return self.__names
    
    def __getitem__(self, index):
        return self.__children[index]
    
    def __iter__(self):
        return iter(self.__children)
    
    def __str__(self):
        visitor = CustomStr()
        return visitor.postprocess(self.__postorder(visitor))
    
    def __repr__(self):
        return self.__class__.__name__ + '(...)'
    
    def __len__(self):
        return len(self.__children)
    

class CustomStr(GraphStr):
    '''
    Extend `GraphStr` to handle named pairs.
    '''
    
    def leaf(self, arg):
        try:
            (name, value) = arg
            return lambda first, rest, name_: \
                [first + name + (' ' if name else '') + repr(value)]
        except Exception as e:
            return super(CustomStr, self).leaf(arg)


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
    def fun(stream_in, stream_out, results):
        return Error(results,
            *_syntax_error_args(msg, stream_in, stream_out, results))
    return fun


def _syntax_error_args(msg, stream_in, stream_out, results):
    '''
    Helper function for constructing format dictionary.
    '''
    try:
        filename = stream_in.source()
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
             'results': results, 'filename': filename, 
             'lineno': lineno, 'offset':offset, 'line':line}
    try:
        return (msg.format(**kargs), (filename, lineno, offset, line))
    except:
        return (msg, (filename, lineno, offset, line))


def raise_error(msg):
    '''
    As `make_error()`, but also raise the result.
    '''
    def fun(stream_in, stream_out, results):
        error = make_error(msg)(stream_in, stream_out, results)
        raise error
    return fun


class Error(Node, SyntaxError):
    '''
    Subclass `Node` and Python's SyntaxError to provide an AST
    node that can be raised as an error via `throw`.
    
    Create with `make_error()`.
    '''
    
    def __init__(self, results, msg, location):
        Node.__init__(self, results)
        SyntaxError.__init__(self, msg, location)
        
    def __str__(self):
        return SyntaxError.__str__(self)


def throw(node):
    '''
    Raise an error, if one exists in the results (AST trees are traversed).
    Otherwise, the results are returned (invoke with ``>>``).
    '''
    for child in postorder(node):
        if isinstance(node, Exception):
            raise node
    return node
        

