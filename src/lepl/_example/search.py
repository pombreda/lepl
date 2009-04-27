
from lepl import *
from lepl._example.support import Example


class SearchExample(Example):
    
    def test_greedy(self):
        
        any = Any()[:,...]
        split = any & any & Eos()
        match = split.string_matcher()

        def example1():
            return [pair[0] for pair in match('****')]
        
        self.examples([(example1, 
"[['****'], ['***', '*'], ['**', '**'], ['*', '***'], ['****']]")])
        
    def test_generous(self):
        
        any = Any()[::'b',...]
        split = any & any & Eos()
        match = split.string_matcher()

        def example1():
            return [pair for (pair, stream) in match('****')]
        
        self.examples([(example1, 
"[['****'], ['*', '***'], ['**', '**'], ['***', '*'], ['****']]")])
        
