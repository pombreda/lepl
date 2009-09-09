
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
from lepl.offside.matchers import DEFAULT_TABSIZE, DEFAULT_POLICY, Block
from lepl.offside.monitor import BlockMonitor
from lepl.offside.regexp import LineAwareAlphabet
from lepl.offside.rewriters import indent_rewriter
from lepl.offside.stream import LineAwareStreamFactory, OffsideSource
from lepl.regexp.matchers import BaseRegexp
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.rewriters import fix_arguments


# pylint: disable-msg=R0913
# lepl conventions

class LineAwareConfiguration(Configuration):
    '''
    Configure the system so that the given alphabet is extended to be
    "line-aware".  This means that the stream will contain additional
    start-of-line and end-of-line values (see `LineAwareAlphabet`), but
    does not introduce any special tokens. 
    '''
    
    def __init__(self, rewriters=None, monitors=None, alphabet=None):
        if rewriters is None:
            rewriters = []
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        alphabet = LineAwareAlphabet(alphabet)
        rewriters.append(fix_arguments(BaseRegexp, alphabet=alphabet))
        stream_factory = LineAwareStreamFactory(alphabet)
        super(LineAwareConfiguration, self).__init__(
                                    rewriters=rewriters, monitors=monitors, 
                                    stream_factory=stream_factory)


class IndentConfiguration(Configuration):
    '''
    Configure the system so that a given alphabet is extended to be
    "line-aware" and that additional tokens are generated for the
    initial indent (`Indent`) and end of line (`Eol`).
    '''
    
    def __init__(self, rewriters=None, monitors=None, alphabet=None,
                 discard=None, error=None, extra_tokens=None,
                 tabsize=DEFAULT_TABSIZE):
        if rewriters is None:
            rewriters = []
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        alphabet = LineAwareAlphabet(alphabet)
        rewriters.extend([fix_arguments(BaseRegexp, alphabet=alphabet),
                          fix_arguments(BaseToken, alphabet=alphabet),
                          indent_rewriter(alphabet, discard=discard, 
                                    error=error, extra_tokens=extra_tokens, 
                                    source=OffsideSource.factory(tabsize))])
        stream_factory = LineAwareStreamFactory(alphabet)
        super(IndentConfiguration, self).__init__(
                                    rewriters=rewriters, monitors=monitors, 
                                    stream_factory=stream_factory)


class OffsideConfiguration(Configuration):
    '''
    Configure the system so that a given alphabet is extended to be
    "line-aware", additional tokens are generated for the initial 
    indent (`Indent`) and end of line (`Eol`), indent
    is converted to space count, and additional support is added for
    structured matching ("offside rule") with `Line` and `Block`.
    '''
    
    def __init__(self, rewriters=None, monitors=None, alphabet=None,
                 discard=None, error=None, extra_tokens=None,
                 tabsize=DEFAULT_TABSIZE, policy=DEFAULT_POLICY):
        if rewriters is None:
            rewriters = []
        if monitors is None:
            monitors = []
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        alphabet = LineAwareAlphabet(alphabet)
        rewriters.extend([fix_arguments(BaseRegexp, alphabet=alphabet),
                          fix_arguments(BaseToken, alphabet=alphabet),
                          fix_arguments(Block, policy=policy),
                          indent_rewriter(alphabet, discard=discard, 
                                    error=error, extra_tokens=extra_tokens, 
                                    source=OffsideSource.factory(tabsize))])
        monitors.append(BlockMonitor)
        stream_factory = LineAwareStreamFactory(alphabet)
        super(OffsideConfiguration, self).__init__(
                                    rewriters=rewriters, monitors=monitors, 
                                    stream_factory=stream_factory)
    