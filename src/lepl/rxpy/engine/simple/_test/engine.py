#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.engine import EngineTest
from lepl.rxpy.engine.simple.engine import SimpleEngine
from lepl.rxpy.parser.support import ParserState


class SimpleEngineTest(EngineTest, TestCase):
    
    def default_engine(self):
        return SimpleEngine

    def test_unicode_escapes(self):
#        groups = self.engine(self.parse('\\d*'), '12x')
#        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
#        groups = self.engine(self.parse('\\D*'), 'x12')
#        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
#        groups = self.engine(self.parse('\\w*'), '12x a')
#        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
#        groups = self.engine(self.parse('\\W*'), ' a')
#        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
#        groups = self.engine(self.parse('\\s*'), '  a')
#        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
#        groups = self.engine(self.parse('\\S*'), 'aa ')
#        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        assert self.engine(self.parse(r'a\b '), 'a ')
        assert not self.engine(self.parse(r'a\bb'), 'ab')
        assert not self.engine(self.parse(r'a\B '), 'a ')
        assert self.engine(self.parse(r'a\Bb'), 'ab')
#        groups = self.engine(self.parse(r'\s*\b\w+\b\s*'), ' a ')
#        assert groups.data(0)[0] == ' a ', groups.data(0)[0]
#        groups = self.engine(self.parse(r'(\s*(\b\w+\b)\s*){3}', flags=ParserState._LOOP_UNROLL), ' a ab abc ')
#        assert groups.data(0)[0] == ' a ab abc ', groups.data(0)[0]

    def test_nested_group(self):
        pass
    
    def test_groups(self):
        pass
    
    def test_group_reference(self):
        pass
    
    def test_group(self):
        pass

    def test_conditional(self):
        pass

    def test_lookback_bug_1(self):
        pass
    
    def test_groups_in_lookback(self):
        pass
    
    def test_extended_groups(self):
        pass
    
    def test_ascii_escapes(self):
#        groups = self.engine(self.parse('\\d*', flags=ParserState.ASCII), '12x')
#        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
#        groups = self.engine(self.parse('\\D*', flags=ParserState.ASCII), 'x12')
#        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
#        groups = self.engine(self.parse('\\w*', flags=ParserState.ASCII), '12x a')
#        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
#        groups = self.engine(self.parse('\\W*', flags=ParserState.ASCII), ' a')
#        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
#        groups = self.engine(self.parse('\\s*', flags=ParserState.ASCII), '  a')
#        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
#        groups = self.engine(self.parse('\\S*', flags=ParserState.ASCII), 'aa ')
#        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        assert self.engine(self.parse(r'a\b ', flags=ParserState.ASCII), 'a ')
        assert not self.engine(self.parse(r'a\bb', flags=ParserState.ASCII), 'ab')
        assert not self.engine(self.parse(r'a\B ', flags=ParserState.ASCII), 'a ')
        assert self.engine(self.parse(r'a\Bb', flags=ParserState.ASCII), 'ab')
#        groups = self.engine(self.parse(r'\s*\b\w+\b\s*', flags=ParserState.ASCII), ' a ')
#        assert groups.data(0)[0] == ' a ', groups.data(0)[0]
#        groups = self.engine(self.parse(r'(\s*(\b\w+\b)\s*){3}', flags=ParserState._LOOP_UNROLL|ParserState.ASCII), ' a ab abc ')
#        assert groups.data(0)[0] == ' a ab abc ', groups.data(0)[0]

    def test_repeat(self):
        pass
    
    def test_prime(self):
        pass
    
