
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
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
Tests for the lepl.regexp.rewriters module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import Any, NfaRegexp, Literal, Add, And, Integer, Float, Word, Star


# pylint: disable-msg=C0103, C0111, C0301, C0324
# (dude this is just a test)


class RewriteTest(TestCase):
    
    def test_any(self):
        #basicConfig(level=DEBUG)
        char = Any()
        char.config.compile_to_nfa(force=True).no_full_match()
        matcher = char.null_matcher()
        results = list(matcher('abc'))
        assert results == [(['a'], 'bc')], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
    def test_or(self):
        #basicConfig(level=DEBUG)
        rx = Any('a') | Any('b') 
        rx.config.compile_to_nfa(force=True).no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('bq'))
        assert results == [(['b'], 'q')], results
        results = list(matcher('aq'))
        assert results == [(['a'], 'q')], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
    def test_plus(self):
        rx = Any('a') + Any('b') 
        rx.config.compile_to_nfa(force=True).no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('abq'))
        assert results == [(['ab'], 'q')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    def test_add(self):
        rx = Add(And(Any('a'), Any('b'))) 
        rx.config.compile_to_nfa(force=True).no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('abq'))
        assert results == [(['ab'], 'q')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    def test_literal(self):
        rx = Literal('abc')
        rx.config.compile_to_nfa(force=True).no_full_match()
        matcher = rx.null_matcher()
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        results = list(matcher('abcd'))
        assert results == [(['abc'], 'd')], results
        
        rx = Literal('abc') >> (lambda x: x+'e')
        rx.config.compose_transforms().compile_to_nfa(force=True).no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('abcd'))
        assert results == [(['abce'], 'd')], results
        print(repr(matcher.matcher))
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    def test_dfs(self):
        expected = [(['abcd'], ''), (['abc'], 'd'), (['ab'], 'cd'), 
                    (['a'], 'bcd'), ([], 'abcd')]
        rx = Any()[:, ...]
        # do un-rewritten to check whether [] or [''] is correct
        rx.config.clear()
        matcher = rx.null_matcher()
        results = list(matcher('abcd'))
        assert results == expected, results
        
        rx.config.compile_to_nfa()
        matcher = rx.null_matcher()
        results = list(matcher('abcd'))
        assert results == expected, results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
    
    def test_complex(self):
        #basicConfig(level=DEBUG)
        rx = Literal('foo') | (Literal('ba') + Any('a')[1:,...])
        rx.config.compile_to_nfa().no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('foo'))
        assert results == [(['foo'], '')], results
        results = list(matcher('baaaaax'))
        assert results == [(['baaaaa'], 'x'), (['baaaa'], 'ax'), 
                           (['baaa'], 'aax'), (['baa'], 'aaax')], results
        results = list(matcher('ba'))
        assert results == [], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe

    def test_integer(self):
        rx = Integer()
        rx.config.compile_to_nfa().no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('12x'))
        assert results == [(['12'], 'x'), (['1'], '2x')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    def test_float(self):
        rx = Float()
        rx.config.compile_to_nfa().no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('1.2x'))
        assert results == [(['1.2'], 'x'), (['1.'], '2x'), (['1'], '.2x')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    def test_star(self):
        rx = Add(Star('a')) 
        rx.config.compile_to_nfa().no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('aa'))
        assert results == [(['aa'], ''), (['a'], 'a'), ([], 'aa')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        
    def test_word(self):
        #basicConfig(level=DEBUG)
        rx = Word('a')
        rx.config.compile_to_nfa().no_full_match()
        matcher = rx.null_matcher()
        results = list(matcher('aa'))
        assert results == [(['aa'], ''), (['a'], 'a')], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.describe
        