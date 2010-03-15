
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

from lepl import *
from lepl._example.support import Example


class Tutorial1Example(Example):
    
    def run_error(self):
        number = SignedFloat() >> float
        add = number & ~Literal('+') & number > sum
        return add.parse('12 + 30')
    
    def run_explicit_space(self):
        number = SignedFloat() >> float
        add = number & ~Space() & ~Literal('+') & ~Space() & number > sum
        return add.parse('12 + 30')
    
    def run_space_error(self):
        number = SignedFloat() >> float
        add = number & ~Space() & ~Literal('+') & ~Space() & number > sum
        return add.parse('12+30')

    def run_star(self, text):
        number = SignedFloat() >> float
        spaces = ~Star(Space())
        add = number & spaces & ~Literal('+') & spaces & number > sum
        return add.parse(text)
    
    def run_a3(self):
        a = Literal('a')
        return a[3].parse('aaa')

    def run_a24(self, text):
        a = Literal('a')
        return a[2:4].parse(text)
    
    def run_a24_all(self):
        a = Literal('a')
        return list(a[2:4].parse_all('aaaa'))
    
    def run_a01(self):
        a = Literal('a')
        return list(a[:1].parse_all('a'))

    def run_a4plus(self):
        a = Literal('a')
        return list(a[4:].parse_all('aaaaa'))
    
    def run_breadth(self):
        a = Literal('a')[2:4:'b']
        a.config.no_full_first_match()
        return list(a.parse_all('aaaa'))
    
    def run_brackets(self, text):
        number = SignedFloat() >> float
        spaces = ~Space()[:]
        add = number & spaces & ~Literal('+') & spaces & number > sum
        return add.parse(text)
    
    def run_nfa_regexp(self):
        return list(NfaRegexp('a*').parse_all('aaa'))
    
    def run_dfa_regexp(self):
        return list(DfaRegexp('a*').parse_all('aaa'))
    
    def run_regexp(self):
        return list(Regexp('a*').parse_all('aaa'))
    
    def run_token_1(self):
        value = Token(SignedFloat())
        symbol = Token('[^0-9a-zA-Z \t\r\n]')
        number = value >> float
        add = number & ~symbol('+') & number > sum
        return add.parse_string('12+30')

    def test_all(self):
        self.examples([
(self.run_error,
"""lepl.stream.maxdepth.FullFirstMatchException: The match failed at ' + 30',
Line 1, character 2 of str: '12 + 30'.
"""),
(self.run_explicit_space,
"""[42.0]"""),
(self.run_space_error,
"""lepl.stream.maxdepth.FullFirstMatchException: The match failed at '+30',
Line 1, character 2 of str: '12+30'.
"""),
(lambda: self.run_star('12 + 30'),
"""[42.0]"""),
(lambda: self.run_star('12+30'),
"""[42.0]"""),
(lambda: self.run_star('12+     30'),
"""[42.0]"""),
(self.run_a3,
"""['a', 'a', 'a']"""),
(lambda: self.run_a24('aa'),
"""['a', 'a']"""),
(lambda: self.run_a24('aaaa'),
"""['a', 'a', 'a', 'a']"""),
(self.run_a24_all,
"""[['a', 'a', 'a', 'a'], ['a', 'a', 'a'], ['a', 'a']]"""),
(self.run_a01,
"""[['a'], []]"""),
(self.run_a4plus,
"""[['a', 'a', 'a', 'a', 'a'], ['a', 'a', 'a', 'a']]"""),
(self.run_breadth,
"""[['a', 'a'], ['a', 'a', 'a'], ['a', 'a', 'a', 'a']]"""),
(lambda: self.run_brackets('12 + 30'),
"""[42.0]"""),
(lambda: self.run_brackets('12+30'),
"""[42.0]"""),
(lambda: self.run_brackets('12+     30'),
"""[42.0]"""),
(self.run_nfa_regexp,
"""[['aaa'], ['aa'], ['a'], ['']]"""),
(self.run_dfa_regexp,
"""[['aaa']]"""),
(self.run_regexp,
"""[['aaa']]"""),
(self.run_token_1,
"""lepl.stream.maxdepth.FullFirstMatchException: The match failed at '[(['Tk0'], '+30')][0:]',
Line 1, character 2 of str: '12+30'.
"""),
])
        
