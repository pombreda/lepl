

from lepl.config import Configuration
from lepl.offside.regexp import LineAwareAlphabet
from lepl.offside.stream import line_aware_stream_factory_factory
from lepl.regexp.matchers import BaseRegexp
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.rewriters import fix_arguments


class LineAwareConfiguration(Configuration):
    
    def __init__(self, rewriters=None, monitors=None, alphabet=None):
        if rewriters is None:
            rewriters = []
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        alphabet = LineAwareAlphabet(alphabet)
        rewriters.append(fix_arguments(BaseRegexp, alphabet=alphabet))
        stream_factory = line_aware_stream_factory_factory(alphabet)
        super(LineAwareConfiguration, self).__init__(
                                    rewriters=rewriters, monitors=monitors, 
                                    stream_factory=stream_factory)

