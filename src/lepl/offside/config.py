
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
from lepl.offside.regexp import LineAwareAlphabet
from lepl.offside.stream import LineAwareStreamFactory, OffsideSource
from lepl.regexp.matchers import BaseRegexp
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
    '''
    
    def __init__(self, rewriters=None, monitors=None, alphabet=None,
                 discard='[ \t\r\n]', tabsize=None):
        if rewriters is None:
            rewriters = [flatten, compose_transforms, auto_memoize()]
        if monitors is None:
            monitors = [TraceResults(False)]
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        alphabet = LineAwareAlphabet(alphabet)
        rewriters = [fix_arguments(BaseRegexp, alphabet=alphabet),
                     fix_arguments(BaseToken, alphabet=alphabet),
                     lexer_rewriter(alphabet, discard=discard, 
                                    source=OffsideSource.factory(tabsize))] \
                    + rewriters
        stream_factory = LineAwareStreamFactory(alphabet)
        super(LineAwareConfiguration, self).__init__(
                                    rewriters=rewriters, monitors=monitors, 
                                    stream_factory=stream_factory)


class OffsideConfiguration(Configuration):
    '''
    As `LineAwareConfiguration`, but with additional support for
    structured matching ("offside rule") with `Line` and `Block`.
    '''
    
    def __init__(self, rewriters=None, monitors=None, alphabet=None,
                 discard='[ \t\r\n]', tabsize=DEFAULT_TABSIZE, 
                 policy=DEFAULT_POLICY, start=0):
        if rewriters is None:
            rewriters = [flatten, compose_transforms, auto_memoize()]
        if monitors is None:
            monitors = [TraceResults(False)]
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        alphabet = LineAwareAlphabet(alphabet)
        rewriters = [fix_arguments(BaseRegexp, alphabet=alphabet),
                     fix_arguments(BaseToken, alphabet=alphabet),
                     fix_arguments(Block, policy=policy),
                     lexer_rewriter(alphabet, discard=discard, 
                                     source=OffsideSource.factory(tabsize))] \
                    + rewriters
        monitors.append(block_monitor(start))
        stream_factory = LineAwareStreamFactory(alphabet)
        super(OffsideConfiguration, self).__init__(
                                    rewriters=rewriters, monitors=monitors, 
                                    stream_factory=stream_factory)
    