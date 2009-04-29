
from lepl import *
from lepl._example.support import Example


class MatcherExample(Example):
    
    def test_most(self):
        self.examples([
            (lambda: Literal('hello').parse_string('hello world'),
             "['hello']"),

            (lambda: Any().parse_string('hello world'), 
             "['h']"),
            (lambda: Any('abcdefghijklm')[0:].parse_string('hello world'), 
             "['h', 'e', 'l', 'l']"),

            (lambda: And(Any('h'), Any()).parse_string('hello world'), 
             "['h', 'e']"),
            (lambda: And(Any('h'), Any('x')).parse_string('hello world'), 
             "None"),

            (lambda: Or(Any('x'), Any('h'), Any('z')).parse_string('hello world'), 
             "['h']"),
            (lambda: Or(Any('h'), Any()[3]).parse_string('hello world'), 
             "['h']"),

            (lambda: Repeat(Any(), 3, 3).parse_string('12345'), 
             "['1', '2', '3']"),

            (lambda: Repeat(Any(), 3).parse_string('12345'), 
             "['1', '2', '3', '4', '5']"),
            (lambda: Repeat(Any(), 3).parse_string('12'),
             "None"),

            (lambda: next(Lookahead(Literal('hello')).match('hello world')), 
             "([], 'hello world')"),
            (lambda: Lookahead(Literal('hello')).parse('hello world'), 
             "[]"),
            (lambda: Lookahead('hello').parse_string('goodbye cruel world'), 
             "None"),
            (lambda: (~Lookahead('hello')).parse_string('hello world'), 
             "None"),
            (lambda: (~Lookahead('hello')).parse_string('goodbye cruel world'), 
             "[]"),

            (lambda: (Drop('hello') / 'world').parse_string('hello world'), 
             "[' ', 'world']"),
            (lambda: (Lookahead('hello') / 'world').parse_string('hello world'), 
             "None")])


    def test_multiple_or(self):
        matcher = Or(Any('h'), Any()[3]).match('hello world')
        assert str(next(matcher)) == "(['h'], 'ello world')"
        assert str(next(matcher)) == "(['h', 'e', 'l'], 'lo world')"


    def test_repeat(self):
        matcher = Repeat(Any(), 3).match('12345')
        assert str(next(matcher)) == "(['1', '2', '3', '4', '5'], '')"
        assert str(next(matcher)) == "(['1', '2', '3', '4'], '5')"
        assert str(next(matcher)) == "(['1', '2', '3'], '45')"
        
        matcher = Repeat(Any(), 3, None, 'b').match('12345')
        assert str(next(matcher)) == "(['1', '2', '3'], '45')"
        assert str(next(matcher)) == "(['1', '2', '3', '4'], '5')"
        assert str(next(matcher)) == "(['1', '2', '3', '4', '5'], '')"



    def test_show(self):
        
        def show(results):
            print('results:', results)
            return results

        self.examples([
            (lambda: Apply(Any()[:,...], show).parse_string('hello world'), 
             "[['hello world']]"),
            (lambda: Apply(Any()[:,...], show, raw=True).parse_string('hello world'),
             "['hello world']")])

