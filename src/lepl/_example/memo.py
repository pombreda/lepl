
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
        