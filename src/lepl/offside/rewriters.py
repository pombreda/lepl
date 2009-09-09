
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
Rewriters and related classes for adding indents.
'''

from lepl.lexer.rewriters import lexer_rewriter
from lepl.offside.regexp import LineAwareAlphabet
from lepl.offside.support import OffsideException
from lepl.offside.lexer import Eol, Indent




def indent_rewriter(alphabet, discard=None, error=None, extra_tokens=None, 
                    source=None):
    '''
    Rewrite a matcher so that indent tokens are present.
    '''
    if discard is None:
        discard = '[ \t\r\n]'
    if not isinstance(alphabet, LineAwareAlphabet):
        raise OffsideException('Alphabet must be line-aware.')
    if not extra_tokens:
        extra_tokens = set()
    extra_tokens.update([Indent(), Eol()])
    return lexer_rewriter(alphabet=alphabet, discard=discard, error=error, 
                          extra_tokens=extra_tokens, source=source)


