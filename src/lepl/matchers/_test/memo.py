
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
Tests for the lepl.memo module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import Delayed, Any, Optional, Node, Literals, Eos, Token, Or


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321
# (dude this is just a test)

    
class MemoTest(TestCase):
    
    def test_right(self):
        
        #basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += letter & Optional(seq)
        
        #print(seq)
        seq.config.clear().right_memoize().trace(True)
        p = seq.string_matcher()
        #print(p.matcher)
        
        results = list(p('ab'))
        assert len(results) == 2, len(results)
        assert results[0][0] == ['a', 'b'], results[0][0]
        assert results[1][0] == ['a'], results[1][0]
        
    
    def test_left1a(self):
        
        #basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += Optional(seq) & letter
        
        seq.config.clear().left_memoize().trace(True)
        p = seq.null_matcher()
        #print(p.matcher)
        results = list(p('ab'))
        assert len(results) == 2, len(results)
        assert results[0][0] == ['a', 'b'], results[0][0]
        assert results[1][0] == ['a'], results[1][0]
        
        
    def test_left1b(self):
        
        #basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += Optional(seq) & letter
        
        seq.config.clear().left_memoize().trace(True)
        p = seq.string_matcher()
        results = list(p('ab'))
        assert len(results) == 2, len(results)
        assert results[0][0] == ['a', 'b'], results[0][0]
        assert results[1][0] == ['a'], results[1][0]
        
    
    def test_left2(self):
        
        #basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += letter | (seq  & letter)
        
        seq.config.clear().left_memoize().trace(True)
        p = seq.string_matcher()
        results = list(p('abcdef'))
        assert len(results) == 6, len(results)
        assert results[0][0] == ['a'], results[0][0]
        assert results[1][0] == ['a', 'b'], results[1][0]
        
    
    def test_complex(self):
        
        #basicConfig(level=DEBUG)
        
        class VerbPhrase(Node): pass
        class DetPhrase(Node): pass
        class SimpleTp(Node): pass
        class TermPhrase(Node): pass
        class Sentence(Node): pass
        
        verb        = Literals('knows', 'respects', 'loves')         > 'verb'
        join        = Literals('and', 'or')                          > 'join'
        proper_noun = Literals('helen', 'john', 'pat')               > 'proper_noun'
        determiner  = Literals('every', 'some')                      > 'determiner'
        noun        = Literals('boy', 'girl', 'man', 'woman')        > 'noun'
        
        verbphrase  = Delayed()
        verbphrase += verb | (verbphrase // join // verbphrase)      > VerbPhrase
        det_phrase  = determiner // noun                             > DetPhrase
        simple_tp   = proper_noun | det_phrase                       > SimpleTp
        termphrase  = Delayed()
        termphrase += simple_tp | (termphrase // join // termphrase) > TermPhrase
        sentence    = termphrase // verbphrase // termphrase & Eos() > Sentence
    
        sentence.config.clear().left_memoize().trace()
        p = sentence.string_matcher()
        
        text = 'every boy or some girl and helen and john or pat knows ' \
               'and respects or loves every boy or some girl and pat or ' \
               'john and helen'
#        text = 'every boy loves helen'
        count = 0
        for _meaning in p(text):
            count += 1
            if count < 3:
                #print(_meaning[0][0])
                pass
        #print(count)
        assert count == 392, count
    
    
class RecursionTest(TestCase):
    
    def right(self):
        matcher = Delayed()
        matcher += Any() & Optional(matcher)
        return matcher
    
    def right_token(self, contents=False):
        matcher = Delayed()
        inner = Token(Any())
        if contents:
            inner = inner(Or('a', 'b'))
        matcher += inner & Optional(matcher)
        return matcher
    
    def left(self):
        matcher = Delayed()
        matcher += Optional(matcher) & Any()
        return matcher
    
    def left_token(self, contents=False):
        matcher = Delayed()
        inner = Token(Any())
        if contents:
            inner = inner(Or('a', 'b'))
        matcher += Optional(matcher) & inner
        return matcher
    
    def do_test(self, parser):
        result = parser('ab')
        assert result == ['a', 'b'], result
        result = parser('aa')
        assert result == ['a', 'a'], result
        result = parser('aaa')
        assert result == ['a', 'a', 'a'], result
        result = parser('aba')
        assert result == ['a', 'b', 'a'], result
        
    def test_right_string(self):
        matcher = self.right()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_right_string(self):
        matcher = self.right()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_right_null(self):
        matcher = self.right()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.null_parser())

    def test_right_token_string(self):
        #basicConfig(level=DEBUG)
        matcher = self.right_token()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_right_token_null(self):
        #basicConfig(level=DEBUG)
        matcher = self.right_token()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.null_parser())
        
    def test_right_token_string_content(self):
        #basicConfig(level=DEBUG)
        matcher = self.right_token(True)
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_right_token_null_content(self):
        #basicConfig(level=DEBUG)
        matcher = self.right_token(True)
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.null_parser())
        
    def test_right_string_clear(self):
        matcher = self.right()
        matcher.config.clear().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_right_null_clear(self):
        matcher = self.right()
        matcher.config.clear().auto_memoize(full=True).trace(True)
        self.do_test(matcher.null_parser())

    def test_right_token_string_clear(self):
        #basicConfig(level=DEBUG)
        matcher = self.right_token()
        matcher.config.clear().auto_memoize(full=True).lexer().trace(True)
        self.do_test(matcher.string_parser())
        
    def test_right_token_null_clear(self):
        #basicConfig(level=DEBUG)
        matcher = self.right_token()
        matcher.config.clear().auto_memoize(full=True).lexer().trace(True)
        self.do_test(matcher.null_parser())
        
    def test_right_token_string_clear_content(self):
        #basicConfig(level=DEBUG)
        matcher = self.right_token(True)
        matcher.config.clear().auto_memoize(full=True).lexer().trace(True)
        self.do_test(matcher.string_parser())
        
    def test_right_token_null_clear_content(self):
        #basicConfig(level=DEBUG)
        matcher = self.right_token(True)
        matcher.config.clear().auto_memoize(full=True).lexer().trace(True)
        self.do_test(matcher.null_parser())
        
    def test_left_string(self):
        matcher = self.left()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_left_null(self):
        matcher = self.left()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.null_parser())

    def test_left_token_string(self):
        matcher = self.left_token()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_left_token_null(self):
        matcher = self.left_token()
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.null_parser())

    def test_left_token_string_content(self):
        matcher = self.left_token(True)
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_left_token_null_content(self):
        matcher = self.left_token(True)
        matcher.config.no_full_match().auto_memoize(full=True).trace(True)
        self.do_test(matcher.null_parser())

    def test_left_string_clear(self):
        matcher = self.left()
        matcher.config.clear().auto_memoize(full=True).trace(True)
        self.do_test(matcher.string_parser())
        
    def test_left_null_clear(self):
        matcher = self.left()
        matcher.config.clear().auto_memoize(full=True).trace(True)
        self.do_test(matcher.null_parser())

    def test_left_token_string_clear(self):
        matcher = self.left_token()
        matcher.config.clear().auto_memoize(full=True).lexer().trace(True)
        self.do_test(matcher.string_parser())
        
    def test_left_token_null_clear(self):
        matcher = self.left_token()
        matcher.config.clear().auto_memoize(full=True).lexer().trace(True)
        self.do_test(matcher.null_parser())

    def test_left_token_string_clear_content(self):
        matcher = self.left_token(True)
        matcher.config.clear().auto_memoize(full=True).lexer().trace(True)
        self.do_test(matcher.string_parser())
        
    def test_left_token_null_clear_content(self):
        matcher = self.left_token(True)
        matcher.config.clear().auto_memoize(full=True).lexer().trace(True)
        self.do_test(matcher.null_parser())

        