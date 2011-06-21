#LICENCE

from subprocess import Popen, PIPE
from unittest import TestCase
from io import StringIO


class GraphTest(TestCase):
    
    def assert_graphs(self, result, target):
        (_state, graph) = result
        graph = repr(graph)
        ok = graph == target
        if not ok:
            try:
                print('target:\n' + target)
                print(Popen(["graph-easy", "--as_ascii"], stdin=PIPE, stdout=PIPE)\
                    .communicate(target.encode('ascii'))[0].decode('ascii'))
                print('result:\n' + graph)
                print(Popen(["graph-easy", "--as_ascii"], stdin=PIPE, stdout=PIPE)\
                      .communicate(graph.encode('ascii'))[0].decode('ascii'))
            except Exception as e:
                print(e)
            assert False
