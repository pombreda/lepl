
from logging import basicConfig, DEBUG, INFO

from lepl import *
from lepl._example.support import Example


class ErrorTest(Example):
    
    def make_parser(self):

        basicConfig(level=DEBUG)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass
        
        expr    = Delayed()
        number  = Digit()[1:,...]                          > 'number'
        badChar = AnyBut(Space() | Digit() | '(')[1:,...]
        
        with Separator(r'\s*'):
            
            unopen   = number ** make_error('no ( before {stream_out}') & ')'
            unclosed = ('(' & expr & Eos()) ** make_error('no ) for {stream_in}')
        
            term    = Or(
                         (number | '(' & expr & ')')      > Term,
                         badChar                          ^ 'unexpected text: {results[0]}',
                         unopen                           >> throw,
                         unclosed                         >> throw
                         )
            muldiv  = Any('*/')                           > 'operator'
            factor  = (term & (muldiv & term)[:])         > Factor
            addsub  = Any('+-')                           > 'operator'
            expr   += (factor & (addsub & factor)[:])     > Expression
            line    = Empty() & Trace(expr) & Eos()
        
        return line.parse_string
    
    def test_errors(self):
        parser = self.make_parser()
        self.examples([(lambda: parser('1 + 2 * (3 + 4 - 5')[0],
                       """  File "str: '1 + 2 * (3 + 4 - 5'", line 1
    1 + 2 * (3 + 4 - 5
            ^
lepl.error.Error: no ) for '(3 + 4...'
"""),
                       (lambda: parser('1 + 2 * 3 + 4 - 5)')[0],
                        """  File "str: '1 + 2 * 3 + 4 - 5)'", line 1
    1 + 2 * 3 + 4 - 5)
                    ^
lepl.error.Error: no ( before ')'
"""),
                       (lambda: parser('1 + 2 * (3 + four - 5)')[0],
                        """  File "str: '1 + 2 * (3 + four - 5)'", line 1
    1 + 2 * (3 + four - 5)
                 ^
lepl.error.Error: unexpected text: four
"""),
                       (lambda: parser('1 + 2 ** (3 + 4 - 5)')[0],
                        """  File "str: '1 + 2 ** (3 + 4 - 5)'", line 1
    1 + 2 ** (3 + 4 - 5)
           ^
lepl.error.Error: unexpected text: *
""")])
        