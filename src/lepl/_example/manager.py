
from lepl._example.support import Example
from lepl import *


class ResourceExample(Example):
    
    def test_no_limit(self):
        matcher = (Literal('*')[:,...][2] & Eos()).match_string()('*' * 4)
        self.examples([(lambda: list(matcher), 
                        "[(['****'], Chunk('')[0:]), (['***', '*'], Chunk('')[0:]), (['**', '**'], Chunk('')[0:]), (['*', '***'], Chunk('')[0:]), (['****'], Chunk('')[0:])]")])

    def test_limit(self):
        matcher = (Literal('*')[:,...][2] & Eos()).match_string(min_queue=1)('*' * 4)
        self.examples([(lambda: list(matcher), 
                        "[(['****'], Chunk('')[0:])]")])

