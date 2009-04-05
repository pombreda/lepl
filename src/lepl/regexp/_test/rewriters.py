
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *
from lepl.regexp.rewriters import regexp_rewriter
from lepl.regexp.unicode import UnicodeAlphabet


UNICODE = UnicodeAlphabet.instance()


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
        results = list(matcher('bq'))
        assert results == [(['b'], 'q')], results
        results = list(matcher('aq'))
        assert results == [(['a'], 'q')], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
    def test_and(self):
        rx = Any('a') + Any('b') 
        matcher = rx.null_matcher(Configuration(rewriters=[regexp_rewriter(UNICODE)]))
        results = list(matcher('abq'))
        assert results == [(['ab'], 'q')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    def test_literal(self):
        rx = Literal('abc')
        matcher = rx.null_matcher(Configuration(rewriters=[regexp_rewriter(UNICODE)]))
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        results = list(matcher('abcd'))
        assert results == [(['abc'], 'd')], results
        
        rx = Literal('abc') >> (lambda x: x+'e')
        matcher = rx.null_matcher(Configuration(rewriters=[compose_transforms,
                                                           regexp_rewriter(UNICODE)]))
        results = list(matcher('abcd'))
        assert results == [(['abce'], 'd')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    def test_dfs(self):
        expected = [(['abcd'], ''), (['abc'], 'd'), (['ab'], 'cd'), 
                    (['a'], 'bcd'), ([], 'abcd')]
        rx = Any()[:, ...]
        # do un-rewritten to check whether [] or [''] is correct
        matcher = rx.null_matcher(Configuration())
        results = list(matcher('abcd'))
        assert results == expected, results
        matcher = rx.null_matcher(Configuration(rewriters=[regexp_rewriter(UNICODE)]))
        results = list(matcher('abcd'))
        assert results == expected, results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
    
    def test_complex(self):
        basicConfig(level=DEBUG)
        rx = Literal('foo') | (Literal('ba') + Any('a')[1:,...])
        matcher = rx.null_matcher(Configuration(rewriters=[regexp_rewriter(UNICODE)]))
        results = list(matcher('foo'))
        assert results == [(['foo'], '')], results
        results = list(matcher('baaaaax'))
        assert results == [(['baaaaa'], 'x'), (['baaaa'], 'ax'), 
                           (['baaa'], 'aax'), (['baa'], 'aaax')], results
        results = list(matcher('ba'))
        assert results == [], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
