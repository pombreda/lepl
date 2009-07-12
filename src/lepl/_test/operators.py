
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
Tests for the lepl.operators module.
'''

from threading import Thread
from unittest import TestCase

from lepl import Delayed, Any, Eos, Drop, Separator, Literal, Space, \
    SmartSeparator1, Optional


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102
# (dude this is just a test)

    
class ThreadTest(TestCase):
    '''
    Test for thread safety.
    '''
    
    def test_safety(self):
        matcher3 = Delayed()
        matcher4 = Delayed()
        matcher1 = Any()[::'b',...] & Eos()
        with Separator(Drop(Any('a')[:])):
            matcher2 = Any()[::'b',...] & Eos()
            # pylint: disable-msg=W0613
            def target(matcher3=matcher3, matcher4=matcher4):
                matcher3 += Any()[::'b',...] & Eos()
                with Separator(Drop(Any('b')[:])):
                    matcher4 += Any()[::'b',...] & Eos()
            t = Thread(target=target)
            t.start()
            t.join()
            matcher5 = Any()[::'b',...] & Eos()
        matcher6 = Any()[::'b',...] & Eos()
        text = 'cababab'
        assert text == matcher1.parse_string(text)[0], matcher1.parse_string(text)
        assert 'cbbb' == matcher2.parse_string(text)[0], matcher2.parse_string(text)
        assert text == matcher3.parse_string(text)[0], matcher3.parse_string(text)
        assert 'caaa' == matcher4.parse_string(text)[0], matcher4.parse_string(text)
        assert 'cbbb' == matcher5.parse_string(text)[0], matcher5.parse_string(text)
        assert text == matcher6.parse_string(text)[0], matcher6.parse_string(text)


class SpaceTest(TestCase):
    
    def word(self):
        return Literal("a") & Literal("bc")[1:,...]

    def test_spaces(self):
        with Separator(~Space()):
            s1 = self.word()[1:].string_parser()
            assert not s1("abc")
            assert s1("a bc")
            with Separator(None):
                s2 = self.word()[1:].string_parser()
                assert s2("abc")
                assert not s2("a bc")


class SmartSpace1Test(TestCase):
    
    def test_smart_spaces(self):
        with SmartSeparator1(Space()):
            parser = 'a' &  Optional('b') & 'c' & Eos()
        assert parser.parse('a b c')
        assert parser.parse('a c')
        assert not parser.parse('a b c ')
        assert not parser.parse('a c ')
        assert not parser.parse('a bc')
        assert not parser.parse('ab c')
        assert not parser.parse('abc')
        assert not parser.parse('ac')
        assert not parser.parse('a  c')
