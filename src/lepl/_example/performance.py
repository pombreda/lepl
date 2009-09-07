
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,W0621,R0903
# (the code style is for documentation, not "real")
#@PydevCodeAnalysisIgnore

'''
Examples from the documentation.
'''

from gc import collect
from timeit import timeit

from lepl import *
from lepl._example.support import Example

NUMBER = 10
REPEAT = 5

def build(config):
    
    #basicConfig(level=INFO)
    
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
    
    parser = line.string_parser(config)
    return parser

def default(): return build(Configuration.default())
def managed(): return build(Configuration.managed())
def nfa(): return build(Configuration.nfa())
def dfa(): return build(Configuration.dfa())
def basic(): return build(Configuration())

def trace_only(): 
    return build(
        Configuration(monitors=[TraceResults(False)]))

def manage_only(): 
    return build(
        Configuration(monitors=[GeneratorManager(queue_len=0)]))

def memo_only(): 
    return build(
        Configuration(rewriters=[auto_memoize()]))

def nfa_only(): 
    return build(
        Configuration(rewriters=[
            regexp_rewriter(UnicodeAlphabet.instance(), False)]))

def dfa_only(): 
    return build(
        Configuration(rewriters=[
            regexp_rewriter(UnicodeAlphabet.instance(), False, DfaRegexp)]))

def slow(): 
    return build(
        Configuration(rewriters=[auto_memoize()],
                      monitors=[TraceResults(False),
                                GeneratorManager(queue_len=0)]))

def parse_multiple(parser):
    for _i in range(NUMBER):
        parser('1.23e4 + 2.34e5 * (3.45e6 + 4.56e7 - 5.67e8)')[0]

def parse_default(): parse_multiple(default())
def parse_managed(): parse_multiple(managed())
def parse_nfa(): parse_multiple(nfa())
def parse_dfa(): parse_multiple(dfa())
def parse_basic(): parse_multiple(basic())
def parse_trace_only(): parse_multiple(trace_only())
def parse_manage_only(): parse_multiple(manage_only())
def parse_memo_only(): parse_multiple(memo_only())
def parse_nfa_only(): parse_multiple(nfa_only())
def parse_dfa_only(): parse_multiple(dfa_only())
def parse_slow(): parse_multiple(slow())

def time(number, name):
    stmt = '{0}()'.format(name)
    setup = 'from __main__ import {0}'.format(name)
    return timeit(stmt, setup, number=number)

def analyse(func, time1_base=None, time2_base=None):
    '''
    We do our own repeating so we can GC between attempts
    '''
    name = func.__name__
    (time1, time2) = ([], [])
    for _i in range(REPEAT):
        collect()
        time1.append(time(NUMBER, name))
        collect()
        time2.append(time(1, 'parse_' + name))
    (time1, time2) = (min(time1), min(time2))
    # remove the time needed to compile
    time2 = time2 - (time1 / NUMBER)
    print('{0:>20s} {1:5.2f} {2:7s}  {3:5.2f} {4:7s}'.format(name, 
            time1, normalize(time1, time1_base), 
            time2, normalize(time2, time2_base)))
    return (time1, time2)

def normalize(time, base):
    if base:
        return '({0:5.2f})'.format(time / base)
    else:
        return ''

def main():
    print('{0:d} iterations; total time in s (best of {1:d})\n'.format(
            NUMBER, REPEAT))
    (time1, time2) = analyse(basic)
    for config in [default, managed, nfa, dfa]:
        analyse(config, time1, time2)
    print()
    for config in [trace_only, manage_only, memo_only, nfa_only, dfa_only, slow]:
        analyse(config, time1, time2)

if __name__ == '__main__':
    main()

# pylint: disable-msg=E0601
# (pylint parsing bug?)        
class PerformanceExample(Example):
    
    def test_parse(self):
    
        # run this to make sure nothing changes
        parsers = [default, managed, nfa, dfa,
                   basic, trace_only, manage_only,
                   memo_only, nfa_only, dfa_only, slow]
        examples = [(lambda: parser()('1.23e4 + 2.34e5 * (3.45e6 + 4.56e7 - 5.67e8)')[0],
"""Expression
 +- Factor
 |   `- Term
 |       `- number '1.23e4'
 +- operator '+'
 `- Factor
     +- Term
     |   `- number '2.34e5'
     +- operator '*'
     `- Term
         +- '('
         +- Expression
         |   +- Factor
         |   |   `- Term
         |   |       `- number '3.45e6'
         |   +- operator '+'
         |   +- Factor
         |   |   `- Term
         |   |       `- number '4.56e7'
         |   +- operator '-'
         |   `- Factor
         |       `- Term
         |           `- number '5.67e8'
         `- ')'""") for parser in parsers]
        self.examples(examples)
        
