
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
Base class for matchers.
'''


from abc import ABCMeta, abstractmethod
from types import FunctionType

from lepl.support.lib import format, singleton, identity

# pylint: disable-msg=C0103, W0105
# Python 2.6
#class Matcher(metaclass=ABCMeta):
_Matcher = ABCMeta('_Matcher', (object, ), {})
'''
ABC used to identify matchers.  

Note that graph traversal assumes subclasses are hashable and iterable.
'''

class Matcher(_Matcher):
    
    def __init__(self):
        self._small_str = self.__class__.__name__
    
#    @abstractmethod 
    def _match(self, stream):
        '''
        This is the core method called during recursive decent.  It must
        yield (stream, results) pairs until the matcher has exhausted all
        possible matches.
        
        To evaluate a sub-matcher it should yield the result of calling
        this method on the sub-matcher:
        
            generator = sub_matcher._match(stream_in)
            try:
                while True:
                    # evaluate the sub-matcher
                    (stream_out, result) = yield generator
                    ....
                    # return the result from this matcher
                    yield (stream_out, result)
            except StopIteration:
                ...
                
        The implementation should be decorated with @tagged in almost all
        cases.
        '''

#    @abstractmethod
    def indented_repr(self, indent, key=None):
        '''
        Called by repr; should recursively call contents.
        '''
        

# Python 2.6
#class FactoryMatcher(metaclass=ABCMeta):
_FactoryMatcher = ABCMeta('_FactoryMatcher', (object, ), {})
'''
ABC used to identify factory matchers (have a property factory that 
identifies the matcher they generate).
'''


class FactoryMatcher(_FactoryMatcher):
    '''
    Imagine an abstract property called 'factory' below.
    '''


class MatcherTypeException(Exception):
    '''
    Used to flag problems related to matcher types.
    '''
    
def raiseException(msg):
    raise MatcherTypeException(msg)


def case_type(matcher, if_factory, if_matcher):
    if isinstance(matcher, FunctionType) and hasattr(matcher, 'factory'):
        return if_factory(matcher.factory)
    elif issubclass(matcher, Matcher):
        return if_matcher(matcher)
    else:
        raise MatcherTypeException(
            format('{0} does not appear to be a matcher type', matcher))


def case_instance(matcher, if_wrapper, if_matcher):
    from lepl.matchers.support import FactoryMatcher
    try:
        if isinstance(matcher, FactoryMatcher):
            return if_wrapper(matcher.factory)
    except TypeError:
        pass # bug in python impl
    if isinstance(matcher, Matcher):
        return if_matcher(matcher)
    else:
        raise MatcherTypeException(
            format('{0} does not appear to be a matcher', matcher))


def matcher_type(matcher):
    return case_type(matcher, identity, identity)

def matcher_instance(matcher):
    return case_instance(matcher, identity, identity)


class Relations(object):
    
    def __init__(self, base):
        self.base = base
        self.factories = set()
        
    def add_child(self, child):
        return case_type(child,
                         lambda m: self.factories.add(m),
                         lambda m: self.base.register(m))
        
    def child_of(self, child):
        return case_instance(child, 
                             lambda m: m is self.base or m in self.factories,
                             lambda m: isinstance(self.base, type) 
                             and isinstance(m, self.base))
        

def relations(base):
    # if base is a factory then we want the related type
    try:
        base = matcher_type(base)
    except MatcherTypeException:
        pass
    table = singleton(Relations, dict)
    if base not in table:
        table[base] = Relations(base)
    return table[base]
    

def is_child(child, base, fail=True):
    try:
        return relations(base).child_of(child)
    except MatcherTypeException as e:
        if fail:
            raise e
        else:
            return False

def add_child(base, child):
    relations(base).add_child(child)

def add_children(base, *children):
    for child in children:
        add_child(base, child)
        