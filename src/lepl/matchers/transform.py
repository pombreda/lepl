
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
Matchers that process results.
'''


# pylint: disable-msg=C0103,W0212
# (consistent interfaces)
# pylint: disable-msg=E1101
# (_args create attributes)
# pylint: disable-msg=R0901, R0904, W0142
# lepl conventions

from abc import ABCMeta

from lepl.core.parser import tagged
from lepl.matchers.support import Transformable, coerce_
from lepl.support.lib import format, str
from lepl.support.node import Node


# pylint: disable-msg=W0105
# Python 2.6
#class ApplyRaw(metaclass=ABCMeta):
ApplyRaw = ABCMeta('ApplyRaw', (object, ), {})
'''
ABC used to control `Apply`, so that the result is not wrapped in a list.  
'''


# Python 2.6
#class ApplyArgs(metaclass=ABCMeta):
ApplyArgs = ABCMeta('ApplyArgs', (object, ), {})
'''
ABC used to control `Apply`, so that the results list is supplied as "*args".  
'''

ApplyArgs.register(Node)



class Transformation(object):
    '''
    A transformation is a wrapper for a series of functions that are applied
    to a result. 
    
    A function takes three arguments (results, stream_in, stream_out)
    and returns the tuple (results, stream_out).
    '''
    
    def __init__(self, functions=None):
        '''
        We accept wither a list of a functions or a single value.
        '''
        functions = [] if functions is None else functions
        if not isinstance(functions, list):
            functions = [functions]
        self.functions = functions
        
    def compose(self, transformation):
        '''
        Apply transformation to the results of this function.
        '''
        functions = list(self.functions)
        functions.extend(transformation.functions)
        if functions == self.functions:
            return self
        else:
            return Transformation(functions)

    def precompose(self, transformation):
        '''
        Insert the transformation before the existing functions.
        '''
        functions = list(transformation.functions)
        functions.extend(self.functions)
        if functions == self.functions:
            return self
        else:
            return Transformation(functions)
        
    def __call__(self, results, stream_in, stream_out):
        for function in self.functions:
            (results, stream_out) = function(results, stream_in, stream_out)
        return (results, stream_out)
        
    def __str__(self):
        return str(self.functions)
        
    def __repr__(self):
        return format('Transformation({0!r})', self.functions)
    
    def __bool__(self):
        return bool(self.functions)
    
    # Python 2.6
    def __nonzero__(self):
        return self.__bool__()
    
    def __iter__(self):
        '''
        Co-operate with graph routines.
        '''
        return iter([])
        

class Transform(Transformable):
    '''
    Apply a function to (result, stream_in, stream_out)

    Typically used via `Apply` and `KApply`.
    '''

    def __init__(self, matcher, function):
        super(Transform, self).__init__(function)
        self._arg(matcher=coerce_(matcher))
        # it's ok that this overwrites the same thing from Transformable
        # (Transformable cannot have an argument because it is subclass to
        # matcher without explicit functions)
        if not isinstance(function, Transformation):
            function = Transformation(function)
        self._arg(function=function)

    @tagged
    def _match(self, stream_in):
        '''
        Do the matching (return a generator that provides successive
        (result, stream) tuples).
        '''
        try:
            generator = self.matcher._match(stream_in)
            while True:
                (results, stream_out) = yield generator
                yield self.function(results, stream_in, stream_out)
        except StopIteration:
            pass
        
    def compose(self, transform):
        '''
        Create a new Transform that includes the extra processing. 
        '''
        return Transform(self.matcher, 
                         self.function.compose(transform.function))
