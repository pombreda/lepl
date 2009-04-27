
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
Some intermediate classes that support parsers for objects that can be
converted to strings using str().
'''

from lepl.regexp.core \
    import BaseAlphabet, Character, Sequence, Choice, Repeat, Option, \
    Regexp, Labelled
from lepl.config import Configuration



class StrAlphabet(BaseAlphabet):
    '''
    An alphabet for unicode strings.
    '''
    
    def __init__(self, min, max, escape='\\', escaped='[]*()-?.+\\^$|'):
        super(StrAlphabet, self).__init__(min, max)
        self._escape = escape if escape else ''
        self._escaped = escaped if escaped else []
        self.__parser = make_str_parser(self)
    
    def _escape_text(self, text):
        '''
        Escape characters in the text (ie return a suitable expression to
        match the given text as a literal value).
        '''
        return ''.join(self._escape_char(x) for x in text)
    
    def _escape_char(self, char):
        if self._escape is not None and str(char) in self._escaped:
            return self._escape + str(char)
        else:
            return str(char)
    
    def fmt_intervals(self, intervals):
        '''
        This must fully describe the data in the intervals (it is used to
        hash the data).
        '''
        ranges = []
        if len(intervals) == 1:
            if intervals[0][0] == intervals[0][1]:
                return self._escape_char(intervals[0][0])
            elif intervals[0][0] == self.min and intervals[0][1] == self.max:
                return '.'
        if len(intervals) > 1 and intervals[0][0] == self.min:
            intervals = self.invert(intervals)
            hat = '^'
        else:
            hat = ''
        for (a, b) in intervals:
            if a == b:
                ranges.append(self._escape_char(a))
            else:
                ranges.append('{0!s}-{1!s}'.format(
                                self._escape_char(a), self._escape_char(b)))
        return '[{0}{1}]'.format(hat, self.join(ranges))
    
    def fmt_sequence(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        return self.join(str(c) for c in children)
    
    def fmt_repeat(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        s = self.fmt_sequence(children)
        if len(children) == 1 and type(children[0]) in (Character, Choice):
            return s + '*'
        else:
            return '({0})*'.format(s)

    def fmt_choice(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        return '({0})'.format('|'.join(self.fmt_sequence(child) 
                                       for child in children))

    def fmt_option(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        s = self.fmt_sequence(children)
        if len(children) == 1 and type(children[0]) in (Character, Choice):
            return s + '?'
        else:
            return '({0})?'.format(s)
        
    def join(self, chars):
        return ''.join(chars)
    
    def from_char(self, char):
        '''
        This must convert a single character.
        '''
        return char
    
    def parse(self, regexp):
        '''
        Generate a Sequence from the given text.
        '''
        return self.__parser(regexp)
       

def make_str_parser(alphabet):
    '''
    Construct a parser for string based expressions.
    
    We need a clear policy on backslashes.  To be as backwards compatible as
    possible I am going with:
    
      0. "Escaping" means prefixing with \.

      1. These characters are special: [, ], -, \, (, ), *, ?, ., +, ^, $, |.

      2. Special characters (ie literal, or unescaped special characters) may 
         not have a meaning currently, or may only have a meaning in certain 
         contexts.

      3. To use a special character literally, it must be escaped.

      4. If a special character is used without an escape, in a context
         where it doesn't have a meaning, then it is an error.

      5. If a non-special character is escaped, that is also an error.
    
    This is not the same as the Python convention, but I believe it makes
    automatic escaping of given text easier.
    '''
    
    # Avoid dependency loops
    from lepl.matchers import Drop, Any, Lookahead, AnyBut, Literal, Delayed, Eos
    
    dup = lambda x: (alphabet.from_char(x), alphabet.from_char(x))
    tup = lambda x: (alphabet.from_char(x[0]), alphabet.from_char(x[1]))
    dot = lambda x: (alphabet.min, alphabet.max)
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
    escaped  = Drop(alphabet._escape) + Any(alphabet._escaped)
    raw      = ~Lookahead(alphabet._escape) + AnyBut(alphabet._escaped)
    
    single   = escaped | raw
    
    any      = Literal('.')                                     >> dot
    letter   = single                                           >> dup
    pair     = single & Drop('-') & single                      > tup
    
    interval = pair | letter
    brackets = Drop('[') & interval[1:] & Drop(']')
    inverted = Drop('[^') & interval[1:] & Drop(']')            >= invert      
    char     = inverted | brackets | letter | any               > character

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
    parser = expr.string_parser(config=Configuration())
    return lambda text: parser(text)

