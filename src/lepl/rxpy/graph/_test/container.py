#LICENCE

from lepl.rxpy.graph._test.lib import GraphTest
from lepl.rxpy.graph.base_graph import BaseLabelledNode
from lepl.rxpy.graph.container import Sequence, Alternatives, Loop
from lepl.rxpy.graph.opcode import Match
from lepl.rxpy.parser.support import ParserState


def n(label):
    return BaseLabelledNode(label=str(label))


def build(sequence):
    return None, sequence.join(Match(), ParserState())


class DummyState(object):
    
    def __init__(self, flags=0):
        self.flags = flags


class ContainerTest(GraphTest):
    
    def test_sequence(self):
        self.assert_graphs(build(Sequence([n(1), n(2), n(3)])),
"""digraph {
 0 [label="1"]
 1 [label="2"]
 2 [label="3"]
 3 [label="Match"]
 0 -> 1
 1 -> 2
 2 -> 3
}""")
        
    def test_alternatives(self):
        self.assert_graphs(build(Alternatives()),
"""digraph {
 0 [label="NoMatch"]
 1 [label="Match"]
 0 -> 1
}""")
        self.assert_graphs(build(Alternatives([Sequence([n(1), n(2), n(3)])])),
"""digraph {
 0 [label="1"]
 1 [label="2"]
 2 [label="3"]
 3 [label="Match"]
 0 -> 1
 1 -> 2
 2 -> 3
}""")
        self.assert_graphs(build(Alternatives([Sequence([n(1), n(2), n(3)]),
                                               Sequence([n(4), n(5)]),
                                               Sequence()])),
"""digraph {
 0 [label="...|..."]
 1 [label="1"]
 2 [label="4"]
 3 [label="Match"]
 4 [label="5"]
 5 [label="2"]
 6 [label="3"]
 0 -> 1
 0 -> 2
 0 -> 3
 2 -> 4
 4 -> 3
 1 -> 5
 5 -> 6
 6 -> 3
}""")
        
    def test_loop(self):
        self.assert_graphs(build(Loop([Sequence([n(1), n(2)])],
                                      parser_state=DummyState(), lazy=True,
                                      label='x')),
"""digraph {
 0 [label="x"]
 1 [label="Match"]
 2 [label="1"]
 3 [label="2"]
 4 [label="!"]
 0 -> 1
 0 -> 2
 2 -> 3
 3 -> 4
 4 -> 0
}""")
        self.assert_graphs(build(Loop([Sequence([n(1), n(2)])],
                                      parser_state=DummyState(), lazy=False,
                                      label='x')),
"""digraph {
 0 [label="x"]
 1 [label="1"]
 2 [label="Match"]
 3 [label="2"]
 4 [label="!"]
 0 -> 1
 0 -> 2
 1 -> 3
 3 -> 4
 4 -> 0
}""")
