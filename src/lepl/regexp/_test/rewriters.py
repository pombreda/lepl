
from unittest import TestCase

from lepl import *
from lepl.regexp.rewriters import regexp_rewriter
from lepl.regexp.unicode import UNICODE


class RewriteTest(TestCase):
    
    def test_any(self):
        char = Any()
        matcher = char.null_matcher(Configuration(rewriters=[regexp_rewriter(UNICODE)]))
        results = list(matcher('abc'))
        assert results == [(['a'], 'bc')], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
    def test_or(self):
        rx = Any('a') | Any('b') 
        matcher = rx.null_matcher(Configuration(rewriters=[regexp_rewriter(UNICODE)]))
        print(matcher.matcher.describe)
        results = list(matcher('bq'))
        assert results == [(['b'], 'q')], results
        results = list(matcher('aq'))
        assert results == [(['a'], 'q')], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
    def test_and(self):
        rx = Any('a') + Any('b') 
        matcher = rx.null_matcher(Configuration(rewriters=[regexp_rewriter(UNICODE)]))
        print(matcher.matcher.describe)
        results = list(matcher('abq'))
        assert results == [(['ab'], 'q')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    
       