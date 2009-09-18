
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
Check location data within tokens.
'''

# pylint: disable-msg=W0614, W0401, C0103, C0111, R0201
#@PydevCodeAnalysisIgnore


#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class LocationTest(TestCase):
    
    def test_location_token(self):
        '''
        Check that location is correct for a token.
        '''
        #basicConfig(level=DEBUG)
        text = '\n   \n   111  xxx 222\n\n'
        fail = Token(Word('x')) ** make_error('{filename} {lineno} {offset}')
        ok = Token(Word('12'))
        parser = Star(fail | ok) >> throw
        try:
            parser.parse_string(text)
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.filename == r"str: '\n   \n   111  xxx 222\n\n'"
            assert e.lineno == 3
            assert e.offset == 9
            assert e.text == '   111  xxx 222\n', repr(e.text)
        
    def test_location_content(self):
        '''
        Check that location is correct inside token.
        '''
        #basicConfig(level=DEBUG)
        text = '\n   \n   111  xxx 222\n\n'
        fail = Token(Word('x'))\
            (Empty() ** make_error('{filename} {lineno} {offset}'), 
             complete=False)
        ok = Token(Word('12'))
        parser = Star(fail | ok) >> throw
        try:
            parser.parse_string(text)
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.filename == r"str: '\n   \n   111  xxx 222\n\n'", \
                e.filename
            assert e.lineno == 3
            assert e.offset == 9
            assert e.text == '   111  xxx 222\n', repr(e.text)
        
    
        