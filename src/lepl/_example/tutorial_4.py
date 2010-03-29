
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,R0201,R0903
#@PydevCodeAnalysisIgnore
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

#from logging import basicConfig, DEBUG
from operator import add, sub, mul, truediv
from timeit import timeit

from lepl import *
from lepl._example.support import Example


def add_sub_node():
    value = Token(UnsignedFloat())
    symbol = Token('[^0-9a-zA-Z \t\r\n]')
    number = Optional(symbol('-')) + value >> float
    group2, group3 = Delayed(), Delayed()

    # first layer, most tightly grouped, is parens and numbers
    parens = symbol('(') & group3 & symbol(')')
    group1 = parens | number

    # second layer, next most tightly grouped, is multiplication
    mul = group1 & symbol('*') & group2 > List
    div = group1 & symbol('/') & group2 > List
    group2 += mul | div | group1

    # third layer, least tightly grouped, is addition
    add = group2 & symbol('+') & group3 > List
    sub = group2 & symbol('-') & group3 > List
    group3 += add | sub | group2
    return group3

def error_1():
    value = Token(UnsignedFloat())
    symbol = Token('[^0-9a-zA-Z \t\r\n]')
    number = Optional(symbol('-')) + value >> float
    group2, group3 = Delayed(), Delayed()

    # first layer, most tightly grouped, is parens and numbers
    parens = symbol('(') & group3 & symbol(')')
    group1 = parens | number

    # second layer, next most tightly grouped, is multiplication
    mul = group1 & symbol('*') & group2 > List
    div = group1 & symbol('/') & group2 > List
    group2 += group1 | mul | div

    # third layer, least tightly grouped, is addition
    add = group2 & symbol('+') & group3 > List
    sub = group2 & symbol('-') & group3 > List
    group3 += group2 | add | sub
    return group3

def error_2():
    value = Token(UnsignedFloat())
    symbol = Token('[^0-9a-zA-Z \t\r\n]')
    number = Optional(symbol('-')) + value >> float
    group2, group3 = Delayed(), Delayed()

    # first layer, most tightly grouped, is parens and numbers
    parens = symbol('(') & group3 & symbol(')')
    group1 = parens | number

    # second layer, next most tightly grouped, is multiplication
    mul = group2 & symbol('*') & group2 > List
    div = group2 & symbol('/') & group2 > List
    group2 += group1 | mul | div

    # third layer, least tightly grouped, is addition
    add = group3 & symbol('+') & group3 > List
    sub = group3 & symbol('-') & group3 > List
    group3 += group2 | add | sub
    return group3

def node_1():
    class Add(List): pass
    class Sub(List): pass
    class Mul(List): pass
    class Div(List): pass
    value = Token(UnsignedFloat())
    symbol = Token('[^0-9a-zA-Z \t\r\n]')
    number = Optional(symbol('-')) + value >> float
    group2, group3 = Delayed(), Delayed()

    # first layer, most tightly grouped, is parens and numbers
    parens = ~symbol('(') & group3 & ~symbol(')')
    group1 = parens | number

    # second layer, next most tightly grouped, is multiplication
    mul = group1 & ~symbol('*') & group2 > Mul
    div = group1 & ~symbol('/') & group2 > Div
    group2 += mul | div | group1

    # third layer, least tightly grouped, is addition
    add = group2 & ~symbol('+') & group3 > Add
    sub = group2 & ~symbol('-') & group3 > Sub
    group3 += add | sub | group2
    return group3

def node_2():
    class Op(List):
        def __float__(self):
            return self._op(float(self[0]), float(self[1]))
    class Add(Op): _op = add
    class Sub(Op): _op = sub
    class Mul(Op): _op = mul
    class Div(Op): _op = truediv
    value = Token(UnsignedFloat())
    symbol = Token('[^0-9a-zA-Z \t\r\n]')
    number = Optional(symbol('-')) + value >> float
    group2, group3 = Delayed(), Delayed()
    # first layer, most tightly grouped, is parens and numbers
    parens = ~symbol('(') & group3 & ~symbol(')')
    group1 = parens | number
    # second layer, next most tightly grouped, is multiplication
    mul_ = group1 & ~symbol('*') & group2 > Mul
    div_ = group1 & ~symbol('/') & group2 > Div
    group2 += mul_ | div_ | group1
    # third layer, least tightly grouped, is addition
    add_ = group2 & ~symbol('+') & group3 > Add
    sub_ = group2 & ~symbol('-') & group3 > Sub
    group3 += add_ | sub_ | group2
    return group3


class Tutorial4Example(Example):
    
    def run_add_sub_node(self):
        return add_sub_node()

    def run_error_1(self):
        return error_1()
    
    def unlimited_run_error_1(self):
        matcher = self.run_error_1()
        matcher.config.no_full_first_match()
        return matcher

    def run_error_2(self):
        return error_2()
    
    def unlimited_run_error_2(self):
        matcher = self.run_error_2()
        matcher.config.no_full_first_match()
        return matcher
    
    def test_all(self):
        
        self.examples([
(lambda: self.run_add_sub_node().parse('1+2*(3-4)+5/6+7')[0],
"""List
 +- 1.0
 +- '+'
 `- List
     +- List
     |   +- 2.0
     |   +- '*'
     |   +- '('
     |   +- List
     |   |   +- 3.0
     |   |   +- '-'
     |   |   `- 4.0
     |   `- ')'
     +- '+'
     `- List
         +- List
         |   +- 5.0
         |   +- '/'
         |   `- 6.0
         +- '+'
         `- 7.0"""),
(lambda: self.run_error_1().parse('1+2*(3-4)+5/6+7')[0], 
"""lepl.stream.maxdepth.FullFirstMatchException: The match failed at '+',
Line 1, character 1 of str: '1+2*(3-4)+5/6+7'.
"""),
(lambda: len(list(self.unlimited_run_error_1().parse_all('1+2*(3-4)+5/6+7'))), 
"""6"""),
(lambda: (self.run_error_1() & Eos()).parse('1+2*(3-4)+5/6+7')[0], 
"""List
 +- 1.0
 +- '+'
 `- List
     +- List
     |   +- 2.0
     |   +- '*'
     |   +- '('
     |   +- List
     |   |   +- 3.0
     |   |   +- '-'
     |   |   `- 4.0
     |   `- ')'
     +- '+'
     `- List
         +- List
         |   +- 5.0
         |   +- '/'
         |   `- 6.0
         +- '+'
         `- 7.0"""),
(lambda: len(list((self.unlimited_run_error_1() & Eos()).parse_all('1+2*(3-4)+5/6+7'))), 
"""1"""),
(lambda: self.run_error_2().parse('1+2*(3-4)+5/6+7')[0], 
"""lepl.stream.maxdepth.FullFirstMatchException: The match failed at '+',
Line 1, character 1 of str: '1+2*(3-4)+5/6+7'.
"""),
(lambda: len(list(self.unlimited_run_error_2().parse_all('1+2*(3-4)+5/6+7'))), 
"""12"""),
(lambda: (self.run_error_2() & Eos()).parse('1+2*(3-4)+5/6+7')[0], 
"""List
 +- 1.0
 +- '+'
 `- List
     +- List
     |   +- 2.0
     |   +- '*'
     |   +- '('
     |   +- List
     |   |   +- 3.0
     |   |   +- '-'
     |   |   `- 4.0
     |   `- ')'
     +- '+'
     `- List
         +- List
         |   +- 5.0
         |   +- '/'
         |   `- 6.0
         +- '+'
         `- 7.0"""),
(lambda: len(list((self.unlimited_run_error_2() & Eos()).parse_all('1+2*(3-4)+5/6+7'))), 
"""5"""),
(lambda: node_1().parse('1+2*(3-4)+5/6+7')[0],
"""Add
 +- 1.0
 `- Add
     +- Mul
     |   +- 2.0
     |   `- Sub
     |       +- 3.0
     |       `- 4.0
     `- Add
         +- Div
         |   +- 5.0
         |   `- 6.0
         `- 7.0"""),
(lambda: node_2().parse('1+2*(3-4)+5/6+7')[0],
"""Add
 +- 1.0
 `- Add
     +- Mul
     |   +- 2.0
     |   `- Sub
     |       +- 3.0
     |       `- 4.0
     `- Add
         +- Div
         |   +- 5.0
         |   `- 6.0
         `- 7.0"""),
(lambda: float(node_2().parse('1+2*(3-4)+5/6+7')[0]),
"""6.83333333333"""),
])


if __name__ == '__main__':
        
    parser = add_sub_node().get_parse()
    print(timeit('parser("1+2*(3-4)+5/6+7")',
                 'from __main__ import parser', number=100))
    
    parser = (error_1() & Eos()).get_parse()
    print(timeit('parser("1+2*(3-4)+5/6+7")',
                 'from __main__ import parser', number=100))
    
    parser = (error_2() & Eos()).get_parse()
    print(timeit('parser("1+2*(3-4)+5/6+7")',
                 'from __main__ import parser', number=100))

