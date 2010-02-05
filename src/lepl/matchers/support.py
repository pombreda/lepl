
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
    GraphStr
from lepl.matchers.matcher import Matcher, FactoryMatcher
from lepl.matchers.operators import OperatorMixin, OPERATORS, \
    OperatorNamespace
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
        return self.indented_repr(0)
                      
    def _fmt_repr(self, indent, value, key=None):
        if isinstance(value, Matcher):
            return value.indented_repr(indent, key)
        else:
            return (' ' * indent) + (key + '=' if key else '') + repr(value)
        
    def indented_repr(self, indent0, key=None):
        (args, kargs) = self._constructor_args()
        compact = len(args) + len(kargs) < 2
        indent1 = 0 if compact else indent0 + 1 
        contents = [self._fmt_repr(indent1, arg) for arg in args] + \
            [self._fmt_repr(indent1, kargs[key], key) for key in kargs]
        return format('{0}{1}{2}({3}{4})', 
                      ' ' * indent0,
                      key + '=' if key else '',
                      self._small_str,
                      '' if compact else '\n',
                      ',\n'.join(contents))
        
    def _fmt_str(self, value, key=None):
        return (key + '=' if key else '') + \
            value._small_str if isinstance(value, Matcher) else str(value)
    
    def __str__(self):
        (args, kargs) = self._constructor_args()
        contents = [self._fmt_str(arg) for arg in args] + \
            [self._fmt_str(kargs[key], key) for key in kargs]
        return format('{0}({1})', self._small_str,
                      ', '.join(contents))
    
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
    
    def __init__(self, name=OPERATORS, namespace=OperatorNamespace):
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


class FactoryWrapper(FactoryMatcher, OperatorMatcher):
    
    def __init__(self, *args, **kargs):
        super(FactoryWrapper, self).__init__()
        self._args(args=args)
        self._kargs(kargs)
        

class TrampolineWrapper(FactoryWrapper):
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
    

class TransformableFactoryWrapper(FactoryMatcher, Transformable):
    
    def __init__(self, *args, **kargs):
        super(TransformableFactoryWrapper, self).__init__()
        self._args(args=args)
        self._kargs(kargs=kargs)
        
    def compose(self, transform):
        copy = type(self)(*self.args, **self.kargs)
        copy.factory = self.factory
        copy.function = self.function.compose(transform.function)
        return copy
        

class SequenceWrapper(TransformableFactoryWrapper):
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
 

class FunctionWrapper(TransformableFactoryWrapper):
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


def make_wrapper_factory(wrapper, factory):
    def wrapper_factory(*args, **kargs):
        made = wrapper(*args, **kargs)
        made.factory = factory
        return made
    wrapper_factory.factory = factory
    return wrapper_factory


def make_factory(maker, matcher):
    def factory(*args, **kargs):
        if args or kargs:
            raise TypeError(format('{0}() takes no arguments', 
                                   matcher.__name__))
        return matcher
    factory.__name__ = matcher.__name__
    factory.__doc__ = matcher.__doc__
    return maker(factory)


def trampoline_matcher_factory(factory):
    return make_wrapper_factory(TrampolineWrapper, factory)

def trampoline_matcher(matcher):
    return make_factory(trampoline_matcher_factory, matcher)

def sequence_matcher_factory(factory):
    return make_wrapper_factory(SequenceWrapper, factory)

def sequence_matcher(matcher):
    return make_factory(sequence_matcher_factory, matcher)

def function_matcher_factory(factory):
    return make_wrapper_factory(FunctionWrapper, factory)

def function_matcher(matcher):
    return make_factory(function_matcher_factory, matcher)


def coerce_(arg, function=None):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    if function is None:
        from lepl.matchers.core import Literal
        function = Literal
    return function(arg) if isinstance(arg, basestring) else arg


