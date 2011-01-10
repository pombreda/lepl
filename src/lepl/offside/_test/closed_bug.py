
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class ClosedBugTest(TestCase):
    
    def test_as_given(self):
        empty = ~Line(Empty())
        word = Token(Word())
        comment = ~Line(Token('#.*'))
        CLine = ContinuedBLineFactory(Token(r'\\'))
        token = word[1:]
        block = Delayed()
        line = ((CLine(token) | block) > list) | empty | comment
        block += CLine((token)) & Block(line[:])
        program = (line[:] & Eos())
        program.config.default_line_aware(block_policy=rightmost)
        self.run_test(program.get_parse(), False)

    def test_fixed(self):
        #basicConfig(level=DEBUG)
        empty = ~Line(Empty())
        word = Token(Word())
        text = word[1:]
        block = Delayed()
        line = BLine(text) | block | empty
        block += Block(line[:]) > list
        program = block[:] & Eos()
        program.config.default_line_aware(block_policy=to_right, block_start=-1)
        self.run_test(program.get_parse(), True)
        
    def run_test(self, parser, ok):
        try:
            result = parser("""
a1
a2
    b2
        c2
    b2
    b2
        c2
           d2
            e2
    b2

a3
    b3

a4
    """)
            if ok:
                assert result == [['a1', 'a2', ['b2', ['c2'], 'b2', 'b2', ['c2', ['d2', ['e2']]], 'b2'], 'a3', ['b3'], 'a4']], result
        except:
            if ok:
                raise
            ok = True
        if not ok:
            assert False, 'expected error'
            