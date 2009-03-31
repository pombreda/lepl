
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class MatchersTest(TestCase):
    
    def test_nfa(self):
#        basicConfig(level=DEBUG)
        
        with Separator(~Regexp(r'\s*')):
            word = NfaRegexp('[A-Z][a-z]*')
            phrase = word[1:]
            
        results = list(Trace(phrase).match('Abc'))
        assert len(results) == 3, results
        assert results[0][0] == ['Abc'], results
        assert results[1][0] == ['Ab'], results
        assert results[2][0] == ['A'], results
        
        results = list(phrase.match('AbcDef'))
        assert len(results) == 6, results
        assert results[0][0] == ['Abc', 'Def'], results
        
        results = list(phrase.match('Abc Def'))
        assert len(results) == 6, results
        
    def test_dfa(self):
        basicConfig(level=DEBUG)
        
        with Separator(~Regexp(r'\s*')):
            word = DfaRegexp('[A-Z][a-z]*')
            phrase = word[1:]
            
        results = list(Trace(phrase).match('Abc'))
        assert len(results) == 1, results
        assert results[0][0] == ['Abc'], results
        
        results = list(phrase.match('AbcDef'))
        assert len(results) == 2, results
        assert results[0][0] == ['Abc', 'Def'], results
        
        results = list(phrase.match('Abc Def'))
        assert len(results) == 2, results
        

