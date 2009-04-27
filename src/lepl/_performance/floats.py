
from logging import basicConfig, DEBUG

from lepl import *
from lepl.rewriters import compose_transforms


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
#    parser = line.string_parser(Configuration.dfa())
    parser = line.string_parser()
    
    #print(parser.matcher)
    for i in range(30):
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

    
    
