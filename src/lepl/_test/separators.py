
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
Tests for separators (space handling).
'''

from unittest import TestCase

from lepl import And, Optional, Space, Separator, SmartSeparator1, \
    SmartSeparator2, Eos


STREAMS_3 = ['a b c ',
           'a b c',
           ' b c',
           'b c',
           'ab c',
           'a c',
           'a  c',
           'c',
           ' c',
           '  c']

STREAMS_2 = ['a b ',
             'a b',
             'ab',
             ' b',
             'b',
             'a ',
             'a',
             '',
             ' ']


class AbcSeparatorTest(TestCase):
    
    def _assert(self, separator, expecteds, streams=STREAMS_3):
        with separator:
            parser = And(Optional('a') & Optional('b') & 'c', Eos())
        ok = True
        for (stream, expected) in zip(streams, expecteds):
            parsed = parser.parse(stream) is not None
            print('{0!r:9} : {1!r:5} {2!r:5}'
                  .format(stream, parsed, parsed == expected))
            ok = ok and (parsed == expected)
        assert ok
        
    def test_separator(self):
        print("\nSeparator(Space())")
        self._assert(Separator(Space()), 
                     [False, True, True, False, False, False, True, False, False, True])
        print("\nSeparator(Space()[:])")
        self._assert(Separator(Space()[:]), 
                     [False, True, True, True, True, True, True, True, True, True])
        
    def test_separator1(self):
        print("\nSmartSeparator1(Space())")
        self._assert(SmartSeparator1(Space()), 
                     [False, True, False, True, False, True, False, True, False, False])
        print("\nSmartSeparator1(Space()[:])")
        self._assert(SmartSeparator1(Space()[:]), 
                     [False, True, False, True, True, True, True, True, False, False])
        
    def test_separator2(self):
        print("\nSmartSeparator2(Space())")
        self._assert(SmartSeparator2(Space()), 
                     [False, True, False, True, False, True, False, False, False, False])
        print("\nSmartSeparator2(Space()[:])")
        self._assert(SmartSeparator2(Space()[:]), 
                     [False, True, False, True, True, True, True, False, False, False])
        
            
class AbSeparatorTest(TestCase):
    
    def _assert(self, separator, expecteds, streams=STREAMS_2):
        with separator:
            parser = And(Optional('a') & Optional('b'), Eos())
        ok = True
        for (stream, expected) in zip(streams, expecteds):
            parsed = parser.parse(stream) is not None
            print('{0!r:9} : {1!r:5} {2!r:5}'
                  .format(stream, parsed, parsed == expected))
            ok = ok and (parsed == expected)
        assert ok
        
    def test_separator(self):
        print("\nSeparator(Space())")
        self._assert(Separator(Space()), 
                     [False, True, False, True, False, True, False, False, True])
        print("\nSeparator(Space()[:])")
        self._assert(Separator(Space()[:]), 
                     [False, True, True, True, True, True, True, True, True])
        
    def test_separator1(self):
        print("\nSmartSeparator1(Space())")
        self._assert(SmartSeparator1(Space()), 
                     [False, True, False, False, True, False, True, True, False])
        print("\nSmartSeparator1(Space()[:])")
        self._assert(SmartSeparator1(Space()[:]), 
                     [False, True, True, False, True, False, True, True, False])
        
    def test_separator2(self):
        print("\nSmartSeparator2(Space())")
        self._assert(SmartSeparator2(Space()), 
                     [False, True, False, False, True, False, True, False, False])
        print("\nSmartSeparator2(Space()[:])")
        self._assert(SmartSeparator2(Space()[:]), 
                     [False, True, True, False, True, False, True, False, False])
        
        
class AbcEosSeparatorTest(TestCase):
    
    def _assert(self, separator, expecteds, streams=STREAMS_3):
        with separator:
            parser = Optional('a') & Optional('b') & 'c' & Eos()
        ok = True
        for (stream, expected) in zip(streams, expecteds):
            parsed = parser.parse(stream) is not None
            print('{0!r:9} : {1!r:5} {2!r:5}'
                  .format(stream, parsed, parsed == expected))
            ok = ok and (parsed == expected)
        assert ok
        
    def test_separator(self):
        print("\nSeparator(Space())")
        self._assert(Separator(Space()), 
                     [True, False, False, False, False, False, False, False, False, False])
        print("\nSeparator(Space()[:])")
        self._assert(Separator(Space()[:]), 
                     [True, True, True, True, True, True, True, True, True, True])
        
    def test_separator1(self):
        print("\nSmartSeparator1(Space())")
        self._assert(SmartSeparator1(Space()), 
                     [False, True, False, True, False, True, False, True, False, False])
        print("\nSmartSeparator1(Space()[:])")
        self._assert(SmartSeparator1(Space()[:]), 
                     [False, True, False, True, True, True, True, True, False, False])
        
    def test_separator2(self):
        print("\nSmartSeparator2(Space())")
        self._assert(SmartSeparator2(Space()), 
                     [True, False, False, False, False, False, False, False, False, False])
        print("\nSmartSeparator2(Space()[:])")
        self._assert(SmartSeparator2(Space()[:]), 
                     [True, True, False, True, True, True, True, False, False, False])
        
            
class AbEosSeparatorTest(TestCase):
    
    def _assert(self, separator, expecteds, streams=STREAMS_2):
        with separator:
            parser = Optional('a') & Optional('b') & Eos()
        ok = True
        for (stream, expected) in zip(streams, expecteds):
            parsed = parser.parse(stream) is not None
            print('{0!r:9} : {1!r:5} {2!r:5}'
                  .format(stream, parsed, parsed == expected))
            ok = ok and (parsed == expected)
        assert ok
        
    def test_separator(self):
        print("\nSeparator(Space())")
        self._assert(Separator(Space()), 
                     [True, False, False, False, False, False, False, False, False])
        print("\nSeparator(Space()[:])")
        self._assert(Separator(Space()[:]), 
                     [True, True, True, True, True, True, True, True, True])
        
    def test_separator1(self):
        print("\nSmartSeparator1(Space())")
        self._assert(SmartSeparator1(Space()), 
                     [False, True, False, False, True, False, True, True, False])
        print("\nSmartSeparator1(Space()[:])")
        self._assert(SmartSeparator1(Space()[:]), 
                     [False, True, True, False, True, False, True, True, False])
        
    def test_separator2(self):
        print("\nSmartSeparator2(Space())")
        self._assert(SmartSeparator2(Space()), 
                     [True, False, False, False, False, True, False, False, False])
        print("\nSmartSeparator2(Space()[:])")
        self._assert(SmartSeparator2(Space()[:]), 
                     [True, True, True, False, True, True, True, False, False])
        
            
        
