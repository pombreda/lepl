
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
#@PydevCodeAnalysisIgnore


#from logging import basicConfig, DEBUG

from lepl import *


def full_left():
    '''
    Extreme test of left-recursion.
    '''
    #basicConfig(level=DEBUG)
    ab  = Delayed()
    with Separator(Regexp(r'\s*')):
        ab += (ab & 'b') | 'a'
#        ab += 'a' | (ab & 'b')
    p = (ab & Eos()).string_matcher(Configuration(rewriters=[auto_memoize]
#                                                  ,monitors=[TraceResults(True)]
                                                  ))
    results = list(p('a' + ('\nb' * 1000)))
    assert len(results) == 1
    print('done')


def time():
    from timeit import Timer
    t = Timer("full_left()", "from __main__ import full_left")
    print(t.timeit(number=10)) 
    # 17.6 for 10 (x100 bs)
    # 0.6 when rewritten 'a' | (ab & 'b')
    # 0.4 with auto_memoize
    

def profile():
    '''
import pstats
p=pstats.Stats('full_left.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(40)
    '''
    import cProfile
    cProfile.run('full_left()', 'full_left.prof')

if __name__ == '__main__':
    time()
#    profile()
#    full_left()

    
    
