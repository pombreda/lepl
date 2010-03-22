from lepl.stream.stream import list_join

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
Tests for the lepl.core.config module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class ParseTest(TestCase):
    
    def run_test(self, name, text, parse, match2, match3, error, 
                 config=lambda x: None, **kargs):
        matcher = Any()[:, ...]
        config(matcher)
        parser = getattr(matcher, 'parse' + name)
        result = str(parser(text, **kargs))
        assert result == parse, result
        matcher = Any()[2, ...]
        matcher.config.no_full_first_match()
        config(matcher)
        parser = getattr(matcher, 'match' + name)
        result = str(list(parser(text, **kargs)))
        assert result == match2, result
        matcher = Any()[3, ...]
        matcher.config.no_full_first_match()
        config(matcher)
        parser = getattr(matcher, 'match' + name)
        result = str(list(parser(text, **kargs)))
        assert result == match3, result
        matcher = Any()
        config(matcher)
        parser = getattr(matcher, 'parse' + name)
        try:
            parser(text)
        except FullFirstMatchException as e:
            assert str(e) == error, str(e)
            
    def test_string(self):
        self.run_test('_string', 'abc', 
                      "['abc']", 
                      "[(['ab'], 'abc'[2:])]", 
                      "[(['abc'], ''[0:])]", 
                      """The match failed at 'bc',
Line 1, character 1 of str: 'abc'.""")
        self.run_test('', 'abc', 
                      "['abc']", 
                      "[(['ab'], 'abc'[2:])]", 
                      "[(['abc'], ''[0:])]",
                      """The match failed at 'bc',
Line 1, character 1 of str: 'abc'.""")
        self.run_test('_null', 'abc', 
                      "['abc']", 
                      "[(['ab'], 'c')]", 
                      "[(['abc'], '')]",
                      """The match failed at 'bc'.""")

    def test_string_list(self):
        self.run_test('_items', ['a', 'b', 'c'], 
                      "['abc']", 
                      "[(['ab'], ['a', 'b', 'c'][2:])]", 
                      "[(['abc'], [][0:])]",
                      """The match failed at '['a', 'b', 'c'][1:]',
Index 1 of items: ['a', 'b', 'c'].""", 
config=lambda m: m.config.no_compile_to_regexp(), sub_list=False)
        self.run_test('_items', ['a', 'b', 'c'], 
                      "[['a', 'b', 'c']]", 
                      "[([['a', 'b']], ['a', 'b', 'c'][2:])]", 
                      "[([['a', 'b', 'c']], [][0:])]",
                      """The match failed at '['a', 'b', 'c'][1:]',
Index 1 of items: ['a', 'b', 'c'].""", 
config=lambda m: m.config.no_compile_to_regexp(), sub_list=True)
        
    def test_int_list(self):
        #basicConfig(level=DEBUG)
        try:
            self.run_test('_items', [1, 2, 3], [], [], [], """""")
        except RegexpError as e:
            assert 'no_compile_regexp' in str(e), str(e)
        self.run_test('_items', [1, 2, 3], 
                      "[[1, 2, 3]]", 
                      "[([[1, 2]], [1, 2, 3][2:])]", 
                      "[([[1, 2, 3]], [][0:])]",
                      """The match failed at '[1, 2, 3][1:]',
Index 1 of items: [1, 2, 3].""",
config=lambda m: m.config.no_compile_to_regexp(), sub_list=True)


class BugTest(TestCase):
    
    def test_bug(self):
        matcher = Any('a')
        matcher.config.clear()
        result = list(matcher.match_items(['b']))
        assert result == [], result
