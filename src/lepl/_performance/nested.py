
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

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401


from random import choice

from lepl import *


def make_data(size):
    '''
    Generate a string about 2^(size+1) in size of nested parens with newlines.
    '''
    data = ""
    for _i in range(size):
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
    #p = pair.string_matcher(Configuration.dfa())
    p = pair.string_matcher(Configuration(rewriters=[auto_memoize(False)]))
    results = list(p(make_data(6)))
    print(len(results))


def time(name='right'):
    from timeit import Timer
    t = Timer("{0}()".format(name), "from __main__ import {0}".format(name))
    print(t.timeit(number=10 if name == 'right' else 6)) 
    # right - 16.2 for 10
    # left - 82.5 for 6 (!)
    # after auto_memoize work
    # left - 30 for 6 (31 for conservative)
    # right - 15 for 10
    

def profile(name='right'):
    '''
import pstats
p=pstats.Stats('nested.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('{0}()'.format(name), 'nested.prof')

if __name__ == '__main__':
    time('left')
#    profile('left')
#    right()
#    left()
    
    
