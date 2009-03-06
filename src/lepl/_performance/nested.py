
from logging import basicConfig, DEBUG
from random import choice, random

from lepl import *


def make_data(size):
    '''
    Generate a string about 2^(size+1) in size of nested parens with newlines.
    '''
    data = ""
    for i in range(size):
        if choice([True, False]):
            data = '(' + data + ')' + data
        else:
            data = data + '(' + data + ')'
        if not data.endswith('\n') and len(data) > 10:
            data += '\n'
    return data


def right():
    pair = Delayed()
    with Separator(Regexp(r'\s*')):
        pair += '(' & Optional(pair) & ')' & Optional(pair)
    p = pair.string_matcher(Configuration(rewriters=[memoize(RMemo)]))
    results = list(p(make_data(10)))
    print(len(results))


def left():
    '''
    This hammers the stream length method.
    
    Hmmm.  No it doesn't.  It does many more iterations than RMemo because it 
    has to "bottom out".  
    '''
    pair = Delayed()
    with Separator(Regexp(r'\s*')):
        pair += Optional(pair) & '(' & Optional(pair) & ')' 
    p = pair.string_matcher(Configuration(rewriters=[memoize(LMemo)]))
    results = list(p(make_data(6)))
    print(len(results))


def time(name='right'):
    from timeit import Timer
    t = Timer("{0}()".format(name), "from __main__ import {0}".format(name))
    print(t.timeit(number=10)) 
    # right - 16.2 for 10
    # left - 82.5 for 6 (!)
    

def profile(name='right'):
    '''
import pstats
p=pstats.Stats('nested.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(20)
    '''
    import cProfile
    cProfile.run('{0}()'.format(name), 'nested.prof')

if __name__ == '__main__':
#    time('left')
    profile('left')
#    right()

    
    
