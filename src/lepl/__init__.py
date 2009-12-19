
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

#@PydevCodeAnalysisIgnore
# pylint: disable-msg=C0301, E0611, W0401
# confused by __init__?

'''
LEPL is a parser library written in Python.
  
This is the API documentation; the module index is at the bottom of this page.  
There is also a `manual <../index.html>`_ which gives a higher level
overview. 

The home page for this package is the 
`LEPL website <http://www.acooke.org/lepl>`_.


Example
-------

A simple example of how to use LEPL::

    from lepl import *
    
    # For a simpler result these could be replaced with 'list', giving
    # an AST as a set of nested lists 
    # (ie replace '> Term' etc with '> list' below).
    
    class Term(Node): pass
    class Factor(Node): pass
    class Expression(Node): pass
        
    def parse_expression(text):
        
        # Here we define the grammar
        
        # A delayed value is defined later (see penultimate line in block) 
        expr   = Delayed()
        number = Digit()[1:,...]                        > 'number'
        spaces = DropEmpty(Regexp(r'\s*'))
        # Allow spaces between items
        with Separator(spaces):
            term    = number | '(' & expr & ')'         > Term
            muldiv  = Any('*/')                         > 'operator'
            factor  = term & (muldiv & term)[:]         > Factor
            addsub  = Any('+-')                         > 'operator'
            expr   += factor & (addsub & factor)[:]     > Expression
            line    = Trace(expr) & Eos()
    
        # parse_string returns a list of tokens, but expr 
        # returns a single value, so take the first entry
        return expression.parse_string(text)[0]
    
    if __name__ == '__main__':
        print(parse_expression('1 + 2 * (3 + 4 - 5)'))

Running this gives the result::

    Expression
     +- Factor
     |   +- Term
     |   |   `- number '1'
     |   `- ' '
     +- operator '+'
     +- ' '
     `- Factor
         +- Term
         |   `- number '2'
         +- ' '
         +- operator '*'
         +- ' '
         `- Term
             +- '('
             +- Expression
             |   +- Factor
             |   |   +- Term
             |   |   |   `- number '3'
             |   |   `- ' '
             |   +- operator '+'
             |   +- ' '
             |   +- Factor
             |   |   +- Term
             |   |   |   `- number '4'
             |   |   `- ' '
             |   +- operator '-'
             |   +- ' '
             |   `- Factor
             |       `- Term
             |           `- number '5'
             `- ')'
'''

from lepl.core.config import Configuration
from lepl.contrib.matchers import SmartSeparator2
from lepl.match.error import make_error, raise_error, Error, throw
from lepl.match.derived import Apply, args, KApply, Regexp, Delayed, Commit, \
    Trace, AnyBut, Optional, Star, ZeroOrMore, Map, Add, Drop, Substitute, \
    Name, Eof, Eos, Identity, Newline, Space, Whitespace, Digit, Letter, \
    Upper, Lower, Printable, Punctuation, UnsignedInteger, SignedInteger, \
    Float, Word, Separator, DropEmpty, Literals, String, SkipTo, \
    GREEDY, NON_GREEDY, DEPTH_FIRST, BREADTH_FIRST
from lepl.core.memo import RMemo, LMemo, MemoException
from lepl.support.node import Node, make_dict, join_with
from lepl.match.operators import Override, Separator, SmartSeparator1 
from lepl.stream.stream import DEFAULT_STREAM_FACTORY
from lepl.lexer.matchers import Token, LexerError, RuntimeLexerError
from lepl.lexer.rewriters import lexer_rewriter
from lepl.core.manager import GeneratorManager
from lepl.match.core import Empty, Repeat, And, Or, Join, First, Any, Literal, \
    Empty, Lookahead, Columns
from lepl.offside.config import LineAwareConfiguration, LineAwareConfiguration
from lepl.offside.lexer import Indent, Eol, BIndent
from lepl.offside.matchers import Line, Block, BLine, ContinuedLineFactory, \
    ContinuedBLineFactory, Extend, SOL, EOL, rightmost, constant_indent
from lepl.regexp.core import RegexpError
from lepl.regexp.matchers import NfaRegexp, DfaRegexp
from lepl.regexp.rewriters import regexp_rewriter
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.core.rewriters import memoize, flatten, compse_transforms, \
    auto_memoize, context_memoize, optimize_or
from lepl.core.trace import RecordDeepest, TraceResults

__all__ = [
        # lepl.core.config
        'Configuration',
        # lepl.contrib.matchers
        'SmartSeparator2',
        # lepl.match.error
        'make_error',
        'raise_error',
        'Error',
        'throw',
        # lepl.match.core
        'Empty',
        'Repeat',
        'And',
        'Or',
        'Join',
        'First',
        'Any',
        'Literal',
        'Empty',
        'Lookahead',
        'Columns',
        # lepl.match.derived
        'Apply',
        'args',
        'KApply',
        'Regexp', 
        'Delayed', 
        'Commit', 
        'Trace', 
        'AnyBut', 
        'Optional', 
        'Star', 
        'ZeroOrMore', 
        'Plus', 
        'OneOrMore', 
        'Map', 
        'Add', 
        'Drop',
        'Substitute', 
        'Name', 
        'Eof', 
        'Eos', 
        'Identity', 
        'Newline', 
        'Space', 
        'Whitespace', 
        'Digit', 
        'Letter', 
        'Upper', 
        'Lower', 
        'Printable', 
        'Punctuation', 
        'UnsignedInteger', 
        'SignedInteger', 
        'Integer', 
        'UnsignedFloat', 
        'SignedFloat', 
        'SignedEFloat', 
        'Float', 
        'Word',
        'Separator',
        'DropEmpty',
        'Literals',
        'String',
        'SkipTo',
        'GREEDY',
        'NON_GREEDY',
        'DEPTH_FIRST',
        'BREADTH_FIRST',
        # lepl.support.node
        'Node',
        'make_dict',
        'join_with',
        # lepl.stream.stream
        'DEFAULT_STREAM_FACTORY',
        # lepl.match.operators
        'Override',
        'Separator',
        'SmartSeparator1',
        # lepl.lexer.matchers
        'Token',
        'LexerError',
        'RuntimeLexerError',
        # lepl.lexer.rewriters
        'lexer_rewriter',
        # lepl.core.manager
        'GeneratorManager',
        # lepl.core.trace
        'RecordDeepest',
        'TraceResults',
        # lepl.core.memo,
        'RMemo',
        'LMemo',
        'MemoException',
        # lepl.regexp.core
        'RegexpError',
        # lepl.regexp.matchers
        'NfaRegexp',
        'DfaRegexp',
        # lepl.regexp.rewriters
        'regexp_rewriter',
        # lepl.regexp.unicode
        'UnicodeAlphabet',
        # lepl.core.rewriters
        'memoize',
        'flatten',
        'compose_transforms',
        'auto_memoize',
        'context_memoize',
        'optimize_or',
        # lepl.offside.config
        'LineAwareConfiguration',
        'LineAwareConfiguration',
        # lepl.offside.lexer
        'Indent',
        'Eol',
        'BIndent',
        # lepl.offside.matchers
        'Line',
        'Block',
        'BLine',
        'ContinuedLineFactory',
        'ContinuedBLineFactory',
        'Extend',
        'SOL',
        'EOL',
        'rightmost',
        'constant_indent'
       ]

__version__ = '3.3.3'

if __version__.find('b') > -1:
    from logging import getLogger, basicConfig, WARN
    #basicConfig(level=WARN)
    getLogger('lepl').warn('You are using a BETA version of LEPL.')
