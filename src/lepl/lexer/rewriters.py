
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

'''
Rewrite a matcher graph to include lexing.
'''

from collections import deque
from logging import getLogger

from lepl.lexer.matchers \
    import Token, TOKENS, TokenNamespace, Lexer, LexerError, NonToken
from lepl.operators import Matcher, Global
from lepl.regexp.unicode import UnicodeAlphabet


def find_tokens(matcher):
    '''
    Returns a set of Tokens.  Also asserts that children of tokens are
    not themselves Tokens. 
    
    Should we also check that a Token occurs somewhere on every path to a
    leaf node?
    '''
    (tokens, visited, non_tokens) = (set(), set(), set())
    stack = deque([matcher])
    while stack:
        matcher = stack.popleft()
        if isinstance(matcher, NonToken):
            non_tokens.add(matcher)
        if matcher not in visited:
            visited.add(matcher)
            if isinstance(matcher, Token):
                tokens.add(matcher)
                if matcher.content:
                    assert_not_token(matcher.content, visited)
            else:
                for child in matcher.children():
                    if isinstance(child, Matcher):
                        stack.append(child)
    if tokens and non_tokens:
        raise LexerError('The grammar contains a mix of Tokens and non-Token '
                         'matchers at the top level. If Tokens are used then '
                         'non-token matchers that consume input must only '
                         'appear "inside" Tokens.  The non-Token matchers '
                         'include: {0}.'
                         .format('; '.join(n.__class__.__name__ for n in non_tokens)))
    return tokens


def assert_not_token(node, visited):
    '''
    Assert that neither this nor any child node is a Token. 
    '''
    if isinstance(node, Matcher) and node not in visited:
        visited.add(node)
        if isinstance(node, Token):
            raise LexerError('Nested token: {0}'.format(node))
        else:
            for child in node.children():
                assert_not_token(child, visited)


def lexer_rewriter(alphabet=None, skip=None, error=None):
    '''
    This is required when using Tokens.  It does the following:
    - Find all tokens in the matcher graph
    - Construct a lexer from the tokens
    - Connect the lexer to the matcher
    - Check that all children have a token parent 
      (and optionally add a default token)
    Although possibly not in that order. 
    
    alphabet is the alphabet for which the regular expressions are defined.
    
    skip is a regular expression that is used to match space if no token can
    be matched (space is then discarded)
    
    error is raised if no token or space can be matched (it is passed the
    current stream).
    '''

    LOG = getLogger('lepl.lexer.rewriters.lexer_rewriter')

    if alphabet is None:
        alphabet = UnicodeAlphabet.instance()
    if skip is None:
        skip = '.'
    def rewriter(matcher):
        tokens = find_tokens(matcher)
        if tokens:
            return Lexer(matcher, tokens, alphabet, skip, error)
        else:
            LOG.info('Lexer rewriter used, but no tokens found.')
            return matcher
    return rewriter
