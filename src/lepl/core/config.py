
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

from lepl.stream.stream import DEFAULT_STREAM_FACTORY

# A major driver for this being separate is that it decouples dependency loops


class ConfigurationError(Exception):
    pass



class Configuration(object):
    '''
    Encapsulate various parameters that describe how the matchers are
    rewritten and evaluated.
    '''
    
    def __init__(self, rewriters=None, monitors=None, stream_factory=None):
        '''
        `rewriters` are functions that take and return a matcher tree.  They
        can add memoisation, restructure the tree, etc.  They are applied left
        to right.
        
        `monitors` are factories that return implementations of `ActiveMonitor`
        or `PassiveMonitor` and will be invoked by `trampoline()`. 
        
        `stream_factory` constructs a stream from the given input.
        '''
        self.rewriters = rewriters
        self.monitors = monitors
        if stream_factory is None:
            stream_factory = DEFAULT_STREAM_FACTORY
        self.stream_factory = stream_factory
        
    

class ConfigBuilder(object):
    
    def __init__(self):
        self.__unused = True
        self.__rewriters = []
        self.__monitors = []
        self.__stream_factory = DEFAULT_STREAM_FACTORY
        self.__alphabet = None
        
    def add_rewriter(self, rewriter):
        self.__unused = False
        self.__rewriters.append(rewriter)
        return self

    def add_monitor(self, monitor):
        self.__unused = False
        self.__monitors.append(monitor)
        return self
    
    def set_stream_factory(self, stream_factory=DEFAULT_STREAM_FACTORY):
        self.__unused = False
        self.__stream_factory = stream_factory
        return self

    @property
    def configuration(self):
        if self.__unused:
            self.default()
        return Configuration(self.__rewriters, self.__monitors, 
                             self.__stream_factory)
    
    @configuration.setter
    def configuration(self, configuration):
        self.__rewriters = list(configuration.rewriters)
        self.__monitors = list(configuration.monitors)
        self.__stream_factory = configuration.stream_factory
    
    @property
    def alphabet(self):
        from lepl.regexp.unicode import UnicodeAlphabet
        if not self.__alphabet:
            self.__alphabet = UnicodeAlphabet.instance()
        return self.__alphabet
    
    @alphabet.setter
    def alphabet(self, alphabet):
        if alphabet:
            if self.__alphabet:
                if self.__alphabet != alphabet:
                    raise ConfigurationError(
                        'Alphabet has changed during configuration '
                        '(perhaps the default was already used?)')
            else:
                self.__alphabet = alphabet
    
    def flatten(self):
        from lepl.core.rewriters import flatten
        return self.add_rewriter(flatten)
        
    def compose_transforms(self):
        from lepl.core.rewriters import compose_transforms
        return self.add_rewriter(compose_transforms)
        
    def optimize_or(self, conservative=True):
        from lepl.core.rewriters import optimize_or
        return self.add_rewriter(optimize_or(conservative))
        
    def lexer(self, alphabet=None, discard=None):
        from lepl.lexer.rewriters import lexer_rewriter
        self.alphabet = alphabet
        return self.add_rewriter(
            lexer_rewriter(alphabet=self.alphabet, discard=discard))
    
    def auto_memoize(self, conservative=None):
        from lepl.core.rewriters import auto_memoize
        return self.add_rewriter(auto_memoize(conservative))
    
    def left_memoize(self):
        from lepl.core.rewriters import memoize
        from lepl.matchers.memo import LMemo
        return self.add_rewriter(memoize(LMemo))
    
    def right_memoize(self):
        from lepl.core.rewriters import memoize
        from lepl.matchers.memo import RMemo
        return self.add_rewriter(memoize(RMemo))
    
    def trace(self, enabled=False):
        from lepl.core.trace import TraceResults
        return self.add_monitor(TraceResults(enabled))
    
    def manage(self, queue_len=0):
        from lepl.core.manager import GeneratorManager
        return self.add_monitor(GeneratorManager(queue_len))
    
    def compile_to_dfa(self, force=False, alphabet=None):
        from lepl.regexp.matchers import DfaRegexp
        from lepl.regexp.rewriters import regexp_rewriter
        self.alphabet = alphabet
        return self.add_rewriter(
                    regexp_rewriter(self.alphabet, force, DfaRegexp))
    
    def compile_to_nfa(self, force=False, alphabet=None):
        from lepl.regexp.matchers import NfaRegexp
        from lepl.regexp.rewriters import regexp_rewriter
        self.alphabet = alphabet
        return self.add_rewriter(
                    regexp_rewriter(self.alphabet, force, NfaRegexp))
    
    def clear(self):
        self.__unused = False
        self.__rewriters = []
        self.__monitors = []
        self.__stream_factory = DEFAULT_STREAM_FACTORY
        self.__alphabet = None
        return self

    def default(self):
        self.clear()
        self.flatten()
        self.compose_transforms()
        self.lexer()
        self.auto_memoize()
        self.trace()
        return self
        