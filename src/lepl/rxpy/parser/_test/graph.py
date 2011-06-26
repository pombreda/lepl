#LICENCE


from lepl.rxpy.graph._test.lib import GraphTest
from lepl.rxpy.parser.pattern import parse_pattern
from lepl.rxpy.parser.support import ParserState
from lepl.rxpy.engine.base import BaseMatchEngine


def parse(pattern, flags=0):
    return parse_pattern(pattern, BaseMatchEngine, flags=flags)

class ReprTest(GraphTest):
    
    def test_already_connected_bug(self):
        parse('a')
        parse('b')
        parse('(c|e)')
        parse('d')
        parse('(c|e)')
        parse('c{1,2}', )
        parse('c{1,2}')
        parse('(c|e){1,2}', flags=ParserState._LOOP_UNROLL)
        parse('(c|e){1,2}')
        parse('(c|e){1,2}?')
        parse('(b|(c|e){1,2}?|d)')
        parse('(?:b|(c|e){1,2}?|d)')
        parse('(?:b|(c|e){1,2}?|d)+?')
        parse('(.)')
        parse('a(?:b|(c|e){1,2}?|d)+?(.)')

    def test_w3_bug(self):
        self.assert_graphs(parse('\w{3}(?_l)$'),
"""digraph {
 0 [label="\\\\w"]
 1 [label="\\\\w"]
 2 [label="\\\\w"]
 3 [label="$"]
 4 [label="Match"]
 0 -> 1
 1 -> 2
 2 -> 3
 3 -> 4
}""")
        self.assert_graphs(parse('(\w)$'),
"""digraph {
 0 [label="(?P<1>"]
 1 [label="\\\\w"]
 2 [label=")"]
 3 [label="$"]
 4 [label="Match"]
 0 -> 1
 1 -> 2
 2 -> 3
 3 -> 4
}""")
        self.assert_graphs(parse('(\w){3}$(?_l)'),
"""digraph {
 0 [label="(?P<1>"]
 1 [label="\\\\w"]
 2 [label=")"]
 3 [label="(?P<1>"]
 4 [label="\\\\w"]
 5 [label=")"]
 6 [label="(?P<1>"]
 7 [label="\\\\w"]
 8 [label=")"]
 9 [label="$"]
 10 [label="Match"]
 0 -> 1
 1 -> 2
 2 -> 3
 3 -> 4
 4 -> 5
 5 -> 6
 6 -> 7
 7 -> 8
 8 -> 9
 9 -> 10
}""")
