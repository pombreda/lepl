
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
The `Indentation` token and support.
'''


from lepl.lexer.matchers import BaseToken
from lepl.lexer.rewriters import lexer_rewriter
from lepl.offside.regexp import LineAwareAlphabet
from lepl.offside.support import OffsideException


# pylint: disable-msg=R0901, R0904, R0913
class Indentation(BaseToken):
    '''
    This token is identified by its class.
    '''
    
    def __init__(self, content=None, id_=None, alphabet=None, complete=True, 
                 compiled=False):
        self.regexp = '^[ \t]*'
        if id_ is None:
            id_ = Indentation
        super(Indentation, self).__init__(content=content, id=id_, 
                                          alphabet=alphabet, complete=complete, 
                                          compiled=compiled)


def offside_rewriter(alphabet, discard=None, error=None, extra_tokens=None, 
                     adapter=None):
    '''
    Rewrite a matcher so that indentation tokens are present.
    '''
    if discard is None:
        discard = '[$ \t\r\n]'
    if not isinstance(alphabet, LineAwareAlphabet):
        raise OffsideException('Alphabet must be line-aware.')
    if not extra_tokens:
        extra_tokens = set()
    extra_tokens.add(Indentation())
    return lexer_rewriter(alphabet, discard, error, extra_tokens, adapter)
