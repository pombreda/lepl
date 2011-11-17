#LICENCE

from subprocess import Popen, PIPE
from unittest import TestCase


class GraphTest(TestCase):
    
    def assert_graphs(self, result, target):
        (_state, graph) = result
        graph = repr(graph)
        ok = graph == target
        if not ok:
            try:
                print('target:\n' + target)
                print(Popen(["graph-easy", "--as_ascii"], stdin=PIPE, stdout=PIPE)
                    .communicate(target.encode('utf8'))[0].decode('utf8'))
                print('result:\n' + graph)
                print(Popen(["graph-easy", "--as_ascii"], stdin=PIPE, stdout=PIPE)
                      .communicate(graph.encode('utf8'))[0].decode('utf8'))
            except Exception as e:
                print(e)
                raise
            #assert False
