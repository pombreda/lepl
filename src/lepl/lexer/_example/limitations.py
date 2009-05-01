
from lepl import *
from lepl._example.support import Example


class Limitations(Example):

    def test_ambiguity(self):
        tokens = (Token(Integer()) | Token(r'\-'))[:] & Eos()
        self.examples([(lambda: list(tokens.match('1-2', config=Configuration.tokens())), "[(['1', '-2'], <SimpleGeneratorStream>)]")])
        matchers = (Integer() | Literal('-'))[:] & Eos()
        self.examples([(lambda: list(matchers.match('1-2')), "[(['1', '-2'], ''), (['1', '-', '2'], '')]")])
    
    def test_complete(self):
        abc = Token('abc')
        incomplete = abc(Literal('ab'))
        self.examples([(lambda: incomplete.parse('abc', config=Configuration.tokens()), "None")])
        abc = Token('abc')
        incomplete = abc(Literal('ab'), complete=False)
        self.examples([(lambda: incomplete.parse('abc', config=Configuration.tokens()), "['ab']")])
       