#LICENCE


from lepl.rxpy.support import _CHARS
from lepl.rxpy.graph._test.lib import GraphTest
from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.parser.replace import parse_replace
from lepl.rxpy.parser.pattern import parse_pattern


class DummyEngine(BaseMatchEngine):
    REQUIRE = _CHARS
    

def parse(pattern, replacement):
    (state, _graph) = parse_pattern(pattern, BaseMatchEngine)
    return parse_replace(replacement, state)


class ParserTest(GraphTest):
    
    def test_string(self):
        self.assert_graphs(parse('', 'abc'), 
"""digraph {
 0 [label="abc"]
 1 [label="Match"]
 0 -> 1
}""")
        
    def test_single_group(self):
        self.assert_graphs(parse('(.)', '\\1'), 
"""digraph {
 0 [label="\\\\1"]
 1 [label="Match"]
 0 -> 1
}""")

    def test_g_numbered_group(self):
        self.assert_graphs(parse('(.)', '\\g<1>'),
"""digraph {
 0 [label="\\\\1"]
 1 [label="Match"]
 0 -> 1
}""")

    def test_g_named_group(self):
        self.assert_graphs(parse('(?P<foo>.)', 'a\\g<foo>b'),
"""digraph {
 0 [label="a"]
 1 [label="\\\\1"]
 2 [label="b"]
 3 [label="Match"]
 0 -> 1
 1 -> 2
 2 -> 3
}""")

