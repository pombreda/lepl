#LICENCE

from lepl.rxpy.alphabet.digits import Digits
from lepl.rxpy.parser.support import ParserState
from lepl.rxpy.engine._test.base import BaseTest
from lepl.stream.factory import DEFAULT_STREAM_FACTORY


class DigitsTest(BaseTest):
    
    def default_alphabet(self):
        return Digits()
    
    def default_factory(self):
        return DEFAULT_STREAM_FACTORY.from_sequence

    def test_string(self):
        assert self.engine(self.parse('1'), [1])
        assert self.engine(self.parse('123'), [1,2,3])
        assert self.engine(self.parse('123'), [1,2,3,4])
        assert not self.engine(self.parse('123'), [1,2])
        
    def test_dot(self):
        assert self.engine(self.parse('1.3'), [1,2,3])
        assert self.engine(self.parse('...'), [1,2,3,4])
        assert not self.engine(self.parse('...'), [1,2])
#        assert not self.engine(self.parse('1.2'), [1,None,2])
#        assert not self.engine(self.parse('1.2', flags=ParserState.DOT_ALL), [1,None,2])
       
    def test_char(self):
        assert self.engine(self.parse('[12]'), [1])
        assert self.engine(self.parse('[12]'), [2])
        assert not self.engine(self.parse('[12]'), [3])

    def test_group(self):
        groups = self.engine(self.parse('(.).'), [1,2])
        assert len(groups) == 1, len(groups)
        groups = self.engine(self.parse('((.).)'), [1,2])
        assert len(groups) == 2, len(groups)
        
    def test_group_reference(self):
        assert self.engine(self.parse('(.)\\1'), [1,1])
        assert not self.engine(self.parse('(.)\\1'), [1,2])
 
    def test_split(self):
        assert self.engine(self.parse('1*2'), [2])
        assert self.engine(self.parse('1*2'), [1,2])
        assert self.engine(self.parse('1*2'), [1,1,2])
        assert not self.engine(self.parse('1*2'), [1,1])
        groups = self.engine(self.parse('1*'), [1,1,1])
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('1*'), [1,1,2])
        assert len(groups.data(0)[0]) == 2, groups[0][0]
        
    def test_nested_group(self):
        groups = self.engine(self.parse('(.)*'), [1,2])
        assert len(groups) == 1

    def test_lookahead(self):
        assert self.engine(self.parse('1(?=2)'), [1,2])
        assert not self.engine(self.parse('1(?=2)'), [1,3])
        assert not self.engine(self.parse('1(?!2)'), [1,2])
        assert self.engine(self.parse('1(?!2)'), [1,3])
    
    def test_lookback(self):
        assert self.engine(self.parse('.(?<=1)'), [1])
        assert not self.engine(self.parse('.(?<=1)'), [2])
        assert not self.engine(self.parse('.(?<!1)'), [1])
        assert self.engine(self.parse('.(?<!1)'), [2])
    
    def test_conditional(self):
        assert self.engine(self.parse('(.)?2(?(1)\\1)'), [1,2,1])
        assert not self.engine(self.parse('(.)?2(?(1)\\1)'), [1,2,3])
        assert self.engine(self.parse('(.)?2(?(1)\\1|3)'), [2,3])
        assert not self.engine(self.parse('(.)?2(?(1)\\1|3)'), [2,4])
        
    def test_star_etc(self):
        assert self.engine(self.parse('1*2'), [2])
        assert self.engine(self.parse('1*2'), [1,2])
        assert self.engine(self.parse('1*2'), [1,1,2])
        assert not self.engine(self.parse('1+2'), [2])
        assert self.engine(self.parse('1+2'), [1,2])
        assert self.engine(self.parse('1+2'), [1,1,2])
        assert self.engine(self.parse('1?2'), [2])
        assert self.engine(self.parse('1?2'), [1,2])
        assert not self.engine(self.parse('1?2'), [1,1,2])
        
        assert self.engine(self.parse('1*2', flags=ParserState._LOOP_UNROLL), [2])
        assert self.engine(self.parse('1*2', flags=ParserState._LOOP_UNROLL), [1,2])
        assert self.engine(self.parse('1*2', flags=ParserState._LOOP_UNROLL), [1,1,2])
        assert not self.engine(self.parse('1+2', flags=ParserState._LOOP_UNROLL), [2])
        assert self.engine(self.parse('1+2', flags=ParserState._LOOP_UNROLL), [1,2])
        assert self.engine(self.parse('1+2', flags=ParserState._LOOP_UNROLL), [1,1,2])
        assert self.engine(self.parse('1?2', flags=ParserState._LOOP_UNROLL), [2])
        assert self.engine(self.parse('1?2', flags=ParserState._LOOP_UNROLL), [1,2])
        assert not self.engine(self.parse('1?2', flags=ParserState._LOOP_UNROLL), [1,1,2])

    def test_counted(self):
        groups = self.engine(self.parse('1{2}', flags=ParserState._LOOP_UNROLL), [1,1,1])
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,2}', flags=ParserState._LOOP_UNROLL), [1,1,1])
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,}', flags=ParserState._LOOP_UNROLL), [1,1,1])
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('1{2}?', flags=ParserState._LOOP_UNROLL), [1,1,1])
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,2}?', flags=ParserState._LOOP_UNROLL), [1,1,1])
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,}?', flags=ParserState._LOOP_UNROLL), [1,1,1])
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,2}?2', flags=ParserState._LOOP_UNROLL), [1,1,2])
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,}?2', flags=ParserState._LOOP_UNROLL), [1,1,2])
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        
        assert self.engine(self.parse('1{0,}?2', flags=ParserState._LOOP_UNROLL), [2])
        assert self.engine(self.parse('1{0,}?2', flags=ParserState._LOOP_UNROLL), [1,2])
        assert self.engine(self.parse('1{0,}?2', flags=ParserState._LOOP_UNROLL), [1,1,2])
        assert not self.engine(self.parse('1{1,}?2', flags=ParserState._LOOP_UNROLL), [2])
        assert self.engine(self.parse('1{1,}?2', flags=ParserState._LOOP_UNROLL), [1,2])
        assert self.engine(self.parse('1{1,}?2', flags=ParserState._LOOP_UNROLL), [1,1,2])
        assert self.engine(self.parse('1{0,1}?2', flags=ParserState._LOOP_UNROLL), [2])
        assert self.engine(self.parse('1{0,1}?2', flags=ParserState._LOOP_UNROLL), [1,2])
        assert not self.engine(self.parse('1{0,1}?2', flags=ParserState._LOOP_UNROLL), [1,1,2])

        groups = self.engine(self.parse('1{2}'), [1,1,1])
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,2}'), [1,1,1])
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,}'), [1,1,1])
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('1{2}?'), [1,1,1])
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,2}?'), [1,1,1])
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,}?'), [1,1,1])
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,2}?2'), [1,1,2])
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('1{1,}?2'), [1,1,2])
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        
        assert self.engine(self.parse('1{0,}?2'), [2])
        assert self.engine(self.parse('1{0,}?2'), [1,2])
        assert self.engine(self.parse('1{0,}?2'), [1,1,2])
        assert not self.engine(self.parse('1{1,}?2'), [2])
        assert self.engine(self.parse('1{1,}?2'), [1,2])
        assert self.engine(self.parse('1{1,}?2'), [1,1,2])
        assert self.engine(self.parse('1{0,1}?2'), [2])
        assert self.engine(self.parse('1{0,1}?2'), [1,2])
        assert not self.engine(self.parse('1{0,1}?2'), [1,1,2])

    def test_ascii_escapes(self):
        self.engine(self.parse('\\d*', flags=ParserState.ASCII), [])

    def test_unicode_escapes(self):
        assert self.engine(self.parse('\\d'), [1])
        assert not self.engine(self.parse('\\D'), [1])
        assert not self.engine(self.parse('\\w'), [1])
        assert self.engine(self.parse('\\W'), [1])
        assert not self.engine(self.parse('\\s'), [1])
        assert self.engine(self.parse('\\S'), [1])
        assert not self.engine(self.parse('\\b'), [1])
        assert self.engine(self.parse('\\B'), [])

    def test_or(self):
        assert self.engine(self.parse('1|2'), [1])
        assert self.engine(self.parse('1|2'), [2])
        assert not self.engine(self.parse('1|2'), 'c')
        assert self.engine(self.parse('(?:1|13)$'), [1,3])
        
    def test_search(self):
        assert self.engine(self.parse('1'), [1,2], search=True)
        
