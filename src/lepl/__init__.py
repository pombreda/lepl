
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

from lepl.config import Configuration
from lepl.memo import * 
from lepl.node import *
from lepl.operators import * 
from lepl.parser import *
from lepl.regexp import *
from lepl.stream import *
from lepl.manager import *
from lepl.matchers import *
from lepl.regexp.matchers import NfaRegexp, DfaRegexp
from lepl.regexp.rewriters import regexp_rewriter
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.rewriters import *
from lepl.trace import *

__all__ = [
        # config
        'Configuration',
        # match
        'Empty',
        'Repeat',
        'And',
        'Or',
        'First',
        'Any',
        'Literal',
        'Empty',
        'Lookahead',
        'Apply',
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
        'GREEDY',
        'NON_GREEDY',
        'DEPTH_FIRST',
        'BREADTH_FIRST',
        # node
        'Node',
        'make_dict',
        'join_with',
        'make_error',
        'raise_error',
        'Error',
        'throw',
        # stream
        'Stream',
        # operators
        'Override',
        'Separator',
        # parser
        'Configuration',
        # manager
        'GeneratorManager',
        # trace
        'RecordDeepest',
        'TraceResults',
        # parser
        # memo,
        'RMemo',
        'LMemo',
        # regexp.matchers
        'NfaRegexp',
        'DfaRegexp',
        # regexp.rewriters
        'regexp_rewriter',
        # regexp.unicode
        'UnicodeAlphabet',
        # rewriters
        'memoize',
        'flatten',
        'compose_transforms',
        'auto_memoize',
        'context_memoize',
        'optimize_or']

__version__ = '2.3.5'

if __version__.find('b') > -1:
    from logging import getLogger, basicConfig, WARN
#    basicConfig(level=WARN)
    getLogger('lepl').warn('You are using a BETA version of LEPL.')
