
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
Pre-built configurations for using the package in several standard ways.
'''


from lepl.config import Configuration
from lepl.lexer.matchers import BaseToken
from lepl.lexer.rewriters import lexer_rewriter
from lepl.offside.matchers import DEFAULT_TABSIZE, DEFAULT_POLICY, Block
from lepl.offside.monitor import block_monitor
from lepl.offside.regexp import LineAwareAlphabet, make_hide_sol_eol_parser
from lepl.offside.stream import LineAwareStreamFactory, LineAwareTokenSource
from lepl.regexp.matchers import BaseRegexp
from lepl.regexp.str import make_str_parser
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.rewriters import fix_arguments, flatten, compose_transforms, \
    auto_memoize
from lepl.trace import TraceResults


# pylint: disable-msg=R0913
# lepl conventions

class LineAwareConfiguration(Configuration):
    '''
    Configure the system so that a given alphabet is extended to be
    "line-aware": SOL and EOL markers are added; `Indent` and `Eol`
    tokens will work, etc.
    
    If `Block` or `BLine` is used, or a block_policy or block_start is given, 
    then the associated monitor is also added automatically.
    '''
    
    def __init__(self, rewriters=None, monitors=None, 
                 alphabet=None, parser_factory=None,
                 discard='[ \t\r\n]', tabsize=DEFAULT_TABSIZE, 
                 block_policy=None, block_start=None):
        '''
        rewriters is an optional list of rewriters that will be used.  If not
        given the same defaults as the standard default configuration will be
        used.
        
        monitors is an optional list of monitors that will be used.  If not 
        given the same defaults as the standard default configuration will be
        used.  In addition a monitor for blocks is added if block_policy or 
        block_start is specified.
        
        alphabet is the alphabet used; by default it is assumed to be Unicode
        and it will be extended to include start and end of line markers.
        
        parser_factory is used to generate a regexp parser.  If this is unset
        then the parser used depends on whether blocks are being used.  If so,
        then the HideSolEolParser is used (so that you can specify tokens 
        without worrying about SOL and EOL); otherwise a normal parser is
        used.
        
        discard is a regular expression which is matched against the stream
        if lexing otherwise fails.  A successful match is discarded.  If None
        then this is not used.
        
        tabsize, if not None, should be the number of spaces used to replace
        tabs.
        
        block_policy should be the number of spaces in an indent, if blocks are
        used (or an appropriate function).  By default (ie if block_start is 
        given) it is taken to be DEFAULT_POLICY.
        
        start is the initial indentation, if blocks are used.  By default 
        (ie if block_policy is given) 0 is used.
        '''
        if rewriters is None:
            rewriters = [flatten, compose_transforms, auto_memoize()]
        if monitors is None:
            monitors = [TraceResults(False)]
        use_blocks = block_policy is not None or block_start is not None
        if use_blocks:
            if block_policy is None:
                block_policy = DEFAULT_POLICY
            if block_start is None:
                block_start = 0
            monitors.append(block_monitor(block_start))
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        if not parser_factory:
            if use_blocks:
                parser_factory = make_hide_sol_eol_parser
            else:
                parser_factory = make_str_parser
        alphabet = LineAwareAlphabet(alphabet, parser_factory)
        rewriters = [fix_arguments(BaseRegexp, alphabet=alphabet),
                     fix_arguments(BaseToken, alphabet=alphabet)] + \
                    ([fix_arguments(Block, policy=block_policy)] 
                      if use_blocks else []) + \
                    [lexer_rewriter(alphabet, discard=discard, 
                            source=LineAwareTokenSource.factory(tabsize))] \
                    + rewriters
        stream_factory = LineAwareStreamFactory(alphabet)
        super(LineAwareConfiguration, self).__init__(
                                    rewriters=rewriters, monitors=monitors, 
                                    stream_factory=stream_factory)
