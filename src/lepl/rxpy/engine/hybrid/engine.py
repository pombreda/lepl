#LICENCE


from lepl.rxpy.engine.simple.engine import SimpleEngine
from lepl.rxpy.support import UnsupportedOperation
from lepl.rxpy.engine.complex.engine import ComplexEngine


class HybridEngine(SimpleEngine):
    
    def __init__(self, parser_state, graph):
        super(HybridEngine, self).__init__(parser_state, graph)
        self.__cached_fallback = None
    
    def run(self, text, pos=0, search=False):
        self._group_defined = False

        try:
            results = self._run_from(0, text, pos, search)
            
            if self._group_defined:
                # reprocess using only the exact region matched
                return self.__fallback.run(text, results.start(0))
            else:
                return results
            
        except UnsupportedOperation:
            # TODO - restart from exact position (will need to set index in
            # compiled function stack by catching exception)
            return self.__fallback.run(text, pos=pos, search=search)
        
    @property
    def __fallback(self):
        if self.__cached_fallback is None:
            self.__cached_fallback = ComplexEngine(self._parser_state, self._graph)
        return self.__cached_fallback

        
