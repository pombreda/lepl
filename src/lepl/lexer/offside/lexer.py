
# The contents of this file are subject to the Mozilla Public License
# (MPL) Version 1.1 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License
# at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#
# The Original Code is LEPL (http://www.acooke.org/lepl)
# The Initial Developer of the Original Code is Andrew Cooke.
# Portions created by the Initial Developer are Copyright (C) 2009-2010
# Andrew Cooke (andrew@acooke.org). All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms
# of the LGPL license (the GNU Lesser General Public License,
# http://www.gnu.org/licenses/lgpl.html), in which case the provisions
# of the LGPL License are applicable instead of those above.
#
# If you wish to allow use of your version of this file only under the
# terms of the LGPL License and not to allow others to use your version
# of this file under the MPL, indicate your decision by deleting the
# provisions above and replace them with the notice and other provisions
# required by the LGPL License.  If you do not delete the provisions
# above, a recipient may use your version of this file under either the
# MPL or the LGPL License.

from lepl.lexer.lexer import Lexer
from lepl.core.parser import tagged
from lepl.stream.core import s_empty, s_line, s_debug, s_stream, s_fmt,\
    s_factory, s_next
from lepl.lexer.support import RuntimeLexerError
from lepl.support.lib import fmt
from lepl.lexer.line_aware.lexer import END, EMPTY




INDENT = 'INDENT'
'''
Name for indent token.
'''


def make_offside_lexer(tabsize):
    '''
    Provide the standard `Lexer` interface while including `tabsize`.
    '''
    def wrapper(matcher, tokens, alphabet, discard, 
                t_regexp=None, s_regexp=None):
        return _OffsideLexer(matcher, tokens, alphabet, discard,
                             t_regexp=t_regexp, s_regexp=s_regexp, 
                             tabsize=tabsize)
    return wrapper


class _OffsideLexer(Lexer):
    '''
    An alternative lexer that adds INDENT and EOL tokens.
    '''
    
    def __init__(self, matcher, tokens, alphabet, discard, 
                  t_regexp=None, s_regexp=None, tabsize=8):
        super(_OffsideLexer, self).__init__(matcher, tokens, alphabet, discard,
                                            t_regexp=t_regexp, s_regexp=s_regexp)
        self._karg(tabsize=tabsize)
        self._tab = ' ' * tabsize

    @tagged
    def _match(self, in_stream):
        '''
        Implement matching - pass token stream to tokens.
        '''
        def tokens():
            stream = in_stream
            try:
                while not s_empty(stream):
                    # this section differs from token lexer
                    (line, next_stream) = s_line(stream, False)
                    line_stream = s_stream(stream, line)
                    try:
                        (terminals, size, _) = self.s_regexp.size_match(line_stream)
                    except TypeError:
                        (terminals, size) = ([INDENT], 0)
                    (indent, line_stream) = s_next(line_stream, count=size)
                    if '\t' in indent:
                        indent = indent.replace('\t', self._tab)
                    self._debug(fmt('Indent: {0!r} {1!r} {2!s}',
                                       terminals, indent, s_debug(line_stream)))
                    yield ([INDENT], s_stream(line_stream, indent))
                    # from here on, as token lexer (share?)
                    while not s_empty(line_stream):
                        try:
                            (terminals, match, next_line_stream) = self.t_regexp.match(line_stream)
                            self._debug(fmt('Token: {0!r} {1!r} {2!s}',
                                               terminals, match, s_debug(line_stream)))
                            yield (terminals, s_stream(line_stream, match))
                        except TypeError:
                            (terminals, _size, next_line_stream) = self.s_regexp.size_match(line_stream)
                            self._debug(fmt('Space: {0!r} {1!s}',
                                               terminals, s_debug(line_stream)))
                        line_stream = next_line_stream
                    yield ([END], EMPTY)
                    stream = next_stream
            except TypeError:
                raise RuntimeLexerError(
                    s_fmt(stream, 
                             'No token for {rest} at {location} of {text}.'))
        token_stream = s_factory(in_stream).to_token(tokens(), in_stream)
        generator = self.matcher._match(token_stream)
        while True:
            yield (yield generator)
