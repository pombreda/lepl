
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

from lepl.support.lib import format

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
        return format('{0}({1}, {2}, {3}, {4})', self.__class__.__name__, 
                      self.function, self.factory, self.args, self.kargs)
        
    def __str__(self):
        return format('{0}({1})', self.factory.__name__,
                      ', '.join(list(map(repr, self.args)) +
                               [format('{0}={1!r}', key, self.kargs[key])
                                for key in self.kargs]))
        
