
from logging import basicConfig, INFO, DEBUG
from unittest import TestCase

from lepl import *
from lepl.parser import string_parser, string_matcher


class MemoTest(TestCase):
    
    def test_right(self):
        
        basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += letter & Optional(seq)
        
        p = string_matcher(seq, 
                Configuration(rewriters=[memoize(RMemo)], 
                              monitors=[TraceResults(True)]))
        results = list(p('ab'))
        print(results)
        assert len(results) == 2, len(results)
        assert results[0][0] == ['a', 'b'], results[0][0]
        assert results[1][0] == ['a'], results[1][0]
        
    
    def test_left1a(self):
        
        basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += Optional(seq) & letter
        
        p = seq.null_matcher(
                Configuration(rewriters=[memoize(LMemo)], 
                              monitors=[TraceResults(True)]))
        results = list(p('ab'))
        print(results)
        assert len(results) == 2, len(results)
        assert results[0][0] == ['a', 'b'], results[0][0]
        assert results[1][0] == ['a'], results[1][0]
        
        
    def test_left1b(self):
        
        basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += Optional(seq) & letter
        
        p = seq.string_matcher(
                Configuration(rewriters=[memoize(LMemo)], 
                              monitors=[TraceResults(True)]))
        results = list(p('ab'))
        print(results)
        assert len(results) == 2, len(results)
        assert results[0][0] == ['a', 'b'], results[0][0]
        assert results[1][0] == ['a'], results[1][0]
        
    
    def test_left2(self):
        
        basicConfig(level=DEBUG)
        
        seq    = Delayed()
        letter = Any()
        seq   += letter | (seq  & letter)
        
        p = string_matcher(seq, 
                Configuration(rewriters=[memoize(LMemo)], 
                              monitors=[TraceResults(True)]))
        results = list(p('abcdef'))
        print(results)
        assert len(results) == 6, len(results)
        assert results[0][0] == ['a'], results[0][0]
        assert results[1][0] == ['a', 'b'], results[1][0]
        
    
    def test_complex(self):
        
        basicConfig(level=DEBUG)
        
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
    
        p = string_matcher(sentence, 
                Configuration(rewriters=[memoize(LMemo)], 
                              monitors=[TraceResults(False)]))
        
        count = 0
        for meaning in p('every boy or some girl and helen and john or pat knows '
                         'and respects or loves every boy or some girl and pat or '
                         'john and helen'):
#            print(meaning[0][0])
            count += 1
        print(count)
    
    