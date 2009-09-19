
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103
# (the code style is for documentation, not "real")
#@PydevCodeAnalysisIgnore

'''
Examples from the documentation.
'''

from lepl import *
from lepl._example.support import Example


class MatcherExample(Example):
    
    def test_most(self):
        self.examples([
            (lambda: Literal('hello').parse_string('hello world'),
             "['hello']"),

            (lambda: Any().parse_string('hello world'), 
             "['h']"),
            (lambda: Any('abcdefghijklm')[0:].parse_string('hello world'), 
             "['h', 'e', 'l', 'l']"),

            (lambda: And(Any('h'), Any()).parse_string('hello world'), 
             "['h', 'e']"),
            (lambda: And(Any('h'), Any('x')).parse_string('hello world'), 
             "None"),
            (lambda: (Any('h') & Any('e')).parse_string('hello world'), 
             "['h', 'e']"),

            (lambda: Or(Any('x'), Any('h'), Any('z')).parse_string('hello world'), 
             "['h']"),
            (lambda: Or(Any('h'), Any()[3]).parse_string('hello world'), 
             "['h']"),

            (lambda: Repeat(Any(), 3, 3).parse_string('12345'), 
             "['1', '2', '3']"),

            (lambda: Repeat(Any(), 3).parse_string('12345'), 
             "['1', '2', '3', '4', '5']"),
            (lambda: Repeat(Any(), 3).parse_string('12'),
             "None"),

            (lambda: next(Lookahead(Literal('hello')).match('hello world')), 
             "([], 'hello world')"),
            (lambda: Lookahead(Literal('hello')).parse('hello world'), 
             "[]"),
            (lambda: Lookahead('hello').parse_string('goodbye cruel world'), 
             "None"),
            (lambda: (~Lookahead('hello')).parse_string('hello world'), 
             "None"),
            (lambda: (~Lookahead('hello')).parse_string('goodbye cruel world'), 
             "[]"),

            (lambda: (Drop('hello') / 'world').parse_string('hello world'), 
             "[' ', 'world']"),
            (lambda: (~Literal('hello') / 'world').parse_string('hello world'), 
             "[' ', 'world']"),
            (lambda: (Lookahead('hello') / 'world').parse_string('hello world'), 
             "None")])


    def test_multiple_or(self):
        matcher = Or(Any('h'), Any()[3]).match('hello world')
        assert str(next(matcher)) == "(['h'], 'ello world')"
        assert str(next(matcher)) == "(['h', 'e', 'l'], 'lo world')"


    def test_repeat(self):
        matcher = Repeat(Any(), 3).match('12345')
        assert str(next(matcher)) == "(['1', '2', '3', '4', '5'], '')"
        assert str(next(matcher)) == "(['1', '2', '3', '4'], '5')"
        assert str(next(matcher)) == "(['1', '2', '3'], '45')"
        
        matcher = Repeat(Any(), 3, None, 'b').match('12345')
        assert str(next(matcher)) == "(['1', '2', '3'], '45')"
        assert str(next(matcher)) == "(['1', '2', '3', '4'], '5')"
        assert str(next(matcher)) == "(['1', '2', '3', '4', '5'], '')"



    def test_show(self):
        
        def show(results):
            #print('results:', results)
            return results

        self.examples([
            (lambda: Apply(Any()[:,...], show).parse_string('hello world'), 
             "[['hello world']]"),
            (lambda: (Any()[:,...] > show).parse_string('hello world'), 
             "[['hello world']]"),
            (lambda: Apply(Any()[:,...], show, raw=True).parse_string('hello world'),
             "['hello world']"),
            (lambda: (Any()[:,...] >= show).parse_string('hello world'),
             "['hello world']")])


    def test_apply_raw(self):
        
        def format3(a, b, c):
            return 'a: {0}; b: {1}; c: {2}'.format(a, b, c)
        
        self.examples([
            (lambda: Apply(Any()[3], format3, args=True).parse('xyz'),
              "['a: x; b: y; c: z']"),
            (lambda: (Any()[3] > args(format3)).parse('xyz'),
              "['a: x; b: y; c: z']")])
        