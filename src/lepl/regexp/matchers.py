

from lepl.matchers import Transformable
from lepl.parser import tagged
from lepl.regexp.core import Regexp
from lepl.regexp.unicode import UNICODE


class NfaRegexp(Transformable):
    
    def __init__(self, regexp, alphabet=UNICODE):
        super(NfaRegexp, self).__init__()
        if not isinstance(regexp, Regexp):
            regexp = Regexp.single(regexp, alphabet)
        self._arg(regexp=regexp)
        self._arg(alphabet=alphabet)
        self.__matcher = regexp.nfa()
        self.tag(regexp)
        
    def compose(self, transform):
        copy = NfaRegexp(self.regexp)
        copy.function = self._compose(transform.function)
        return copy
    
    @tagged
    def __call__(self, stream0):
        matches = self.__matcher(stream0)
        for (terminal, match, stream1) in matches:
            yield ([match], stream1)


class DfaRegexp(Transformable):
    
    def __init__(self, regexp, alphabet=UNICODE):
        super(DfaRegexp, self).__init__()
        if not isinstance(regexp, Regexp):
            regexp = Regexp.single(regexp, alphabet)
        self._arg(regexp=regexp)
        self._arg(alphabet=alphabet)
        self.__matcher = regexp.dfa()
        self.tag(regexp)
        
    def compose(self, transform):
        copy = DfaRegexp(self.regexp)
        copy.function = self._compose(transform.function)
        return copy
    
    @tagged
    def __call__(self, stream0):
        results = self.__matcher(stream0)
        if results:
            (terminals, match, stream1) = results
            yield ([match], stream1)

