
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
Tests for the lepl.offside.regexp module.
'''

# pylint: disable-msg=C0111, R0201
# tests


#from logging import basicConfig, DEBUG, INFO, ERROR
from unittest import TestCase

from lepl.lexer.matchers import Token
#from lepl.memo import LMemo
#from lepl.rewriters import memoize
from lepl.offside.config import LineAwareConfiguration
from lepl.offside.matchers import BLine
from lepl.offside.regexp import LineAwareAlphabet, SOL, EOL
from lepl.regexp.core import Expression
from lepl.regexp.matchers import DfaRegexp
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.support import str
from lepl.trace import TraceResults


class RegexpTest(TestCase):
    
    def test_invert_bug_1(self):
        #basicConfig(level=DEBUG)
        config = LineAwareConfiguration(monitors=[TraceResults(True)])
        match = DfaRegexp('^[^c]*')
        result = list(match.match_string('abc', config))[0][0]
        assert result == ['ab'], result
        
        # these are waiting on [^...] for line aware automatically
        # excluding ^ and $
        
#    def test_invert_bug_2(self):
#        #basicConfig(level=DEBUG)
#        bad = BLine(Token('[^a]'))
#        parser = bad.string_parser(
#            LineAwareConfiguration(block_policy=2, 
#                                   rewriters=[memoize(LMemo)]))
#        result = parser('123')
#        assert result == ['123'], result
#        
#    def test_invert_bug_3(self):
#        #basicConfig(level=DEBUG)
#        bad = BLine(Token(str('[^a]')))
#        parser = bad.string_parser(
#            LineAwareConfiguration(block_policy=2, 
#                                   rewriters=[memoize(LMemo)]))
#        result = parser('123')
#        assert result == ['123'], result
#        
#    def test_invert_bug_4(self):
#        #basicConfig(level=DEBUG)
#        bad = BLine(Token('[^a]*'))
#        parser = bad.string_parser(
#            LineAwareConfiguration(block_policy=2, 
#                                   rewriters=[memoize(LMemo)]))
#        result = parser('123')
#        assert result == ['123'], result
        
    def test_invert_bug_5(self):
        #basicConfig(level=DEBUG)
        bad = BLine(Token('[^^$a]*'))
        parser = bad.string_parser(
            LineAwareConfiguration(block_policy=2, 
                                   rewriters=[],
                                   monitors=[TraceResults(True)]))
        result = parser('123')
        assert result == ['123'], result
        
    def test_invert_bug_6(self):
        #basicConfig(level=DEBUG)
        bad = BLine(Token(str('[^^$a]*')))
        parser = bad.string_parser(
            LineAwareConfiguration(block_policy=2, 
                                   rewriters=[],
                                   monitors=[TraceResults(True)]))
        result = parser(str('123'))
        assert result == [str('123')], result
        
    def test_match_1(self):
        alphabet = LineAwareAlphabet(UnicodeAlphabet.instance())
        expr = Expression.single(alphabet, '[a]').nfa()
        result = list(expr.match(str('a123')))
        assert result == [(str('label'), str('a'), str('123'))], result
        
    def test_match_2(self):
        alphabet = LineAwareAlphabet(UnicodeAlphabet.instance())
        expr = Expression.single(alphabet, '[^a]').nfa()
        result = list(expr.match(str('123a')))
        assert result == [(str('label'), str('1'), str('23a'))], result
        
    def test_match_3(self):
        alphabet = LineAwareAlphabet(UnicodeAlphabet.instance())
        expr = Expression.single(alphabet, '[^a]*').dfa()
        result = list(expr.match(str('123a')))
        assert result == [[str('label')], str('123'), str('a')], result
        
    def test_match_4(self):
        alphabet = LineAwareAlphabet(UnicodeAlphabet.instance())
        expr = Expression.single(alphabet, '[^a]*').dfa()
        result = list(expr.match([str('1'), str('a')]))
        assert result == [[str('label')], [str('1')], [str('a')]], result
        
    def test_match_5(self):
        alphabet = LineAwareAlphabet(UnicodeAlphabet.instance())
        expr = Expression.single(alphabet, '[^a]*').dfa()
        result = list(expr.match([SOL, str('1'), str('a')]))
        assert result == [[str('label')], [SOL, str('1')], [str('a')]], result
        
    def test_match_6(self):
        alphabet = LineAwareAlphabet(UnicodeAlphabet.instance())
        expr = Expression.single(alphabet, '[^^a]*').dfa()
        result = list(expr.match([SOL, str('1'), str('a')]))
        assert result == [[str('label')], [], [SOL, str('1'), str('a')]], \
            result

    def test_match_7(self):
        alphabet = LineAwareAlphabet(UnicodeAlphabet.instance())
        expr = Expression.single(alphabet, '[^^$a]*').dfa()
        result = list(expr.match([str('1'), EOL]))
        assert result == [[str('label')], [str('1')], [EOL]], \
            result
