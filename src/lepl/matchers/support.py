
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
from lepl.matchers.matcher import Matcher
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


class FacadeMixin(object):
    
    def __init__(self, factory, args, kargs, *_args, **_kargs):
        super(FacadeMixin, self).__init__(*_args, **_kargs)
        self._karg(factory=factory)
        self._karg(args=args)
        self._karg(kargs=kargs)
        self._name = factory.__name__
        
    def __repr__(self):
        return format('{0}({1}, {2}, {3})', self.__class__.__name__, 
                      self.factory, self.args, self.kargs)
        
    def __str__(self):
        return format('{0}({1})', self.factory.__name__,
                      ', '.join(list(map(repr, self.args)) +
                               [format('{0}={1!r}', key, self.kargs[key])
                                for key in self.kargs]))
        

class GeneratorFacade(FacadeMixin, OperatorMatcher):
    
    def _match(self, stream):
        '''
        The code below is called once and then replaces itself so that the
        same logic is not repeated on any following calls.
        '''
        matcher = self.factory(*self.args, **self.kargs)
        self._match = tagged_function(self, matcher)
        return self._match(stream)


class FunctionFacade(FacadeMixin, Transformable):
    
    def __init__(self, factory, args, kargs, function=None):
        super(FunctionFacade, self).__init__(factory, args, kargs, function)
    
    def _match(self, stream):
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

    def compose(self, transform):
        return FunctionFacade(self.factory, self.args, self.kargs,
                              self.function.compose(transform.function))
        
        
def function_matcher_factory(factory):
    def wrapped_factory(*args, **kargs):
        return FunctionFacade(factory, args, kargs)
    wrapped_factory.factory = factory
    return wrapped_factory


def function_matcher(matcher):
    def factory():
        return matcher
    factory.__name__ = matcher.__name__
    return function_matcher_factory(factory)


def generator_matcher_factory(factory):
    def wrapped_factory(*args, **kargs):
        return GeneratorFacade(factory, args, kargs)
    wrapped_factory.factory = factory
    return wrapped_factory


def generator_matcher(matcher):
    def factory():
        return matcher
    factory.__name__ = matcher.__name__
    return generator_matcher_factory(factory)


def coerce_(arg, function=None):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    if function is None:
        from lepl.matchers.core import Literal
        function = Literal
    return function(arg) if isinstance(arg, basestring) else arg


