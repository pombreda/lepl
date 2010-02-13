
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

from lepl.core.parser import make_matcher, make_parser
from lepl.stream.stream import DEFAULT_STREAM_FACTORY
from lepl.support.lib import lmap

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
        if rewriters is None:
            rewriters = []
        self.__rewriters = rewriters
        self.monitors = monitors
        if stream_factory is None:
            stream_factory = DEFAULT_STREAM_FACTORY
        self.stream_factory = stream_factory
        
    def add_rewriter(self, rewriter, order=1000):
        self.__rewriters.append((rewriter, order))
        
    @property
    def rewriters(self):
        rewriters = list(self.__rewriters)
        rewriters.sort(key=lambda x: x[1])
        return lmap(lambda x: x[0], rewriters)
        
    

class ConfigBuilder(object):
    
    def __init__(self):
        # this is cleared when any config is specified by the user
        # if it is set when the configuration is requested, then the default
        # config is generated (so if the user sets anything, then that takes
        # priority and is from an empty state)
        self.__default = True
        # this is set whenever and config is changed.  it is cleared when
        # the configuration is read.  so if is is false then the configuration
        # is the same as previously read
        self.__changed = True
        self.__rewriters = []
        self.__monitors = []
        self.__stream_factory = DEFAULT_STREAM_FACTORY
        self.__alphabet = None
        
    # raw access to basic components
        
    def add_rewriter(self, rewriter, order=1000):
        self.__default = False
        self.__changed = True
        self.__rewriters.append((rewriter, order))
        return self

    def add_monitor(self, monitor):
        self.__default = False
        self.__changed = True
        self.__monitors.append(monitor)
        return self
    
    def stream_factory(self, stream_factory=DEFAULT_STREAM_FACTORY):
        self.__default = False
        self.__changed = True
        self.__stream_factory = stream_factory
        return self

    @property
    def configuration(self):
        if self.__default:
            self.default()
        self.__changed = False
        return Configuration(self.__rewriters, self.__monitors, 
                             self.__stream_factory)
    
    @configuration.setter
    def configuration(self, configuration):
        self.__rewriters = list(configuration.rewriters)
        self.__monitors = list(configuration.monitors)
        self.__stream_factory = configuration.stream_factory
        self.__changed = True
    
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
                
    @property
    def changed(self):
        return self.__changed
    
    # rewriters
    
    def set_arguments(self, type_, order=0, **kargs):
        '''
        Set the given keyword arguments on all matchers of the given `type_`
        (ie class) in the grammar.
        '''
        from lepl.core.rewriters import set_arguments
        return self.add_rewriter(set_arguments(type_, **kargs), order)
        
    def set_alphabet_arg(self, alphabet, order=0):
        '''
        Set `alphabet` on various matchers.  This is useful when using an 
        unusual alphabet (most often when using line-aware parsing), as
        it saves having to specify it on each matcher when creating the
        grammar.
        
        Although this option is often required for line aware parsing,
        you normally do not need to call this because it is called by 
        `default_line_aware` (and `line_aware`).
        '''
        from lepl.regexp.matchers import BaseRegexp
        from lepl.lexer.matchers import BaseToken
        self.alphabet = alphabet
        self.set_arguments(BaseRegexp, order=order, alphabet=self.alphabet)
        self.set_arguments(BaseToken, order=order, alphabet=self.alphabet)
        return self

    def set_block_policy_arg(self, block_policy, order=0):
        '''
        Set the block policy on all `Block` instances.
        
        Although this option is required for "offside rule" parsing,
        you normally do not need to call this because it is called by 
        `default_line_aware` (and `line_aware`) if either `block_policy` 
        or `block_start` is specified.
        '''
        from lepl.offside.matchers import Block
        return self.set_arguments(Block, order=order, policy=block_policy)
    
    def flatten(self, order=10):
        from lepl.core.rewriters import flatten
        return self.add_rewriter(flatten, order)
        
    def compile_to_dfa(self, force=False, alphabet=None, order=20):
        from lepl.regexp.matchers import DfaRegexp
        from lepl.regexp.rewriters import regexp_rewriter
        self.alphabet = alphabet
        return self.add_rewriter(
                    regexp_rewriter(self.alphabet, force, DfaRegexp), order)
    
    def compile_to_nfa(self, force=False, alphabet=None, order=20):
        from lepl.regexp.matchers import NfaRegexp
        from lepl.regexp.rewriters import regexp_rewriter
        self.alphabet = alphabet
        return self.add_rewriter(
                    regexp_rewriter(self.alphabet, force, NfaRegexp), order)
        
    def optimize_or(self, conservative=True, order=30):
        from lepl.core.rewriters import optimize_or
        return self.add_rewriter(optimize_or(conservative), order)
        
    def lexer(self, alphabet=None, discard=None, source=None, order=40):
        from lepl.lexer.rewriters import lexer_rewriter
        self.alphabet = alphabet
        return self.add_rewriter(
            lexer_rewriter(alphabet=self.alphabet, discard=discard,
                           source=source), order)
    
    def no_trampoline(self, spec=None, order=50):
        from lepl.core.rewriters import function_only
        from lepl.matchers.combine import DepthFirst, DepthNoTrampoline, \
            BreadthFirst, BreadthNoTrampoline, And, AndNoTrampoline, \
            Or, OrNoTrampoline
        if spec is None:
            spec = {DepthFirst: (('first', 'rest'), DepthNoTrampoline),
                    BreadthFirst: (('first', 'rest'), BreadthNoTrampoline),
                    And: (('*matchers',), AndNoTrampoline),
                    Or: (('*matchers',), OrNoTrampoline)}
        return self.add_rewriter(function_only(spec), order)
    
    def compose_transforms(self, order=60):
        from lepl.core.rewriters import compose_transforms
        return self.add_rewriter(compose_transforms, order)
        
    def auto_memoize(self, conservative=None, order=100):
        from lepl.core.rewriters import auto_memoize
        return self.add_rewriter(auto_memoize(conservative))
    
    def left_memoize(self, order=100):
        from lepl.core.rewriters import memoize
        from lepl.matchers.memo import LMemo
        return self.add_rewriter(memoize(LMemo))
    
    def right_memoize(self, order=100):
        from lepl.core.rewriters import memoize
        from lepl.matchers.memo import RMemo
        return self.add_rewriter(memoize(RMemo))
    
    # monitors
    
    def trace(self, enabled=False):
        from lepl.core.trace import TraceResults
        return self.add_monitor(TraceResults(enabled))
    
    def manage(self, queue_len=0):
        from lepl.core.manager import GeneratorManager
        return self.add_monitor(GeneratorManager(queue_len))
    
    # packages
    
    def blocks(self, block_policy=None, block_start=None):
        '''
        Set the given `block_policy` on all block elements and add a 
        `block_monitor` with the given `block_start`.  If either is
        not given, default values are used.
        
        Although these options are required for "offside rule" parsing,
        you normally do not need to call this because it is called by 
        `default_line_aware` (and `line_aware`) if either `block_policy` or 
        `block_start` is specified.
        '''
        from lepl.offside.matchers import DEFAULT_POLICY 
        from lepl.offside.monitor import block_monitor
        if block_policy is None:
            block_policy = DEFAULT_POLICY
        if block_start is None:
            block_start = 0
        self.add_monitor(block_monitor(block_start))
        self.set_block_policy_arg(block_policy)
        return self
    
    def line_aware(self, alphabet=None, parser_factory=None,
                   discard=None, tabsize=None, 
                   block_policy=None, block_start=None):
        '''
        Configure the parser for line aware behaviour.  This sets many 
        different options and is intended to be the "normal" way to enable
        line aware parsing (including "offside rule" support).
        
        See also `default_line_aware`.
        
        Normally calling this method is all that is needed for configuration.
        If you do need to "fine tune" the configuration for parsing should
        consult the source for this method and then call other methods
        as needed.
        
        `alphabet` is the alphabet used; by default it is assumed to be Unicode
        and it will be extended to include start and end of line markers.
        
        `parser_factory` is used to generate a regexp parser.  If this is unset
        then the parser used depends on whether blocks are being used.  If so,
        then the HideSolEolParser is used (so that you can specify tokens 
        without worrying about SOL and EOL); otherwise a normal parser is
        used.
        
        `discard` is a regular expression which is matched against the stream
        if lexing otherwise fails.  A successful match is discarded.  If None
        then the usual token defaut is used (whitespace).  To disable, use
        an empty string.
        
        `tabsize`, if not None, should be the number of spaces used to replace
        tabs.
        
        `block_policy` should be the number of spaces in an indent, if blocks 
        are used (or an appropriate function).  By default (ie if `block_start`
        is given) it is taken to be DEFAULT_POLICY.
        
        `block_start` is the initial indentation, if blocks are used.  By 
        default (ie if `block_policy` is given) 0 is used.
        
        To enable blocks ("offside rule" parsing), at least one of 
        `block_policy` and `block_start` must be given.
        `
        '''
        from lepl.offside.matchers import DEFAULT_TABSIZE
        from lepl.offside.regexp import LineAwareAlphabet, \
            make_hide_sol_eol_parser
        from lepl.offside.stream import LineAwareStreamFactory, \
            LineAwareTokenSource
        from lepl.regexp.str import make_str_parser
        from lepl.regexp.unicode import UnicodeAlphabet
        
        self.clear()
        
        use_blocks = block_policy is not None or block_start is not None
        if use_blocks:
            self.blocks(block_policy, block_start)
            
        if tabsize is None:
            tabsize = DEFAULT_TABSIZE
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        if not parser_factory:
            if use_blocks:
                parser_factory = make_hide_sol_eol_parser
            else:
                parser_factory = make_str_parser
        self.alphabet = LineAwareAlphabet(alphabet, parser_factory)

        self.set_alphabet_arg(self.alphabet)
        if use_blocks:
            self.set_block_policy_arg(block_policy)
        self.lexer(alphabet=self.alphabet, discard=discard, 
                   source=LineAwareTokenSource.factory(tabsize))
        self.stream_factory(LineAwareStreamFactory(self.alphabet))
        
        return self
        
    def default_line_aware(self, alphabet=None, parser_factory=None,
                           discard=None, tabsize=None, 
                           block_policy=None, block_start=None):
        '''
        Configure the parser for line aware behaviour.  This sets many 
        different options and is intended to be the "normal" way to enable
        line aware parsing (including "offside rule" support).
        
        Compared to `line_aware`, this also adds various "standard" options.
        
        Normally calling this method is all that is needed for configuration.
        If you do need to "fine tune" the configuration for parsing should
        consult the source for this method and then call other methods
        as needed.
        
        `alphabet` is the alphabet used; by default it is assumed to be Unicode
        and it will be extended to include start and end of line markers.
        
        `parser_factory` is used to generate a regexp parser.  If this is unset
        then the parser used depends on whether blocks are being used.  If so,
        then the HideSolEolParser is used (so that you can specify tokens 
        without worrying about SOL and EOL); otherwise a normal parser is
        used.
        
        `discard` is a regular expression which is matched against the stream
        if lexing otherwise fails.  A successful match is discarded.  If None
        then the usual token defaut is used (whitespace).  To disable, use
        an empty string.
        
        `tabsize`, if not None, should be the number of spaces used to replace
        tabs.
        
        `block_policy` should be the number of spaces in an indent, if blocks 
        are used (or an appropriate function).  By default (ie if `block_start`
        is given) it is taken to be DEFAULT_POLICY.
        
        `block_start` is the initial indentation, if blocks are used.  By 
        default (ie if `block_policy` is given) 0 is used.
        
        To enable blocks ("offside rule" parsing), at least one of 
        `block_policy` and `block_start` must be given.
        `
        '''
        self.line_aware(alphabet, parser_factory, discard, tabsize, 
                        block_policy, block_start)
        self.flatten()
        self.compose_transforms()
        self.auto_memoize()
        return self
        
    
    def clear(self):
        self.__default = False
        self.__changed = True
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
        self.no_trampoline()
        self.compile_to_nfa()
        return self


class ParserMixin(object):
    '''
    Methods to configure and generate a parser or matcher.
    '''
    
    def __init__(self, *args, **kargs):
        super(ParserMixin, self).__init__(*args, **kargs)
        self.config = ConfigBuilder()
        self.__matcher_cache = None
        self.__from = None

    def __matcher(self, from_, kargs):
        if self.config.changed or self.__matcher_cache is None \
                or self.__from != from_:
            config = self.config.configuration
            self.__from = from_
            stream_factory = getattr(config.stream_factory, 'from_' + from_)
            self.__matcher_cache = \
                make_matcher(self, stream_factory, config, kargs)
        return self.__matcher_cache
    
    def file_parser(self, **kargs):
        '''
        Construct a parser for file objects that uses a stream 
        internally and returns a single result.
        '''
        return make_parser(self.file_matcher(**kargs))
    
    def items_parser(self, **kargs):
        '''
        Construct a parser for a sequence of times (an item is something
        that would be matched by `Any`) that uses a stream internally and 
        returns a single result.
        '''
        return make_parser(self.items_matcher(**kargs))
    
    def path_parser(self, **kargs):
        '''
        Construct a parser for a file that uses a stream 
        internally and returns a single result.
        '''
        return make_parser(self.path_matcher(**kargs))
    
    def string_parser(self, **kargs):
        '''
        Construct a parser for strings that uses a stream 
        internally and returns a single result.
        '''
        return make_parser(self.string_matcher(**kargs))
    
    def null_parser(self, **kargs):
        '''
        Construct a parser for strings and lists that returns a single result
        (this does not use streams).
        '''
        return make_parser(self.null_matcher(**kargs))
    
    
    def parse_file(self, file_, **kargs):
        '''
        Parse the contents of a file, returning a single match and using a
        stream internally.
        '''
        return self.file_parser(**kargs)(file_)
        
    def parse_items(self, list_, **kargs):
        '''
        Parse the contents of a sequence of items (an item is something
        that would be matched by `Any`), returning a single match and using a
        stream internally.
        '''
        return self.items_parser(**kargs)(list_)
        
    def parse_path(self, path, **kargs):
        '''
        Parse the contents of a file, returning a single match and using a
        stream internally.
        '''
        return self.path_parser(**kargs)(path)
        
    def parse_string(self, string, **kargs):
        '''
        Parse the contents of a string, returning a single match and using a
        stream internally.
        '''
        return self.string_parser(**kargs)(string)
    
    def parse(self, stream, **kargs):
        '''
        Parse the contents of a string or list, returning a single match (this
        does not use streams).
        '''
        return self.null_parser(**kargs)(stream)
    
    
    def file_matcher(self, **kargs):
        '''
        Construct a parser for file objects that returns a sequence of matches
        and uses a stream internally.
        '''
        return self.__matcher('file', kargs)
    
    def items_matcher(self, **kargs):
        '''
        Construct a parser for a sequence of items (an item is something that
        would be matched by `Any`) that returns a sequence of matches
        and uses a stream internally.
        '''
        return self.__matcher('items', kargs)
    
    def path_matcher(self, **kargs):
        '''
        Construct a parser for a file that returns a sequence of matches
        and uses a stream internally.
        '''
        return self.__matcher('path', kargs)
    
    def string_matcher(self, **kargs):
        '''
        Construct a parser for strings that returns a sequence of matches
        and uses a stream internally.
        '''
        return self.__matcher('string', kargs)

    def null_matcher(self, **kargs):
        '''
        Construct a parser for strings and lists list objects that returns a 
        sequence of matches (this does not use streams).
        '''
        return self.__matcher('null', kargs)

    def match_file(self, file_, **kargs):
        '''
        Parse the contents of a file, returning a sequence of matches and using 
        a stream internally.
        '''
        return self.file_matcher(**kargs)(file_)
        
    def match_items(self, list_, **kargs):
        '''
        Parse a sequence of items (an item is something that would be matched
        by `Any`), returning a sequence of matches and using a
        stream internally.
        '''
        return self.items_matcher(**kargs)(list_)
        
    def match_path(self, path, **kargs):
        '''
        Parse a file, returning a sequence of matches and using a
        stream internally.
        '''
        return self.path_matcher(**kargs)(path)
        
    def match_string(self, string, **kargs):
        '''
        Parse a string, returning a sequence of matches and using a
        stream internally.
        '''
        return self.string_matcher(**kargs)(string)

    def match(self, stream, **kargs):
        '''
        Parse a string or list, returning a sequence of matches 
        (this does not use streams).
        '''
        return self.null_matcher(**kargs)(stream)
