
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
A transformation is a function that modifies the result of calling a matcher
once.

From the point of view of a transformation, a matcher is a function that 
takes no arguments and either returns (results, stream_out) or raises a 
StopIteration (note - this is an interface - the way you typically define 
matchers doesn't conform to that interface, but decorators like 
@function_matcher etc do the necessary work to adapt things as necessary).

A transformation takes two arguments - the initial stream and a matcher 
(as described above).  The transformation, when called, should return 
either return a (result, stream_out) pair, or raise a StopIteration.  
A null transformation, therefore, would simply evaluate the matcher it 
receives:
    null_transform = lambda stream, matcher: matcher()
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


class NullTransformation(object):
    
    def __call__(self, _stream, matcher):
        return matcher()
    
    def __bool__(self):
        return False
    
    # Python 2.6
    def __nonzero__(self):
        return self.__bool__()
    

class TransformationWrapper(object):
    '''
    Helper object that composes transformations and also keeps a list of
    the separate transformations for introspection.
    '''
    
    def __init__(self, functions=None):
        '''
        We accept either a list of a functions or a single value.
        '''
        functions = [] if functions is None else functions
        if not isinstance(functions, list):
            functions = [functions]
        self.functions = []
        self.function = NullTransformation()
        self.extend(functions)
        
    def extend(self, functions):
        for function in functions:
            self.append(function)
            
    def append(self, function):
        if self:
            self.function = \
                lambda stream, matcher, f=self.function: \
                    function(stream, lambda: f(stream, matcher))
        else:
            self.function = function
        self.functions.append(function)
        
    def compose(self, wrapper):
        '''
        Apply wrapped transformations to the results of this wrapper.
        '''
        functions = list(self.functions)
        functions.extend(wrapper.functions)
        return TransformationWrapper(functions)

    def precompose(self, wrapper):
        '''
        Insert the transformation before the existing functions.
        '''
        functions = list(wrapper.functions)
        functions.extend(self.functions)
        return TransformationWrapper(functions)
        
    def __str__(self):
        return '<' + ','.join(map(lambda x: x.__name__, self.functions)) + '>'
        
    def __repr__(self):
        return format('TransformationWrapper({0})', self)
    
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
    
    
def raise_(e):
    '''
    Let raise be used as a function.
    '''
    raise e
        

class Transform(Transformable):
    '''
    Apply a function to (stream_in, matcher)

    Typically used via `Apply` and `KApply`.
    '''

    def __init__(self, matcher, function):
        super(Transform, self).__init__(function)
        self._arg(matcher=coerce_(matcher))
        # it's ok that this overwrites the same thing from Transformable
        # (Transformable cannot have an argument because it subclasses
        # OperatorMatcher, and passing in function as a constructor arg
        # is a nightmare).
        if not isinstance(function, TransformationWrapper):
            function = TransformationWrapper(function)
        self._arg(wrapper=function)

    @tagged
    def _match(self, stream_in):
        '''
        Do the matching (return a generator that provides successive
        (result, stream) tuples).
        '''
        function = self.wrapper.function
        generator = self.matcher._match(stream_in)
        while True:
            try:
                results = yield generator
                yield function(stream_in, lambda: results)
            except StopIteration:
                yield function(stream_in, lambda: raise_(StopIteration))
            
        
    def compose(self, function):
        '''
        Create a new Transform that includes the extra processing. 
        '''
        return Transform(self.matcher, self.wrapper.compose(function))
