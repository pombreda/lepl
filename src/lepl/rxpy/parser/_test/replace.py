#LICENCE


from lepl.rxpy.lib import _CHARS
from lepl.rxpy.graph._test.lib import GraphTest
from lepl.rxpy.engine.base import BaseEngine
from lepl.rxpy.parser.replace import parse_replace
from lepl.rxpy.parser.pattern import parse_pattern


class DummyEngine(BaseEngine):
    REQUIRE = _CHARS
    

def parse(pattern, replacement):
    (state, _graph) = parse_pattern(pattern, BaseEngine)
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

        
