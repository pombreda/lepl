
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.offside.config import LineAwareConfiguration
from lepl.regexp.matchers import DfaRegexp


class RegexpTest(TestCase):
    
    def test_start(self):
        basicConfig(level=DEBUG)
        config = LineAwareConfiguration()
        match = DfaRegexp('^a*')
        print(list(match.match_string('abc', config)))
        
    