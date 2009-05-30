
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

from traceback import print_exc
from collections import Iterable, Mapping, deque

from lepl.graph import SimpleWalker, GraphStr, POSTORDER
from lepl.support import LogMixin


def is_named(arg):
    '''
    Is this is "named tuple"?
    '''
    return (isinstance(arg, tuple) or isinstance(arg, list)) \
            and len(arg) == 2 and isinstance(arg[0], str)
            

def dispatch(arg, value=None, node=None, named=None):
    '''
    Process `Node` arguments in a uniform manner.
    
    `Node` can take constructor arguments in a variety of forms:
      - subclasses of Node - these are "child nodes", named by class
      - value - a simple value
      - (name, value) - a named value
      
    This function allows processing of an argument without having to unpack
    those different forms to access the subclass or value arguments.
    When called it matches the argument can calls either value or node
    directly (without any name).  They are called as follows:
      - value for any value, named or not
      - node for any sub-node
      - named called for named values, after value, with (name, value)
    '''
    if is_named(arg):
        if value:
            arg = (arg[0], value(arg[1]))
        if named:
            named(arg[0], arg[1])
    else:
        if isinstance(arg, Node):
            if node:
                arg = node(arg)
            if named:
                named(arg.__class__.__name__, arg)
        else:
            if value:
                arg = value(arg)
    return arg


class Node(LogMixin):
    '''
    A base class for AST nodes.
    
    This is a container that combines named and indexed (integer) lookup.
    Integer indexing accesses all contents in order; named attributes give
    access to either (1) subclasses of Node by class name or (2) named
    pairs of values (name, value).  In both cases the attribute is a list
    (since there may be more than one value with that name in the given
    args).  So all arguments can be accessed by [index], but only certain
    kinds can be accessed as attributes. 
    
    It is designed to be applied to a list of results, via ``>``.
    '''
    
    def __init__(self, args, value=None, node=None):
        '''
        Expects a single list of arguments, as will be received if invoked with
        the ``>`` operator.
        '''
        super(Node, self).__init__()
        self.__postorder = SimpleWalker(self, Node)
        self._children = []
        self._names = []
        for arg in args:
            self._children.append(
                    dispatch(arg, value, node, self.__add_attribute))
            
    def __add_attribute(self, name, value):
        if name not in self._names:
            self._names.append(name)
            setattr(self, name, [])
        getattr(self, name).append(value)
        
    def __dir__(self):
        '''
        The names of all the attributes constructed from the results.
        '''
        return self._names
    
    def __getitem__(self, index):
        return self._children[index]
    
    def __iter__(self):
        return iter(self._children)
    
    def __str__(self):
        visitor = NodeTreeStr()
        return visitor.postprocess(self.__postorder(visitor))
    
    def __repr__(self):
        return self.__class__.__name__ + '(...)'
    
    def __len__(self):
        return len(self._children)
    
    def __bool__(self):
        return bool(self._children)
    
    # Python 2.6
    def __nonzero__(self):
        return self.__bool__()
    
    def __eq__(self, other):
        '''
        Note that eq compares contents, but hash uses object identity.
        '''
        try:
            siblings = iter(other)
        except TypeError:
            return False
        for child in self:
            try:
                if child != next(siblings):
                    return False
            except StopIteration:
                return False
        try:
            next(siblings)
            return False
        except StopIteration:
            return True
        
    def __hash__(self):
        '''
        Note that eq compares contents, but hash uses object identity.
        '''
        return super(Node, self).__hash__()

    
class MutableNode(Node):
    '''
    Extend `Node` to allow children to be set.
    '''
    
    def __setitem__(self, index, value):
        self._children[index] = value
    

class NodeTreeStr(GraphStr):
    '''
    Extend `GraphStr` to handle named pairs - this generates an 'ASCII tree'
    representation of the node graph.
    '''
    
    def leaf(self, arg):
        if is_named(arg):
            return lambda first, rest, name_: \
                    [first + arg[0] + (' ' if arg[0] else '') + repr(arg[1])]
        else:
            return super(NodeTreeStr, self).leaf(arg)


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
    

