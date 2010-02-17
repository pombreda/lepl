
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
Performance related tests.
'''

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401, R0914, R0903
#@PydevCodeAnalysisIgnore


#from logging import basicConfig, DEBUG

from lepl import *


def natural_language():
    '''
    This focuses on the LMemo cache.  It does not use any monitor or stream.
    '''
    
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

    p = sentence.null_matcher(Configuration)
    #p = sentence.null_matcher(Configuration.dfa())
    #p = sentence.null_matcher()
    print(p.matcher)
    for _i in range(1000):
        assert len(list(p('every boy or some girl and helen and john or pat knows '
                          'and respects or loves every boy or some girl and pat or '
                          'john and helen'))) == 392  


def natural_language2():
    '''
    This focuses on the LMemo cache.  It does not use any monitor or stream.
    '''
    
    #basicConfig(level=DEBUG)
    
    class VerbPhrase(Node): pass
    class DetPhrase(Node): pass
    class SimpleTp(Node): pass
    class TermPhrase(Node): pass
    class Sentence(Node): pass
    
    t           = Token('[a-z]+')
    
    verb        = t(Literals('knows', 'respects', 'loves'))    > 'verb'
    join        = t(Literals('and', 'or'))                     > 'join'
    proper_noun = t(Literals('helen', 'john', 'pat'))          > 'proper_noun'
    determiner  = t(Literals('every', 'some'))                 > 'determiner'
    noun        = t(Literals('boy', 'girl', 'man', 'woman'))   > 'noun'
    
    verbphrase  = Delayed()
    verbphrase += verb | (verbphrase & join & verbphrase)      > VerbPhrase
    det_phrase  = determiner & noun                            > DetPhrase
    simple_tp   = proper_noun | det_phrase                     > SimpleTp
    termphrase  = Delayed()
    termphrase += simple_tp | (termphrase & join & termphrase) > TermPhrase
    sentence    = termphrase & verbphrase & termphrase & Eos() > Sentence

    p = sentence.null_matcher(Configuration.tokens())
    print(p.matcher)
    for _i in range(1000):
        assert len(list(p('every boy or some girl and helen and john or pat knows '
                          'and respects or loves every boy or some girl and pat or '
                          'john and helen'))) == 392  


def time():
    from timeit import Timer
    t = Timer("naturalLanguage()", "from __main__ import naturalLanguage")
    print(t.timeit(number=1))
    # without compilation, and with smart dfa switch:
    # with dfa: 12.4
    # without dfa: 5.7
    # default: 12.4
    # with tokens: 13.3
    
    # all numbers below included compilation!
    # using LMemo:
    # 6.3, 6.6 for 2.0 on laptop
    # 5.3 after simplifying generator wrapper
    # using auto_memoize 48 -> 34 (44->31)
    # Or as Transformable -> 24
    # RMemo as Transformable -> 30
    # Both as Transformable -> 27
    # So not worth making RMemo transformable(!)
    # Seem to be back at 27 for auto_memoize(False) after fixing bugs
    # and slightly worse (28) for auto_memoize(True)
    # DFA (and so NFA) makes things slower (40)
    # (expected - converting literal to FSA)
    

def profile():
    '''
import pstats
p=pstats.Stats('nat_lang.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('natural_language()', 'nat_lang.prof')

if __name__ == '__main__':
    time()
#    profile()
#    natural_language()

    
    
    