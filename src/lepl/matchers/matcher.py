
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

from lepl.support.lib import format, singleton

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
        self._name = self.__class__.__name__
    
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

# Python 2.6
#class FactoryMatcher(metaclass=ABCMeta):
_FactoryMatcher = ABCMeta('_FactoryMatcher', (object, ), {})
'''
ABC used to identify factory matchers (have a property factory that 
identifies the matcher they generate).
'''


class FactoryMatcher(_FactoryMatcher):
    
    def __init__(self, *args, **kargs):
        super(FactoryMatcher, self).__init__(*args, **kargs)

    def __repr__(self):
        return format('{0}({1}, {2}, {3})', self.__class__.__name__, 
                      self.factory, self.args, self.kargs)
        
    def __str__(self):
        return format('{0}({1})', self.factory.__name__,
                      ', '.join(list(map(repr, self.args)) +
                               [format('{0}={1!r}', key, self.kargs[key])
                                for key in self.kargs]))
        

class Relations(object):
    
    def __init__(self, base):
        self.base = base
        self.factories = set()
        
    def add_factory(self, child):
        self.factories.add(child.factory)
        
    def child_of(self, child):
        if isinstance(child, FactoryMatcher):
            return child.factory in self.factories
        else:
            return isinstance(child, self.base)
    
        
def is_child(child, base):
    relations = singleton(base, lambda: Relations(base))
    return relations.child_of(child)

def add_child(base, child):
    relations = singleton(base, lambda: Relations(base))
    if isinstance(child, FunctionType) and hasattr(child, 'factory'):
        relations.add_factory(child)
    elif isinstance(base, ABCMeta) and isinstance(child, type):
        relations.base.register(child)
    else:
        raise Exception(format('Cannot add {0} to {1}', child, base))

def add_children(base, *children):
    for child in children:
        add_child(base, child)
        