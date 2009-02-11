
from unittest import TestCase

from lepl import *
from lepl.matchers import Literals
from lepl.memo import LMemo
from lepl.parser import string_parser


def main():
    
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
    sentence    = termphrase // verbphrase // termphrase         > Sentence

    p = string_parser(sentence, memoizers=[LMemo])
    print(p.matcher)
    
    for meaning in p('every boy or some girl and helen and john or pat knows '
                     'and respects or loves every boy or some girl and pat or '
                     'john and helen'):
        print(p)

if __name__ == '__main__':
    main()
    