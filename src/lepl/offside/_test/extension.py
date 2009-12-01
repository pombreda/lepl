
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
Tests for the regexp extensions.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import UnicodeAlphabet
from lepl.offside.regexp import LineAwareAlphabet, make_hide_sol_eol_parser
from lepl.offside.stream import LineAwareStreamFactory
from lepl.regexp.core import Compiler
from lepl.regexp.str import make_str_parser
#from lepl.support import format


# pylint: disable-msg=C0103, C0111, C0301
# (dude this is just a test)


class CompilerTest(TestCase):
    
    def test_explicit(self):
        #basicConfig(level=DEBUG)
        self.do_test('(*SOL)', 'a', 
                     (['label'], '', "[Marker('(*SOL)',False), 'a', Marker('(*EOL)',True)][1:]"), 
                     [('label', '', "[Marker('(*SOL)',False), 'a', Marker('(*EOL)',True)][1:]")],
                     make_str_parser)
        self.do_test('.', 'a', 
                     (['label'], '', "[Marker('(*SOL)',False), 'a', Marker('(*EOL)',True)][1:]"), 
                     [('label', '', "[Marker('(*SOL)',False), 'a', Marker('(*EOL)',True)][1:]")],
                     make_str_parser)
        self.do_test('[^a]', 'a', 
                     (['label'], '', "[Marker('(*SOL)',False), 'a', Marker('(*EOL)',True)][1:]"), 
                     [('label', '', "[Marker('(*SOL)',False), 'a', Marker('(*EOL)',True)][1:]")],
                     make_str_parser)
        
    def test_implicit(self):
        #basicConfig(level=DEBUG)
        self.do_test('(*SOL)', 'a', 
                     (['label'], '', "[Marker('(*SOL)',False), 'a', Marker('(*EOL)',True)][1:]"), 
                     [('label', '', "[Marker('(*SOL)',False), 'a', Marker('(*EOL)',True)][1:]")],
                     make_hide_sol_eol_parser)
        self.do_test('.', 'a', 
                     None, 
                     [],
                     make_hide_sol_eol_parser)
        self.do_test('[^a]', 'a', 
                     None, 
                     [],
                     make_hide_sol_eol_parser)
        
        
    def do_test(self, pattern, target, dfa_result, nfa_result, parser_factory):
        alphabet = LineAwareAlphabet(UnicodeAlphabet.instance(), parser_factory)
        compiler = Compiler.single(alphabet, pattern)
        text = str(compiler.expression)
#        assert text == format('(?P<label>{0!s})', pattern), text
        
        factory = LineAwareStreamFactory(alphabet)
        target = factory.from_string(target)
        
        dfa = compiler.dfa()
        result = dfa.match(target)
        if result:
            (a, b, c) = result
            (p, q, r) = dfa_result
            assert a == p, result
            assert b == q, result
            assert repr(c) == r, result
        else:
            assert dfa_result == None, dfa_result

        nfa = compiler.nfa()
        result = list(nfa.match(target))
        assert len(result) == len(nfa_result), result
        for ((a,b,c), (p,q,r)) in zip(result, nfa_result):
            assert a == p, result
            assert b == q, result
            assert repr(c) == r, result
        
