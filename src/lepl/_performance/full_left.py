
from logging import basicConfig, DEBUG
from random import choice, random

from lepl import *


def full_left():
    '''
    '''
    basicConfig(level=DEBUG)
    ab  = Delayed()
    with Separator(Regexp(r'\s*')):
        ab += (ab & 'b') | 'a'
#        ab += 'a' | (ab & 'b')
    p = (ab & Eos()).string_matcher(Configuration(rewriters=[memoize(LMemo)]
#                                                  ,monitors=[TraceResults(True)]
                                                  ))
    results = list(p('a' + ('\nb' * 100)))
    assert len(results) == 1
    print('done')


def time():
    from timeit import Timer
    t = Timer("full_left()", "from __main__ import full_left")
    print(t.timeit(number=10)) 
    # 17.6 for 10
    # 0.6 when rewritten 'a' | (ab & 'b')
    

def profile():
    '''
import pstats
p=pstats.Stats('full_left.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(20)
    '''
    import cProfile
    cProfile.run('full_left()', 'full_left.prof')

if __name__ == '__main__':
    time()
#    profile()
#    full_left()

    
    
