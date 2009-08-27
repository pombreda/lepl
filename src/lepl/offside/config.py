
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.



from lepl.config import Configuration
from lepl.lexer.matchers import BaseToken
from lepl.offside.lexer import offside_rewriter
from lepl.offside.regexp import LineAwareAlphabet
from lepl.offside.stream import LineAwareStreamFactory
from lepl.regexp.matchers import BaseRegexp
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.rewriters import fix_arguments


class LineAwareConfiguration(Configuration):
    
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


class IndentationConfiguration(Configuration):
    
    def __init__(self, rewriters=None, monitors=None, alphabet=None,
                 discard=None, tabsize=None, error=None, extra_tokens=None):
        if rewriters is None:
            rewriters = []
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        alphabet = LineAwareAlphabet(alphabet)
        rewriters.extend([fix_arguments(BaseRegexp, alphabet=alphabet),
                          fix_arguments(BaseToken, alphabet=alphabet),
                          offside_rewriter(alphabet, discard, error, 
                                           extra_tokens)])
        stream_factory = LineAwareStreamFactory(alphabet)
        super(IndentationConfiguration, self).__init__(
                                    rewriters=rewriters, monitors=monitors, 
                                    stream_factory=stream_factory)
