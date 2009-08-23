

from lepl.offside.support import LineAwareException
from lepl.regexp.str import StrAlphabet


START = '^'
END = '$'


def token_factory(str_, cmp):
    
    class Token(object):
        
        __slots__ = ()
        
        def __cmp__(self, other):
            if other is self:
                return 0
            return cmp
    
        def __str__(self):
            return str_


def line_aware_alphabet_factory(base_):
    
    if not isinstance(base, StrAlphabet):
        raise LineAwareException('Only StrAlphabet subclasses supported')
    
    SOL = token_factory(START, -1)
    EOL = token_factory(END, 1)
    
    class LineAwareAlphabet(StrAlphabet):
        
        base = base_
        
        def __init(self):
            super(LineAwareAlphabet, self).__init__(SOL, EOL,
                                    parser_factory=make_line_aware_parser)
            
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
    
    fullchar = single | sol | eol                               >> dup
    any_     = Literal('.')                                     >> dot
    letter   = single                                           >> dup
    pair     = single & Drop('-') & single                      > tup
    
    interval = pair | letter
    brackets = Drop('[') & interval[1:] & Drop(']')
    inverted = Drop('[^') & interval[1:] & Drop(']')            >= invert      
    char     = inverted | brackets | fullchar | any_            > character

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
    return expr.string_parser(config=Configuration())

