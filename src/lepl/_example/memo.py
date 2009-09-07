
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,R0903,R0914
# (the code style is for documentation, not "real")
#@PydevCodeAnalysisIgnore

'''
Examples from the documentation.
'''

from lepl import *
from lepl._example.support import Example


class MemoExample(Example):
    
    def test_right(self):
        
        matcher = Any('a')[:] & Any('a')[:] & RMemo(Any('b')[4])
        self.examples([(lambda: len(list(matcher.match('aaaabbbb'))), "5")])
    
    def test_left(self):
        
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
    
        p = sentence.null_matcher(
                Configuration(rewriters=[memoize(LMemo)], 
                              monitors=[TraceResults(False)]))
        self.examples([(lambda: 
            len(list(p('every boy or some girl and helen and john or pat knows '
                       'and respects or loves every boy or some girl and pat or '
                      'john and helen'))),
            "392")])
        