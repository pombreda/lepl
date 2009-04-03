

from lepl.matchers import Transformable
from lepl.parser import tagged
from lepl.regexp.core import Regexp
from lepl.regexp.unicode import UnicodeAlphabet


class NfaRegexp(Transformable):
    '''
    A matcher for NFA-based regular expressions.  This will yield alternative
    matches.
    
    Typically used only in specialised situations (see `Regexp`).
    '''
    
    def __init__(self, regexp, alphabet=None):
        super(NfaRegexp, self).__init__()
        alphabet = UnicodeAlphabet() if alphabet is None else alphabet
        if not isinstance(regexp, Regexp):
            regexp = Regexp.single(regexp, alphabet)
        self._arg(regexp=regexp)
        self._arg(alphabet=alphabet)
        self.__matcher = regexp.nfa()
        self.tag(regexp)
        
    def compose(self, transform):
        return self.compose_transformation(transform.function)
    
    def compose_transformation(self, transformation):
        copy = NfaRegexp(self.regexp)
        copy.function = self.function.compose(transformation)
        return copy
        
    
    @tagged
    def __call__(self, stream_in):
        matches = self.__matcher(stream_in)
        for (terminal, match, stream_out) in matches:
            yield self.function([match], stream_in, stream_out)


class DfaRegexp(Transformable):
    '''
    A matcher for DFA-based regular expressions.  This yields a single greedy
    match.
    
    Typically used only in specialised situations (see `Regexp`).
    '''
    
    def __init__(self, regexp, alphabet=None):
        super(DfaRegexp, self).__init__()
        alphabet = UnicodeAlphabet() if alphabet is None else alphabet
        if not isinstance(regexp, Regexp):
            regexp = Regexp.single(regexp, alphabet)
        self._arg(regexp=regexp)
        self._arg(alphabet=alphabet)
        self.__matcher = regexp.dfa()
        self.tag(regexp)
        
    def compose(self, transform):
        copy = DfaRegexp(self.regexp)
        copy.function = self.function.compose(transform.function)
        return copy
    
    @tagged
    def __call__(self, stream_in):
        results = self.__matcher(stream_in)
        if results:
            (terminals, match, stream_out) = results
            yield self.function([match], stream_in, stream_out)

