
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

from types import GeneratorType

from lepl.core.config import ParserMixin
from lepl.core.parser import tagged, tagged_function, GeneratorWrapper
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
    
    def __str__(self):
        visitor = ConstructorStr()
        return self.postorder(visitor, Matcher)
    
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
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


def to_generator(value):
    '''
    Create a single-shot generator from a value.
    '''
    if value is not None:
        yield value


class UserLayerFacade(OperatorMixin, ArgAsAttributeMixin, 
                      PostorderWalkerMixin, LogMixin, ParserMixin, Matcher):
    
    def __init__(self, pure, factory, args, kargs):
        super(UserLayerFacade, self).__init__(name=OPERATORS, 
                                              namespace=DefaultNamespace)
        self._karg(pure=pure)
        self._karg(factory=factory)
        self._karg(args=args)
        self._karg(kargs=kargs)
        
    def _match(self, stream):
        '''
        The code below is called once and then replaces itself so that the
        same logic is not repeated on any following calls.
        
        We handle both normal functions (pure=True) and generators.
        '''
        matcher = self.factory(*self.args, **self.kargs)
        if self.pure:
            self._match = lambda stream: \
                GeneratorWrapper(to_generator(matcher(self, stream)),
                                 self, stream)
        else:
            self._match = tagged_function(self, matcher)
        return self._match(stream)
    
    def __repr__(self):
        return format('UserLayerFacade({0}, {1}, {2})', 
                      self.factory, self.args, self.kargs)
        
    def __str__(self):
        return self.factory.__name__
        
        
def function_matcher_factory(factory):
    def wrapped_factory(*args, **kargs):
        return UserLayerFacade(True, factory, args, kargs)
    wrapped_factory.factory = factory
    return wrapped_factory


def generator_matcher_factory(factory):
    def wrapped_factory(*args, **kargs):
        return UserLayerFacade(False, factory, args, kargs)
    wrapped_factory.factory = factory
    return wrapped_factory


def coerce_(arg, function=None):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    if function is None:
        from lepl.matchers.core import Literal
        function = Literal
    return function(arg) if isinstance(arg, basestring) else arg


