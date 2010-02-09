
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

from inspect import getargspec

from lepl.core.config import ParserMixin
from lepl.core.parser import tagged_function, GeneratorWrapper, tagged
from lepl.support.graph import ArgAsAttributeMixin, PostorderWalkerMixin, \
    GraphStr
from lepl.matchers.matcher import Matcher, FactoryMatcher, add_child, is_child
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
        return self._indented_repr(0, set())
                      
    def _fmt_repr(self, indent, value, visited, key=None):
        prefix = (' ' * indent) + (key + '=' if key else '')
        if is_child(value, Matcher, fail=False):
            if value in visited:
                return prefix + '[' + value._small_str + ']'
            else:
                return value._indented_repr(indent, visited, key)
        else:
            return prefix + repr(value)
        
    def _format_repr(self, indent, key, contents):
        return format('{0}{1}{2}({3}{4})', 
                      ' ' * indent,
                      key + '=' if key else '',
                      self._small_str,
                      '' if self._fmt_compact else '\n',
                      ',\n'.join(contents))
        
    def _indented_repr(self, indent0, visited, key=None):
        visited.add(self)
        (args, kargs) = self._constructor_args()
        indent1 = 0 if self._fmt_compact else indent0 + 1 
        contents = [self._fmt_repr(indent1, arg, visited) for arg in args] + \
            [self._fmt_repr(indent1, kargs[key], visited, key) for key in kargs]
        return self._format_repr(indent0, key, contents)
        
    @property
    def _fmt_compact(self):
        (args, kargs) = self._constructor_args()
        if len(args) + len(kargs) > 1:
            return False
        for arg in args:
            try:
                if not arg._fmt_compact:
                    return False
            except AttributeError:
                pass
        for arg in kargs:
            try:
                if not arg._fmt_compact:
                    return False
            except AttributeError:
                pass
        return True
        
    def _fmt_str(self, value, key=None):
        return (key + '=' if key else '') + \
            value._small_str if isinstance(value, Matcher) else repr(value)
    
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

    def _format_repr(self, indent, key, contents):
        return format('{0}{1}{2}:{3}({4}{5})', 
                      ' ' * indent,
                      key + '=' if key else '',
                      self._small_str,
                      self.function,
                      '' if self._fmt_compact else '\n',
                      ',\n'.join(contents))
        

class BaseFactoryMatcher(FactoryMatcher):
    '''
    This must be used as a mixin with something that inherits from 
    ArgsAsAttribute (ie the usual matcher classes).
    '''
    
    def __init__(self, *args, **kargs):
        super(FactoryMatcher, self).__init__()
        self.__args = args
        self.__kargs = kargs
        self.__factory = None
        self.__small_str = None
        self.__cached_matcher = None
        
    def __args_as_attributes(self):
        spec = getargspec(self.factory)
        names = list(spec.args)
        defaults = dict(zip(names[::-1], spec.defaults if spec.defaults else []))
        for name in names:
            if name in self.__kargs:
                self._karg(**{name: self.__kargs[name]})
                del self.__kargs[name]
            elif self.__args:
                self._arg(**{name: self.__args[0]})
                self.__args = self.__args[1:]
            else:
                if name not in defaults:
                    self._warn(format('No value for argument {0} in {1}', 
                                      name, self._small_str))
        if self.__args:
            if spec.varargs:
                self._args(**{spec.varargs: self.__args})
            else:
                self._warn(format('No *args parameter for {0} in {1}',
                                  self.__args, self._small_str))
        if self.__kargs:
            if spec.varkw:
                self.__kargs(**{spec.varkw: self.__kargs})
            else:
                self._warn(format('No **kargs parameter for {0} in {1}',
                                  self.__kargs, self._small_str))
        
    @property
    def factory(self):
        return self.__factory
    
    @factory.setter
    def factory(self, factory):
        if not self.__factory:
            assert factory
            self.__factory = factory
            self._small_str = self.__small_str if self.__small_str else factory.__name__
            self.__args_as_attributes()

    def _format_repr(self, indent, key, contents):
        return format('{0}{1}{2}<{3}>({4}{5})', 
                      ' ' * indent, 
                      key + '=' if key else '',
                      self.__class__.__name__,
                      self._small_str,
                      '' if self._fmt_compact else '\n',
                      ',\n'.join(contents))
        
    @property
    def _cached_matcher(self):
        if not self.__cached_matcher:
            (args, kargs) = self._constructor_args()
            self.__cached_matcher = self.factory(*args, **kargs)
        return self.__cached_matcher
        
        
def to_generator(value):
    '''
    Create a single-shot generator from a value.
    '''
    if value is not None:
        yield value


class TrampolineWrapper(BaseFactoryMatcher, OperatorMatcher):
    '''
    A wrapper for source of generators that evaluate other matchers via
    the trampoline (ie for generators that evaluate matchers via yield).
    
    Typically only used for advanced matchers.
    '''
    
    @tagged
    def _match(self, stream):
        generator = self._cached_matcher(self, stream)
        try:
            value = next(generator)
            while True:
                if type(value) is GeneratorWrapper:
                    try:
                        response = yield value
                        value = generator.send(response)
                    except StopIteration as e:
                        value = generator.throw(e)
                else:
                    yield value
                    value = next(generator)
        except StopIteration:
            pass
    

class TransformableWrapper(BaseFactoryMatcher, Transformable):
    
    def compose(self, transform):
        (args, kargs) = self._constructor_args()
        copy = type(self)(*args, **kargs)
        copy.factory = self.factory
        copy.function = self.function.compose(transform.function)
        return copy
    
    def _format_repr(self, indent, key, contents):
        return format('{0}{1}{2}<{3}:{4}>({5}{6})', 
                      ' ' * indent, 
                      key + '=' if key else '',
                      self.__class__.__name__,
                      self._small_str,
                      self.function,
                      '' if self._fmt_compact else '\n',
                      ',\n'.join(contents))
        

class TransformableTrampolineWrapper(TransformableWrapper):
    '''
    A wrapper for source of generators that evaluate other matchers via
    the trampoline (ie for generators that evaluate matchers via yield).
    
    Typically only used for advanced matchers.
    '''
    
    @tagged
    def _match(self, stream_in):
        generator = self._cached_matcher(self, stream_in)
        try:
            value = next(generator)
            while True:
                if type(value) is GeneratorWrapper:
                    try:
                        response = yield value
                        value = generator.send(response)
                    except StopIteration as e:
                        value = generator.throw(e)
                else:
                    (results, stream_out) = value
                    yield self.function(results, stream_in, stream_out)
                    value = next(generator)
        except StopIteration:
            pass
    
    
class NoTrampolineTransformableWrapper(TransformableWrapper):
    pass


class SequenceWrapper(NoTrampolineTransformableWrapper):
    '''
    A wrapper for simple generator factories, where the final matcher is a
    function that yields a series of matches without evaluating other matchers
    via the trampoline.
    '''
    
    @tagged
    def _match(self, stream_in):
        for (results, stream_out) in self._cached_matcher(self, stream_in):
            yield self.function(results, stream_in, stream_out)
 

class FunctionWrapper(NoTrampolineTransformableWrapper):
    '''
    A wrapper for simple function factories, where the final matcher is a
    function that returns a single match or None.
    '''
    
    @tagged
    def _match(self, stream_in):
        try:
            (results, stream_out) = self._cached_matcher(self, stream_in)
            yield self.function(results, stream_in, stream_out)
        except TypeError:
            pass


def make_wrapper_factory(wrapper, factory):
    def wrapper_factory(*args, **kargs):
        made = wrapper(*args, **kargs)
        made.factory = factory
        return made
    wrapper_factory.factory = factory
    add_child(Matcher, wrapper_factory)
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


def trampoline_matcher_factory(transformable=True):
    def wrapper(factory):
        if transformable:
            return make_wrapper_factory(TransformableTrampolineWrapper, factory)
        else:
            return make_wrapper_factory(TrampolineWrapper, factory)
    return wrapper

def trampoline_matcher(transformable=True):
    def wrapper(matcher):
        return make_factory(trampoline_matcher_factory(transformable), matcher)
    return wrapper

def sequence_matcher_factory(factory):
    from lepl.matchers.memo import NoMemo
    wrapper = make_wrapper_factory(SequenceWrapper, factory)
    add_child(NoMemo, wrapper)
    return wrapper

def sequence_matcher(matcher):
    return make_factory(sequence_matcher_factory, matcher)

def function_matcher_factory(factory):
    from lepl.matchers.memo import NoMemo
    wrapper = make_wrapper_factory(FunctionWrapper, factory)
    add_child(NoMemo, wrapper)
    return wrapper

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


