
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
from lepl.offside.support import LineAwareException
from lepl.rewriters import flatten
from lepl.regexp.core import Alphabet, Character, Sequence, Choice, Repeat, \
    Option
from lepl.regexp.str import StrAlphabet
from lepl.trace import TraceResults


START = '^'
END = '$'


class Token(object):
    
    def __init__(self, text, high):
        self.text = text
        self.high = high
    
    def __gt__(self, other):
        return other is not self and self.high

    def __ge__(self, other):
        return other is self or self.high
    
    def __eq__(self, other):
        return other is self

    def __lt__(self, other):
        return other is not self and not self.high

    def __le__(self, other):
        return other is self or not self.high
    
    def __str__(self):
        return self.text
    
    def __hash__(self):
        return hash(repr(self))
    
    def __repr__(self):
        return 'Token({0!r},{1:b})'.format(self.text, self.high)
    

SOL = Token(START, False)
EOL = Token(END, True)


class LineAwareAlphabet(StrAlphabet):
    
    def __init__(self, alphabet):
        if not isinstance(alphabet, StrAlphabet):
            raise LineAwareException('Only StrAlphabet subclasses supported: '
                                     '{0}/{1}'.format(alphabet, 
                                                      type(alphabet).__name__))
        super(LineAwareAlphabet, self).__init__(SOL, EOL,
                                parser_factory=make_line_aware_parser)
        self.base = alphabet
        
    def before(self, char):
        if char > self.base.min:
            return self.base.before(char)
        return self.min
    
    def after(self, char):
        if char < self.base.max:
            return self.base.after(char)
        return self.max


def make_line_aware_parser(alphabet):
    
    # Avoid dependency loops
    from lepl.functions import Drop, Eos, AnyBut, Substitute
    from lepl.matchers import Any, Lookahead, Literal, Delayed
    
    dup = lambda x: (alphabet.from_char(x), alphabet.from_char(x))
    tup = lambda x: (alphabet.from_char(x[0]), alphabet.from_char(x[1]))
    # dot doesn't match line boundaries
    dot = lambda x: (alphabet.base.min, alphabet.base.max)
    # Character needed here to ensure intervals passed to invert are ordered 
    invert = lambda x: alphabet.invert(Character(x, alphabet))
    sequence = lambda x: Sequence(x, alphabet)
    repeat = lambda x: Repeat(x, alphabet)
    repeat2 = lambda x: sequence([sequence(x), Repeat(x, alphabet)])
    option = lambda x: Option(x, alphabet)
    choice = lambda x: Choice(x, alphabet)
    character = lambda x: Character(x, alphabet)
    
    # these two definitions enforce the conditions above, providing only
    # special characters appear as literals in the grammar
    escaped  = Drop(alphabet.escape) + Any(alphabet.escaped)
    raw      = ~Lookahead(alphabet.escape) + AnyBut(alphabet.escaped)
    
    sol      = Substitute(START, alphabet.min)
    eol      = Substitute(END, alphabet.max)
    
    single  = escaped | raw
    
    fullchar = (single | sol | eol)                             >> dup
    any_     = Literal('.')                                     >> dot
    letter   = single                                           >> dup
    pair     = single & Drop('-') & single                      > tup
    
    interval = pair | letter
    brackets = Drop('[') & interval[1:] & Drop(']')
    inverted = Drop('[^') & interval[1:] & Drop(']')            >= invert      
    char     = (inverted | brackets | fullchar | any_)          > character

    item     = Delayed()
    
    seq      = (char | item)[0:]                                > sequence
    group    = Drop('(') & seq & Drop(')')
    alts     = Drop('(') & seq[2:, Drop('|')] & Drop(')')       > choice
    star     = (alts | group | char) & Drop('*')                > repeat
    plus     = (alts | group | char) & Drop('+')                > repeat2
    opt      = (alts | group | char) & Drop('?')                > option
    
    item    += alts | group | star | plus | opt
    
    expr     = (char | item)[:] & Drop(Eos())

    # Empty config here avoids loops if the default config includes
    # references to alphabets
    return expr.string_parser(config=
            Configuration(rewriters=[flatten],
                          monitors=[TraceResults(True)]))

