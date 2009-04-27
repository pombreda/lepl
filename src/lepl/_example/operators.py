
from lepl import *
from lepl._example.support import Example


class OperatorExamples(Example):
    
    def test_errors(self):
        self.examples([(lambda: eval("('Mr' | 'Ms') // Word()"),
                        "TypeError: unsupported operand type(s) for |: 'str' and 'str'\n"),
                       (lambda: eval("('Mr' // Word() > 'man' | 'Ms' // Word() > 'woman')"),
                        '''  File "<string>", line None
SyntaxError: The operator > for And was applied to a matcher (<Or>). Check syntax and parentheses.
''')])

    def test_override(self):
        
        abcd = None
        with Override(or_=And, and_=Or):
            abcd = (Literal('a') & Literal('b')) | ( Literal('c') & Literal('d'))
        
        self.examples([(lambda: abcd.parse_string('ac'), "['a', 'c']"),
                       (lambda: abcd.parse_string('ab'), "None")])
            
        sentence = None
        word = Letter()[:,...]
        with Separator(r'\s+'):
            sentence = word[1:]
            
        self.examples([(lambda: sentence.parse_string('hello world'), 
                        "['hello', ' ', 'world']")])
        
