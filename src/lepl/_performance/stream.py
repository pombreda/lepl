
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

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401, R0903, R0914
#@PydevCodeAnalysisIgnore


#from logging import basicConfig, DEBUG

from lepl import *


def matcher():
    '''
    Compared to nat_lang, this focuses on the stream.  It does not use any 
    monitor.  Note multiple lines.
    '''
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
    
    with Separator(Regexp(r'\s*')):
        verbphrase  = Delayed()
        verbphrase += verb | (verbphrase & join & verbphrase)      > VerbPhrase
        det_phrase  = determiner & noun                            > DetPhrase
        simple_tp   = proper_noun | det_phrase                     > SimpleTp
        termphrase  = Delayed()
        termphrase += simple_tp | (termphrase & join & termphrase) > TermPhrase
        sentence    = termphrase & verbphrase & termphrase & Eos() > Sentence

    sentence.config
    p = sentence.string_matcher()
    print(repr(p.matcher))
    return p

p = matcher()

def stream():
    results = list(p('every boy or some girl and helen and john or pat knows\n'
                     'and respects or loves every boy or some girl and pat or\n'
                     'john and helen'))
    assert len(results) == 392, len(results)  


def time():
    from timeit import Timer
    t = Timer("stream()", "from __main__ import stream")
    print(t.timeit(number=100)) 
    # new (functions etc) system, no compile
    # 30.3 default - difficult to get faster than that
    # now 28.3 with fixed rewriting


def profile():
    '''
import pstats
p=pstats.Stats('stream.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(20)
    '''
    import cProfile
    cProfile.run('stream()', 'stream.prof')

if __name__ == '__main__':
    time()
#    profile()
#    stream()

    
    
