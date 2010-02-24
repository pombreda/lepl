
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
Matchers that call the regular expression engine.

These are used internally for rewriting; users typically use `Regexp` which
calls the standard Python regular expression library (and so is faster).
'''

from lepl.matchers.support import Transformable
from lepl.matchers.transform import raise_
from lepl.core.parser import tagged
from lepl.regexp.core import Compiler
from lepl.regexp.unicode import UnicodeAlphabet


# pylint: disable-msg=R0904, R0901, E1101
# lepl convention
class BaseRegexp(Transformable):
    '''
    Common code for all matchers.
    '''
    
    # pylint: disable-msg=E1101
    # (using _arg to set attributes)
    def __init__(self, regexp, alphabet=None):
        super(BaseRegexp, self).__init__()
        self._arg(regexp=regexp)
        self._karg(alphabet=alphabet)
        self.tag(regexp)
        
    def compose(self, wrapper):
        '''
        Implement the Transformable interface.
        '''
        copy = type(self)(self.regexp, self.alphabet)
        copy.wrapper = self.wrapper.compose(wrapper)
        return copy
    
    def precompose(self, wrapper):
        '''
        Like compose, but does the given transformation first.
        '''
        copy = type(self)(self.regexp, self.alphabet)
        copy.wrapper = self.wrapper.precompose(wrapper)
        return copy
    

class NfaRegexp(BaseRegexp):
    '''
    A matcher for NFA-based regular expressions.  This will yield alternative
    matches.
    
    This doesn't suffer from the same limitations as `Regexp` (it can "see"
    all the input data, if necessary), but currently has quite basic syntax 
    and no grouping (the syntax may improve, but grouping will not be added - 
    use LEPL itself for complex problems).
    '''
    
    def __init__(self, regexp, alphabet=None):
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        super(NfaRegexp, self).__init__(regexp, alphabet)
        self.__cached_matcher = None
        
    def _compile(self):
        '''
        Compile the matcher.
        '''
        if self.__cached_matcher is None:
            self.__cached_matcher = \
                    Compiler.single(self.alphabet, self.regexp).nfa().match
        return self.__cached_matcher

    @tagged
    def _match(self, stream_in):
        '''
        Actually do the work of matching.
        '''
        function = self.wrapper.function
        matches = self._compile()(stream_in)
        for (_terminal, match, stream_out) in matches:
            yield function(stream_in, lambda: ([match], stream_out)) \
                if function else [match]
        while True:
            yield function(stream_in, lambda: raise_(StopIteration))

        

class DfaRegexp(BaseRegexp):
    '''
    A matcher for DFA-based regular expressions.  This yields a single greedy
    match.
    
    Typically used only in specialised situations (see `Regexp`).
    '''
    
    def __init__(self, regexp, alphabet=None):
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        super(DfaRegexp, self).__init__(regexp, alphabet)
        self.__cached_matcher = None

    def _compile(self):
        '''
        Compile the matcher.
        '''
        if self.__cached_matcher is None:
            self.__cached_matcher = \
                    Compiler.single(self.alphabet, self.regexp).dfa().match
        return self.__cached_matcher

    @tagged
    def _match(self, stream_in):
        '''
        Actually do the work of matching.
        '''
        function = self.wrapper.function
        match = self._compile()(stream_in)
        if match is not None:
            (_terminals, match, stream_out) = match
            yield function(stream_in, lambda: ([match], stream_out)) \
                if function else [match]
        while True:
            yield function(stream_in, lambda: raise_(StopIteration))

