class UnicodeAlphabet(Alphabet):
    '''
    An alphabet for unicode strings.
    '''
    
    def __init__(self):
        try:
            max = chr(maxunicode)
        except: # Python 2.6
            max = unichr(maxunicode)
        super(UnicodeAlphabet, self).__init__(chr(0), max)
        self._escape = '\\'
        self._escaped = '[]*()-?.+\\^$'
    
    def before(self, c): 
        '''
        Must return the character before c in the alphabet.  Never called with
        min (assuming input data are in range).
        ''' 
        return chr(ord(c)-1)
    
    def after(self, c): 
        '''
        Must return the character after c in the alphabet.  Never called with
        max (assuming input data are in range).
        ''' 
        return chr(ord(c)+1)
    
    def _escape_text(self, text):
        '''
        Escape characters in the text (ie return a suitable expression to
        match the given text as a literal value).
        '''
        return ''.join(self._escape_char(x) for x in text)
    
    def _escape_char(self, char):
        if char in self._escaped:
            return self._escape + char
        else:
            return char
    
    def fmt_intervals(self, intervals):
        '''
        This must fully describe the data in the intervals (it is used to
        hash the data).
        '''
        inrange = '-\\[]' # escaped inside []
        outrange = inrange + '*+().' # escaped everywhere
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
        return '[{0}{1}]'.format(hat, ''.join(ranges))
    
    def fmt_sequence(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        return ''.join(str(c) for c in children)
    
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


UNICODE = UnicodeAlphabet()


def _make_unicode_parser():
    '''
    Construct a parser for Unicode based expressions.
    
    We need a clear policy on backslashes.  To be as backwars compatible as
    possible I am going with:
    0 - "Escaping" means prefixing with \.
    1 - These characters are special: [, ], -, \, (, ), *, ?, ., +, ^, $.
    2 - Special characters (ie literal, or unescaped special characters) may 
        not have a meaning currently, or may only have a meaning in certain 
        contexts.
    2 - To use a special character literally, it must be escaped.
    3 - If a special character is used without an escape, in a context
        where it doesn't have a meaning, then it is an error.
    4 - If a non-special character is escaped, that is also an error.
    
    This is not the same as the Python convention, but I believe it makes
    automatic escaping of given text easier.
    '''
    
    dup = lambda x: (x, x)
    dot = lambda x: (UNICODE.min, UNICODE.max)
    invert = UNICODE.invert
    sequence = lambda x: Sequence(x, UNICODE)
    repeat = lambda x: Repeat(x, UNICODE)
    option = lambda x: Option(x, UNICODE)
    choice = lambda x: Choice(x, UNICODE)
    character = lambda x: Character(x, UNICODE)
    
    # these two definitions enforce the conditions above, providing only
    # special characters appear as literals in the grammar
    escaped  = Drop(UNICODE._escape) + Any(UNICODE._escaped)
    raw      = ~Lookahead(UNICODE._escape) + AnyBut(UNICODE._escaped)
    
    single   = escaped | raw
    
    any      = Literal('.')                                     >> dot
    pair     = single & Drop('-') & single                      > tuple
    letter   = single                                           >> dup
    
    interval = pair | letter
    brackets = Drop('[') & interval[1:] & Drop(']')
    inverted = Drop('[^') & interval[1:] & Drop(']')            >= invert      
    char     = inverted | brackets | letter | any               > character

    item     = Delayed()
    
    seq      = (char | item)[1:]                                > sequence
    group    = Drop('(') & seq & Drop(')')
    alts     = Drop('(') & seq[2:, Drop('|')] & Drop(')')       > choice
    star     = (alts | group | char) & Drop('*')                > repeat
    opt      = (alts | group | char) & Drop('?')                > option
    
    item    += alts | group | star | opt
    
    expr     = (char | item)[:] & Drop(Eos())
    parser = expr.string_parser()
    return lambda text: parser(text)

__compiled_unicode_parser = _make_unicode_parser()
'''
Cache the parser to allow efficient re-use.
'''

def unicode_single_parser(label, text):
    '''
    Parse a Unicode regular expression, returning the associated Regexp.
    '''
    return Regexp([Labelled(label, __compiled_unicode_parser(text), UNICODE)], 
                  UNICODE)


def unicode_parser(*regexps):
    '''
    Parse a set of Unicode regular expressions, returning the associated Regexp.
    '''
    return Regexp([Labelled(label, __compiled_unicode_parser(text), UNICODE)
                   for (label, text) in regexps], UNICODE)


