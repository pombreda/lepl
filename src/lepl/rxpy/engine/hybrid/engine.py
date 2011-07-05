#LICENCE

from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.engine.simple.engine import SimpleEngine
from lepl.rxpy.support import UnsupportedOperation
from lepl.rxpy.engine.complex.engine import ComplexEngine


class HybridEngine(BaseMatchEngine):
    
    def __init__(self, parser_state, graph):
        self.__parser_state = parser_state
        self.__graph = graph
        self.__simple = SimpleEngine(parser_state, graph)
        self.__cached_complex = None
    
    def run(self, stream, pos=0, search=False):

        try:
            return self.__simple.run(stream, pos, search)
        except UnsupportedOperation:
            # TODO - restart from exact position (will need to set index in
            # compiled function stack by catching exception)
            return self.__complex.run(stream, pos=pos, search=search)
        
    @property
    def __complex(self):
        if self.__cached_complex is None:
            self.__cached_complex = ComplexEngine(self.__parser_state, self.__graph)
        return self.__cached_complex

        
