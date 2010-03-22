
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
from lepl.matchers.core import Regexp, Literal, Any
from lepl.offside.matchers import BLine, Indent, Eol
from lepl.offside.support import OffsideError
from lepl.regexp.matchers import DfaRegexp

class LineTest(TestCase):
    
    def test_bad_config(self):
        #basicConfig(level=DEBUG)
        text = Token('[^\n\r]+')
        quoted = Regexp("'[^']'")
        line = BLine(text(quoted))
        line.config.default_line_aware()
        parser = line.get_parse_string()
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
        line.config.default_line_aware(block_start=0)
        parser = line.get_parse_string()
        assert parser("'a'") == ["'a'"]
        
    def test_offset(self):
        #basicConfig(level=DEBUG)
        text = Token('[^\n\r]+')
        line = BLine(text(~Literal('aa') & Regexp('.*')))
        line.config.default_line_aware(block_start=0)
        parser = line.get_parse_string()
        assert parser('aabc') == ['bc']
        # what happens with an empty match?
        check = ~Literal('aa') & Regexp('.*')
        check.config.no_full_first_match()
        assert check.parse('aa') == ['']
        assert parser('aa') == ['']
        
    def test_single_line(self):
        #basicConfig(level=DEBUG)
        line = DfaRegexp('(*SOL)[a-z]*(*EOL)')
        line.config.default_line_aware()
        parser = line.get_parse_string()
        assert parser('abc') == ['abc']
        
    def test_tabs(self):
        '''
        Use block_policy here so that the regexp parser that excludes SOL
        and EOL is used; otherwise Any()[:] matches those and we end up
        with a single monster token.
        '''
        line = Indent() & Token(Any()) & Eol()
        line.config.default_line_aware(tabsize=8, block_policy=0).trace(True)
        result = line.parse('a')
        assert result == ['', 'a', ''], result
        result = line.parse('\ta')
        assert result == ['        ', 'a', ''], result
        line.config.default_line_aware(tabsize=None, block_policy=0)
        result = line.parse('\ta')
        assert result == ['\t', 'a', ''], result
        line.config.default_line_aware(block_policy=0)
        result = line.parse('\ta')
        assert result == ['        ', 'a', ''], result

