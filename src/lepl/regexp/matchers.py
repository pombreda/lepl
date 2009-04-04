

from lepl.matchers import Transformable
from lepl.parser import tagged
from lepl.regexp.core import Regexp
from lepl.regexp.unicode import UnicodeAlphabet


class BaseRegexp(Transformable):
    
    def __init__(self, regexp, alphabet=None):
        super(BaseRegexp, self).__init__()
        self._arg(regexp=regexp)
        self._arg(alphabet=alphabet)
        self.tag(regexp)
        
    def compose(self, transform):
        return self.compose_transformation(transform.function)
    
    def compose_transformation(self, transformation):
        copy = type(self)(self.regexp)
        copy.function = self.function.compose(transformation)
        return copy
    

class NfaRegexp(BaseRegexp):
    '''
    A matcher for NFA-based regular expressions.  This will yield alternative
    matches.
    
    Typically used only in specialised situations (see `Regexp`).
    '''
    
    def __init__(self, regexp, alphabet=None):
        if not isinstance(regexp, Regexp):
            regexp = Regexp.single(regexp, alphabet)
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        super(NfaRegexp, self).__init__(regexp, alphabet)
        self.__matcher = regexp.nfa()

    @tagged
    def __call__(self, stream_in):
        matches = self.__matcher(stream_in)
        for (terminal, match, stream_out) in matches:
            yield self.function([match], stream_in, stream_out)

        

class DfaRegexp(BaseRegexp):
    '''
    A matcher for DFA-based regular expressions.  This yields a single greedy
    match.
    
    Typically used only in specialised situations (see `Regexp`).
    '''
    
    def __init__(self, regexp, alphabet=None):
        if not isinstance(regexp, Regexp):
            regexp = Regexp.single(regexp, alphabet)
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        super(DfaRegexp, self).__init__(regexp, alphabet)
        self.__matcher = regexp.dfa()

    @tagged
    def __call__(self, stream_in):
        match = self.__matcher(stream_in)
        if match is not None:
            (terminals, match, stream_out) = match
            yield self.function([match], stream_in, stream_out)

