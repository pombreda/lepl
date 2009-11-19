
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
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

from lepl.graph import GraphStr, ConstructorGraphNode, ConstructorWalker
from lepl.support import LogMixin, basestring


def is_named(arg):
    '''
    Is this is "named tuple"?
    '''
    return (isinstance(arg, tuple) or isinstance(arg, list)) \
            and len(arg) == 2 and isinstance(arg[0], basestring)
            

# pylint: disable-msg=R0903
# it's not supposed to have public attributes, because it exposes contents
class Node(LogMixin, ConstructorGraphNode):
    '''
    A base class for AST nodes.

    It is designed to be applied to a list of results, via ``>``.
    '''
    
    def __init__(self, *args):
        '''
        Expects a single list of arguments, as will be received if invoked with
        the ``>`` operator.
        '''
        super(Node, self).__init__()
        self.__postorder = ConstructorWalker(self, Node)
        self.__children = []
        self.__paths = []
        self.__names = set()
        for arg in args:
            if is_named(arg):
                self.__add_named_child(arg[0], arg[1])
            elif isinstance(arg, Node):
                self.__add_named_child(arg.__class__.__name__, arg)
            else:
                self.__add_anon_child(arg)
        
    def __add_named_child(self, name, value):
        '''
        Add a value associated with a name (either a named pair or the class
        of a Node subclass).
        '''
        index = self.__add_attribute(name, value)
        self.__children.append(value)
        self.__paths.append((name, index))
        
    def __add_anon_child(self, value):
        '''
        Add a nameless value.
        '''
        index = len(self.__children)
        self.__children.append(value)
        self.__paths.append(index)
            
    def __add_attribute(self, name, value):
        '''
        Attributes are associated with lists of (named) values.
        '''
        if name not in self.__names:
            self.__names.add(name)
            setattr(self, name, [])
        attr = getattr(self, name)
        index = len(attr)
        attr.append(value)
        return index
        
    def __dir__(self):
        '''
        The names of all the attributes constructed from the results.
        '''
        # this must return a list, not an iterator (Python requirement)
        return list(self.__names)
    
    def __getitem__(self, index):
        return self.__children[index]
    
    def __iter__(self):
        return iter(self.__children)
    
    def __str__(self):
        visitor = NodeTreeStr()
        return self.__postorder(visitor)
    
    def __repr__(self):
        return self.__class__.__name__ + '(...)'
    
    def __len__(self):
        return len(self.__children)
    
    def __bool__(self):
        return bool(self.__children)
    
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

    def _constructor_args(self):
        '''
        Regenerate the constructor arguments (returns (args, kargs)).
        '''
        args = []
        for (path, value) in zip(self.__paths, self.__children):
            if isinstance(path, int):
                args.append(value)
            else:
                name = path[0]
                if name == value.__class__.__name__:
                    args.append(value)
                else:
                    args.append((name, value))
        return (args, {})
    
    
# pylint: disable-msg=R0903
# __ method
class MutableNode(Node):
    '''
    Extend `Node` to allow children to be set.
    '''
    
    def __setitem__(self, index, value):
        self.__children[index] = value
        
        
class NodeTreeStr(GraphStr):
    '''
    Extend `GraphStr` to handle named pairs - this generates an 'ASCII tree'
    representation of the node graph.
    '''
    
    def leaf(self, arg):
        '''
        Leaf nodes are either named or simple values.
        '''
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
                 and isinstance(entry[0], basestring))


def join_with(separator=''):
    '''
    Join results together (via separator.join()) into a single string.
    
    Invoke as ``> join_with(',')``, for example.
    '''
    def fun(results):
        '''
        Delay evaluation.
        '''
        return separator.join(results)
    return fun
    

