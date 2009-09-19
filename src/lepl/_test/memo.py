
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

from lepl import Configuration, RMemo, Delayed, Any, TraceResults, memoize, \
    Optional, LMemo, Node, Literals, Eos


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321
# (dude this is just a test)

    
class MemoTest(TestCase):
    
    def test_right(self):
        
        #basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += letter & Optional(seq)
        
        #print(seq)
        p = seq.string_matcher( 
                Configuration(rewriters=[memoize(RMemo)], 
                              monitors=[TraceResults(True)]))
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
        
        p = seq.null_matcher(
                Configuration(rewriters=[memoize(LMemo)], 
                              monitors=[TraceResults(True)]))
        results = list(p('ab'))
        assert len(results) == 2, len(results)
        assert results[0][0] == ['a', 'b'], results[0][0]
        assert results[1][0] == ['a'], results[1][0]
        
        
    def test_left1b(self):
        
        #basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += Optional(seq) & letter
        
        p = seq.string_matcher(
                Configuration(rewriters=[memoize(LMemo)], 
                              monitors=[TraceResults(True)]))
        results = list(p('ab'))
        assert len(results) == 2, len(results)
        assert results[0][0] == ['a', 'b'], results[0][0]
        assert results[1][0] == ['a'], results[1][0]
        
    
    def test_left2(self):
        
        #basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += letter | (seq  & letter)
        
        p = seq.string_matcher(Configuration(rewriters=[memoize(LMemo)], 
                                             monitors=[TraceResults(True)]))
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
    
        p = sentence.string_matcher(
                    Configuration(rewriters=[memoize(LMemo)], 
                                  monitors=[TraceResults(False)]))
        
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
    