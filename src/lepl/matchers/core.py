
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
Matchers that embody fundamental, common actions.
'''

# pylint: disable-msg=C0103,W0212
# (consistent interfaces)
# pylint: disable-msg=E1101
# (_args create attributes)
# pylint: disable-msg=R0901, R0904, W0142
# lepl conventions

from re import compile as compile_

from lepl.core.parser import tagged
from lepl.matchers.support import OperatorMatcher, coerce_, \
    function_matcher_factory
from lepl.matchers.transform import Transformable
from lepl.support.lib import format


@function_matcher_factory
def Any(restrict=None):
    '''
    Create a matcher for a single character.
    
    :Parameters:
    
      restrict (optional)
        A list of tokens (or a string of suitable characters).  
        If omitted any single token is accepted.  
        
        **Note:** This argument is *not* a sub-matcher.
    '''
    warned = [False]

    def match(support, stream):
        '''
        Do the matching.  The result will be a single matchingcharacter.
        '''
        ok = bool(stream)
        if ok and restrict:
            try:
                ok = stream[0] in restrict
            except TypeError:
                # it would be nice to make this an error, but for line aware
                # parsing (and any other heterogenous input) it's legal
                if not warned[0]:
                    support._debug(format('Cannot restrict {0} with {1!r}',
                                          stream[0], restrict))
                    warned[0] = True
        if ok:
            return ([stream[0]], stream[1:])
            
    return match
            
            
class Literal(Transformable):
    '''
    Match a series of tokens in the stream (**''**).
    '''
    
    def __init__(self, text):
        '''
        Typically the argument is a string but a list might be appropriate 
        with some streams.
        '''
        super(Literal, self).__init__()
        self._arg(text=text)
        self.tag(repr(text))
    
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).

        Need to be careful here to use only the restricted functionality
        provided by the stream interface.
        '''
        try:
            if self.text == stream[0:len(self.text)]:
                yield self.function([self.text], stream, 
                                    stream[len(self.text):])
        except IndexError:
            pass
        
    def compose(self, transform):
        '''
        Generate a new instance with the composed function from the Transform.
        '''
        copy = Literal(self.text)
        copy.function = self.function.compose(transform.function)
        return copy
        
        
class Empty(OperatorMatcher):
    '''
    Match any stream, consumes no input, and returns nothing.
    '''
    
    def __init__(self, name=None):
        super(Empty, self).__init__()
        self._karg(name=name)
        if name:
            self.tag(name)
    
    # pylint: disable-msg=R0201
    # keep things consistent for future subclasses
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  Match any character and progress to 
        the next.
        '''
        yield ([], stream)
        
        
class Lookahead(OperatorMatcher):
    '''
    Tests to see if the embedded matcher *could* match, but does not do the
    matching.  On success an empty list (ie no result) and the original
    stream are returned.
    
    When negated (preceded by ~) the behaviour is reversed - success occurs
    only if the embedded matcher would fail to match.
    
    This is a consumer because it's correct functioning depends directly on
    the stream's contents.
    '''
    
    def __init__(self, matcher, negated=False):
        '''
        On success, no input is consumed.
        If negated, this will succeed if the matcher fails.  If the matcher is
        a string it is coerced to a literal match.
        '''
        super(Lookahead, self).__init__()
        self._arg(matcher=coerce_(matcher))
        self._karg(negated=negated)
        if negated:
            self.tag('~')
    
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            yield self.matcher._match(stream) # an evaluation, not a return
            success = True
        except StopIteration:
            success = False
        if success is self.negated:
            return
        else:
            yield ([], stream)
            
    def __invert__(self):
        '''
        Invert the semantics (this overrides the usual meaning for ~).
        '''
        return Lookahead(self.matcher, negated=not self.negated)
            

class Regexp(OperatorMatcher):
    '''
    Match a regular expression.  If groups are defined, they are returned
    as results.  Otherwise, the entire expression is returned.
    '''
    
    def __init__(self, pattern):
        '''
        If the pattern contains groups, they are returned as separate results,
        otherwise the whole match is returned.
        
        :Parameters:
        
          pattern
            The regular expression to match. 
        '''
        super(Regexp, self).__init__()
        self._arg(pattern=pattern)
        self.tag(repr(pattern))
        self.__pattern = compile_(pattern)
        
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            match = self.__pattern.match(stream.text)
        except AttributeError: # no text method
            match = self.__pattern.match(stream)
        if match:
            eaten = len(match.group())
            if match.groups():
                yield (list(match.groups()), stream[eaten:])
            else:
                yield ([match.group()], stream[eaten:])
            
            
class Delayed(OperatorMatcher):
    '''
    A placeholder that allows forward references (**+=**).  Before use a 
    matcher must be assigned via '+='.
    '''
    
    def __init__(self, matcher=None):
        '''
        Introduce the matcher.  It can be defined later with '+='
        '''
        super(Delayed, self).__init__()
        self._karg(matcher=matcher)
    
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        if self.matcher:
            return self.matcher._match(stream)
        else:
            raise ValueError('Delayed matcher still unbound.')
        
    # pylint: disable-msg=E0203, W0201
    # _karg defined this in constructor
    def __iadd__(self, matcher):
        if self.matcher:
            raise ValueError('Delayed matcher already bound.')
        else:
            self.matcher = coerce_(matcher)
            return self
        

class Eof(OperatorMatcher):
    '''
    Match the end of a stream.  Returns nothing.  

    This is also aliased to Eos in lepl.derived.
    '''

    def __init__(self):
        super(Eof, self).__init__()

    # pylint: disable-msg=R0201
    # consistent for subclasses
    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        if not stream:
            yield ([], stream)
            
            
class Consumer(OperatorMatcher):
    '''
    Only accept the match if it consumes data from the input
    '''

    def __init__(self, matcher, consume=True):
        '''
        If consume is False, accept when no data is consumed.  
        '''
        super(Consumer, self).__init__()
        self._arg(matcher=coerce_(matcher))
        self._karg(consume=consume)
    
    @tagged
    def _match(self, stream_in):
        '''
        Do the match and test whether the stream has progressed.
        '''
        try:
            generator = self.matcher._match(stream_in)
            while True:
                (result, stream_out) = yield generator
                if self.consume == (stream_in != stream_out):
                    yield (result, stream_out)
        except StopIteration:
            pass
        
        
    