
from lepl import *
from lepl._example.support import Example


class ResourceExample(Example):
    
    def test_no_limit(self):
        matcher = (Literal('*')[:,...][2] & Eos()).match('*' * 4)
        self.examples([(lambda: list(matcher), 
                        "[(['****'], ''), (['***', '*'], ''), (['**', '**'], ''), (['*', '***'], ''), (['****'], '')]")])

    def test_limit(self):
        config = Configuration(monitors=[GeneratorManager(queue_len=1)])
        matcher = (Literal('*')[:,...][2] & Eos()).match('*' * 4, config)
        self.examples([(lambda: list(matcher), 
                        "[(['****'], '')]")])

