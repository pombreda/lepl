
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
Tests for the lepl.offside.stream module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.lexer.matchers import Token
from lepl.matchers import Regexp, Literal
from lepl.offside.config import LineAwareConfiguration
from lepl.offside.matchers import BLine
from lepl.offside.support import OffsideError
from lepl.regexp.matchers import DfaRegexp

class LineTest(TestCase):
    
    def test_bad_config(self):
        #basicConfig(level=DEBUG)
        text = Token('[^\n\r]+')
        quoted = Regexp("'[^']'")
        line = BLine(text(quoted))
        parser = line.string_parser(LineAwareConfiguration())
        try:
            parser("'a'")
            assert False, 'Expected error'
        except OffsideError as error:
            assert str(error).startswith('No initial indentation has been set.')
            
    def test_line(self):
        #basicConfig(level=DEBUG)
        text = Token('[^\n\r]+')
        quoted = Regexp("'[^']'")
        line = BLine(text(quoted))
        parser = line.string_parser(LineAwareConfiguration(block_start=0))
        assert parser("'a'") == ["'a'"]
        
    def test_offset(self):
        #basicConfig(level=DEBUG)
        text = Token('[^\n\r]+')
        line = BLine(text(~Literal('aa') & Regexp('.*')))
        parser = line.string_parser(LineAwareConfiguration(block_start=0))
        assert parser('aabc') == ['bc']
        # what happens with an empty match?
        check = ~Literal('aa') & Regexp('.*')
        assert check.parse('aa') == ['']
        assert parser('aa') == ['']
        
    def test_single_line(self):
        #basicConfig(level=DEBUG)
        line = DfaRegexp('(*SOL)[a-z]*(*EOL)')
        parser = line.string_parser(LineAwareConfiguration())
        assert parser('abc') == ['abc']
        

