
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
Rewrite a matcher graph to include lexing.
'''

from collections import deque
from logging import getLogger

from lepl.lexer.matchers import BaseToken, Lexer, LexerError, NonToken
from lepl.operators import Matcher
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
            if isinstance(matcher, BaseToken):
                tokens.add(matcher)
                if matcher.content:
                    assert_not_token(matcher.content, visited)
            else:
                for child in matcher:
                    if isinstance(child, Matcher):
                        stack.append(child)
    if tokens and non_tokens:
        raise LexerError('The grammar contains a mix of Tokens and non-Token '
                         'matchers at the top level. If Tokens are used then '
                         'non-token matchers that consume input must only '
                         'appear "inside" Tokens.  The non-Token matchers '
                         'include: {0}.'
                         .format('; '.join(n.__class__.__name__ 
                                           for n in non_tokens)))
    return tokens


def unique_ids(tokens):
    '''
    Drop tokens with unique IDs (these are "machine added" things like 
    indentation).
    '''
    log = getLogger('lepl.lexer.rewriters.unique_ids')
    by_id = {}
    for token in tokens:
        if token.id_ in by_id:
            if type(token.id_) is int:
                log.warn('Discarding duplicate token: {0}'.format(token))
        else:
            by_id[token.id_] = token
    return set(by_id.values())


def assert_not_token(node, visited):
    '''
    Assert that neither this nor any child node is a Token. 
    '''
    if isinstance(node, Matcher) and node not in visited:
        visited.add(node)
        if isinstance(node, BaseToken):
            raise LexerError('Nested token: {0}'.format(node))
        else:
            for child in node:
                assert_not_token(child, visited)


def lexer_rewriter(alphabet=None, discard='[ \t\r\n]', extra_tokens=None, 
                   source=None):
    '''
    This is required when using Tokens.  It does the following:
    - Find all tokens in the matcher graph
    - Construct a lexer from the tokens
    - Connect the lexer to the matcher
    - Check that all children have a token parent 
      (and optionally add a default token)
    Although possibly not in that order. 
    
    alphabet is the alphabet for which the regular expressions are defined.
    
    discard is a regular expression that is used to match space (typically)
    if no token can be matched (and which is then discarded)
    
    error is raised if no token or discard can be matched (it is passed the
    current stream).
    
    extra_tokens are added to those found by analysing the grammar.
    
    source is the source used to generate the final stream.
    '''

    log = getLogger('lepl.lexer.rewriters.lexer_rewriter')

    if alphabet is None:
        alphabet = UnicodeAlphabet.instance()
    def rewriter(matcher):
        '''
        Either construct the lexer, or warn that none found.
        '''
        tokens = find_tokens(matcher)
        if extra_tokens:
            tokens.update(extra_tokens)
        # this breaks specialised tokens
#        tokens = unique_ids(tokens)
        if tokens:
            return Lexer(matcher, tokens, alphabet, discard, source=source)
        else:
            log.info('Lexer rewriter used, but no tokens found.')
            return matcher
    return rewriter
