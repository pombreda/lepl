
from logging import basicConfig, DEBUG

from lepl import *


def stream():
    '''
    Compared to nat_lang, this focuses on the stream.  It does not use any 
    monitor.  Note multiple lines.
    '''
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
    
    with Separator(Regexp(r'\s*')):
        verbphrase  = Delayed()
        verbphrase += verb | (verbphrase & join & verbphrase)      > VerbPhrase
        det_phrase  = determiner & noun                            > DetPhrase
        simple_tp   = proper_noun | det_phrase                     > SimpleTp
        termphrase  = Delayed()
        termphrase += simple_tp | (termphrase & join & termphrase) > TermPhrase
        sentence    = termphrase & verbphrase & termphrase & Eos() > Sentence

    p = sentence.string_matcher(Configuration(rewriters=[auto_memoize]))
    results = list(p('every boy or some girl and helen and john or pat knows\n'
                     'and respects or loves every boy or some girl and pat or\n'
                     'john and helen'))
    assert len(results) == 392, len(results)  


def time():
    from timeit import Timer
    t = Timer("stream()", "from __main__ import stream")
    print(t.timeit(number=100)) 
    # 56.6
    # auto-memoize brings that down to 30 (24 for nat_lang)
    

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

    
    
