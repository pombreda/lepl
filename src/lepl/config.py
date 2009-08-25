
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
The main configuration object and various standard configurations.
'''

from lepl.stream import DEFAULT_STREAM_FACTORY

# A major driver for this being separate is that it decouples dependency loops


class Configuration(object):
    '''
    Encapsulate various parameters that describe how the matchers are
    rewritten and evaluated.
    '''
    
    __default = None
    __managed = None
    
    def __init__(self, rewriters=None, monitors=None, stream_factory=None):
        '''
        `rewriters` are functions that take and return a matcher tree.  They
        can add memoisation, restructure the tree, etc.  They are applied left
        to right.
        
        `monitors` are factories that return implementations of `ActiveMonitor`
        or `PassiveMonitor` and will be invoked by `trampoline()`. 
        '''
        self.rewriters = rewriters
        self.monitors = monitors
        if stream_factory is None:
            stream_factory = DEFAULT_STREAM_FACTORY
        self.__stream_factory = stream_factory
        
    @property
    def stream(self):
        '''
        Read only access to the stream factory.
        '''
        return self.__stream_factory
        
    @classmethod    
    def default(cls, config=None):
        '''
        If no config is given, Generate a default configuration instance.  
        Currently this flattens nested `And()` and `Or()` instances;
        adds memoisation (which allows left recursion, but may alter the order 
        in which matches are returned for ambiguous grammars);
        adds a lexer if any tokens are found (assuming unicode input);
        and supports tracing (which is initially disabled, but can be enabled
        using the `Trace()` matcher).
        '''
        if config:
            return config
        if cls.__default is None:
            from lepl.lexer.rewriters import lexer_rewriter
            from lepl.rewriters import flatten, compose_transforms, auto_memoize
            from lepl.trace import TraceResults
            cls.__default = \
                Configuration(
                    rewriters=[flatten, compose_transforms, lexer_rewriter(),
                               auto_memoize()],
                    monitors=[TraceResults(False)])
        return cls.__default
    
    @classmethod
    def managed(cls):
        '''
        Add generator management (no limit, but enables `Commit()`) to the
        default configuration.
        '''
        if cls.__managed is None:
            from lepl.lexer.rewriters import lexer_rewriter
            from lepl.manager import GeneratorManager
            from lepl.rewriters import flatten, compose_transforms, auto_memoize
            from lepl.trace import TraceResults
            cls.__managed = \
                Configuration(
                    rewriters=[flatten, compose_transforms, lexer_rewriter(),
                               auto_memoize()],
                    monitors=[TraceResults(False), 
                              GeneratorManager(queue_len=0)])
        return cls.__managed
    
    @classmethod    
    def tokens(cls, alphabet):
        '''
        Tokens for a unicode alphabet are already suppored by the default
        configuration; this allows other alphabets to be supported.
        
        If alphabet is not specified, Unicode is assumed.
        '''
        from lepl.lexer.rewriters import lexer_rewriter
        from lepl.regexp.unicode import UnicodeAlphabet
        from lepl.rewriters import flatten, compose_transforms, auto_memoize
        from lepl.trace import TraceResults
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        return Configuration(
                rewriters=[flatten, compose_transforms,
                           lexer_rewriter(alphabet), auto_memoize()],
                monitors=[TraceResults(False)])
    
    @classmethod
    def nfa(cls, alphabet=None):
        '''
        Rewrite fragments of the matcher graph as regular expressions.
        This uses a pushdown automaton and should return all possible matches.
        
        If alphabet is not specified, Unicode is assumed.
        '''
        from lepl.lexer.rewriters import lexer_rewriter
        from lepl.regexp.rewriters import regexp_rewriter
        from lepl.regexp.unicode import UnicodeAlphabet
        from lepl.rewriters import flatten, compose_transforms, auto_memoize
        from lepl.trace import TraceResults
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        return Configuration(
                rewriters=[flatten, compose_transforms,
                           regexp_rewriter(alphabet, False),
                           compose_transforms, lexer_rewriter(alphabet),
                           auto_memoize()],
                monitors=[TraceResults(False)])
    
    @classmethod
    def dfa(cls, alphabet=None):
        '''
        Rewrite fragments of the matcher graph as regular expressions.
        This uses a finite automaton and returns only the greediest match,
        so may produce changed results with ambiguous parsers.
        
        Note - this assumes that the value being parsed is Unicode text.
        '''
        from lepl.lexer.rewriters import lexer_rewriter
        from lepl.regexp.matchers import DfaRegexp
        from lepl.regexp.rewriters import regexp_rewriter
        from lepl.regexp.unicode import UnicodeAlphabet
        from lepl.rewriters import flatten, compose_transforms, auto_memoize
        from lepl.trace import TraceResults
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        return Configuration(
                rewriters=[flatten, compose_transforms,
                           regexp_rewriter(UnicodeAlphabet.instance(), 
                                           False, DfaRegexp),
                           compose_transforms, lexer_rewriter(alphabet),
                           auto_memoize()],
                monitors=[TraceResults(False)])
    
