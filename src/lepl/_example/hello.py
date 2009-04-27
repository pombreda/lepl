
from lepl import *
from lepl._example.support import Example


class HelloWorldExample(Example):

    def test_hello(self):
        self.examples([(lambda: next(Literal('hello').match('hello world')),
                        "(['hello'], ' world')"),
                       (lambda: Literal('hello').parse_string('hello world'),
                        "['hello']")])
        
    def test_123(self):
        self.examples([(lambda: next(Integer().match('123 four five')),
                        "(['123'], ' four five')")])

    def test_and(self):
        self.examples([(lambda: next(And(Word(), Space(), Integer()).match('hello 123')),
                        "(['hello', ' ', '123'], '')"),
                       (lambda: next((Word() & Space() & Integer()).match('hello 123')),
                        "(['hello', ' ', '123'], '')"),
                       (lambda: next((Word() / Integer()).match('hello 123')),
                        "(['hello', ' ', '123'], '')"),
                       (lambda: (Word() / Integer()).parse_string('hello 123'),
                        "['hello', ' ', '123']")])
        


