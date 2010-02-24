
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

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401, R0903
#@PydevCodeAnalysisIgnore


from lepl import *


def floats():
        
    class Term(Node): pass
    class Factor(Node): pass
    class Expression(Node): pass
        
    expr   = Delayed()
    number = Float()                                > 'number'
    spaces = Drop(Regexp(r'\s*'))
    
    with Separator(spaces):
        term    = number | '(' & expr & ')'         > Term
        muldiv  = Any('*/')                         > 'operator'
        factor  = term & (muldiv & term)[:]         > Factor
        addsub  = Any('+-')                         > 'operator'
        expr   += factor & (addsub & factor)[:]     > Expression
        line    = Trace(expr) & Eos()
    
    #basicConfig(level=DEBUG)
    line.config
    parser = line.string_parser()
    
    print(repr(parser.matcher))
    for _i in range(3000): # increased from 30 to 3000 for new code
        results = parser('1.2e3 + 2.3e4 * (3.4e5 + 4.5e6 - 5.6e7)')
        assert isinstance(results[0], Expression)
    print(results[0])


def time():
    from timeit import Timer
    t = Timer("floats()", "from __main__ import floats")
    print(t.timeit(number=1))
    # 5.8 for default
    # second values after improving rewrite
    # 4.9,3.5,2.8,1.3 for dfa
    # 5.0,3.7,2.9,3.1 for nfa
    # wow - new code, with standard config, functions etc, 0.5
    # increase to 300, avoids parser building bias: 2.2
    # increase to 3000, improved memo: 20
    

def profile():
    '''
import pstats
p=pstats.Stats('floats.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('floats()', 'floats.prof')

if __name__ == '__main__':
    time()
#    profile()
#    floats()

    
    
