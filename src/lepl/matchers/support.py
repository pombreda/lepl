
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
Support classes for matchers.
'''

from lepl.core.config import ParserMixin
from lepl.core.parser import tagged_function
from lepl.support.graph import ArgAsAttributeMixin, PostorderWalkerMixin, \
    ConstructorStr, GraphStr
from lepl.matchers.matcher import Matcher, FactoryMatcher
from lepl.matchers.operators import OperatorMixin, OPERATORS, \
    DefaultNamespace
from lepl.support.lib import LogMixin, basestring, format

# pylint: disable-msg=C0103,W0212
# (consistent interfaces)
# pylint: disable-msg=E1101
# (_args create attributes)
# pylint: disable-msg=R0901, R0904, W0142
# lepl conventions


class BaseMatcher(ArgAsAttributeMixin, PostorderWalkerMixin, 
                    LogMixin, Matcher):
    '''
    A base class that provides support to all matchers.
    '''
    
    def __repr__(self):
        visitor = ConstructorStr()
        return self.postorder(visitor, Matcher)
    
    def __str__(self):
        return self.__repr__()
    
    @property
    def kargs(self):
        (_, kargs) = self._constructor_args()
        return kargs
    
    def tree(self):
        '''
        An ASCII tree for display.
        '''
        visitor = GraphStr()
        return self.postorder(visitor)
    


class OperatorMatcher(OperatorMixin, ParserMixin, BaseMatcher):
    '''
    A base class that provides support to all matchers with operators.
    '''
    
    def __init__(self, name=OPERATORS, namespace=DefaultNamespace):
        super(OperatorMatcher, self).__init__(name=name, namespace=namespace)


class Transformable(OperatorMatcher):
    '''
    All subclasses invoke the function attribute on
    (results, stream_in, stream_out) when returning their final value.
    This allows `Transform` instances to be merged directly.
    '''

    def __init__(self, function=None):
        from lepl.matchers.transform import Transformation
        super(Transformable, self).__init__()
        if not isinstance(function, Transformation):
            function = Transformation(function)
        self.function = function

    def compose(self, transform):
        '''
        Combine with a transform, returning a new instance.
        
        We must return a new instance because the same Transformable may 
        occur more than once in a graph and we don't want to include the
        Transform in other cases.
        '''
        raise NotImplementedError()


def to_generator(value):
    '''
    Create a single-shot generator from a value.
    '''
    if value is not None:
        yield value


class _FactoryWrapper(FactoryMatcher, OperatorMatcher):
    
    def __init__(self, factory, *args, **kargs):
        super(_FactoryWrapper, self).__init__()
        self._arg(factory=factory)
        self._args(args=args)
        self._kargs(kargs)
        self._name = factory.__name__
        

class TrampolineWrapper(_FactoryWrapper):
    '''
    A wrapper for source of generators that evaluate other matchers via
    the trampoline (ie for generators that evaluate matchers via yield).
    
    Typically only used for advanced matchers.
    '''
    
    def _match(self, stream):
        '''
        The code below is called once and then replaces itself so that the
        same logic is not repeated on any following calls.
        '''
        matcher = self.factory(*self.args, **self.kargs)
        self._match = tagged_function(self, matcher)
        return self._match(stream)
    

class _TransformableFactoryWrapper(FactoryMatcher, Transformable):
    
    def __init__(self, factory, *args, **kargs):
        super(_TransformableFactoryWrapper, self).__init__(function=None)
        self._arg(factory=factory)
        self._args(args=args)
        self._kargs(kargs=kargs)
        self._name = factory.__name__
        
    def compose(self, transform):
        copy = type(self)(self.factory, *self.args, **self.kargs)
        copy.function = self.function.compose(transform.function)
        return copy
        

class SequenceWrapper(_TransformableFactoryWrapper):
    '''
    A wrapper for simple generator factories, where the final matcher is a
    function that yields a series of matches without evaluating other matchers
    via the trampoline.
    '''
    
    def _match(self, stream):
        '''
        The code below is called once and then replaces itself so that the
        same logic is not repeated on any following calls.
        '''
        matcher0 = self.factory(*self.args, **self.kargs)
        if self.function:
            # if we have a transformation, build a matcher than includes it
            def matcher1(support, stream_in):
                for (results, stream_out) in matcher0(support, stream_in):
                    yield self.function(results, stream_in, stream_out)
        else:
            matcher1 = matcher0
        self._match = tagged_function(self, matcher1)
        return self._match(stream)
 

class FunctionWrapper(_TransformableFactoryWrapper):
    '''
    A wrapper for simple function factories, where the final matcher is a
    function that returns a single match or None.
    '''
    
    def _match(self, stream):
        '''
        The code below is called once and then replaces itself so that the
        same logic is not repeated on any following calls.
        '''
        matcher0 = self.factory(*self.args, **self.kargs)
        if self.function:
            # if we have a transformation, build a matcher than includes it
            def matcher1(support, stream_in):
                try:
                    (results, stream_out) = matcher0(support, stream_in)
                    return self.function(results, stream_in, stream_out)
                except TypeError:
                    return None
        else:
            matcher1 = matcher0
        matcher2 = lambda support, s, m=matcher1: to_generator(m(support, s))
        self._match = tagged_function(self, matcher2)
        return self._match(stream)

        
def trampoline_matcher_factory(factory):
    def wrapped_factory(*args, **kargs):
        return TrampolineWrapper(factory, *args, **kargs)
    wrapped_factory.factory = factory
    return wrapped_factory


def trampoline_matcher(matcher):
    def factory(*args, **kargs):
        if args or kargs:
            raise TypeError(format('{0}() takes no arguments', 
                                   matcher.__name__))
        return matcher
    factory.__name__ = matcher.__name__
    factory.__doc__ = matcher.__doc__
    return trampoline_matcher_factory(factory)


def sequence_matcher_factory(factory):
    def wrapped_factory(*args, **kargs):
        return SequenceWrapper(factory, *args, **kargs)
    wrapped_factory.factory = factory
    return wrapped_factory


def sequence_matcher(matcher):
    def factory(*args, **kargs):
        if args or kargs:
            raise TypeError(format('{0}() takes no arguments', 
                                   matcher.__name__))
        return matcher
    factory.__name__ = matcher.__name__
    factory.__doc__ = matcher.__doc__
    return sequence_matcher_factory(factory)


def function_matcher_factory(factory):
    def wrapped_factory(*args, **kargs):
        return FunctionWrapper(factory, *args, **kargs)
    wrapped_factory.factory = factory
    return wrapped_factory


def function_matcher(matcher):
    def factory(*args, **kargs):
        if args or kargs:
            raise TypeError(format('{0}() takes no arguments', 
                                   matcher.__name__))
        return matcher
    factory.__name__ = matcher.__name__
    factory.__doc__ = matcher.__doc__
    return function_matcher_factory(factory)


def coerce_(arg, function=None):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    if function is None:
        from lepl.matchers.core import Literal
        function = Literal
    return function(arg) if isinstance(arg, basestring) else arg


