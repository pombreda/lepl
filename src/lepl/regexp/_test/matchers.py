
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
Tests for the lepl.regexp.matchers module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import Separator, Regexp, NfaRegexp, Trace, DfaRegexp


# pylint: disable-msg=C0103, C0111, C0301
# (dude this is just a test)


class MatchersTest(TestCase):
    
    def test_nfa(self):
        #basicConfig(level=DEBUG)
        
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
        #basicConfig(level=DEBUG)
        
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
        


