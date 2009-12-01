
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
Tests for the lepl.regexp.matchers module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import UnicodeAlphabet
from lepl.regexp.core import Compiler
from lepl.support import format


# pylint: disable-msg=C0103, C0111, C0301
# (dude this is just a test)


class CompilerTest(TestCase):
    
    def test_compiler(self):
        #basicConfig(level=DEBUG)
        self.do_test('a', 'a', (['label'], 'a', ''), [('label', 'a', '')])
        self.do_test('ab', 'ab', (['label'], 'ab', ''), [('label', 'ab', '')])
        self.do_test('a', 'ab', (['label'], 'a', 'b'), [('label', 'a', 'b')])
        self.do_test('a*', 'aab', (['label'], 'aa', 'b'), 
                     [('label', 'aa', 'b'), ('label', 'a', 'ab'), 
                      ('label', '', 'aab')])
        self.do_test('(a|b)', 'a', (['label'], 'a', ''), [('label', 'a', '')])
        self.do_test('(a|b)', 'b', (['label'], 'b', ''), [('label', 'b', '')])
        
    def do_test(self, pattern, target, dfa_result, nfa_result):
        alphabet = UnicodeAlphabet.instance()
        compiler = Compiler.single(alphabet, pattern)
        text = str(compiler.expression)
        assert text == format('(?P<label>{0!s})', pattern), text
        nfa = compiler.nfa()
        result = list(nfa.match(target))
        assert result == nfa_result, result
        dfa = compiler.dfa()
        result = dfa.match(target)
        assert result == dfa_result, result
