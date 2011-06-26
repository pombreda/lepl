#LICENCE


from lepl.support.lib import UnimplementedMethod
from lepl.rxpy.graph.base_compilable import BaseMatchTarget


class BaseMatchEngine(BaseMatchTarget):
    '''
    Subclasses can redefine REFUSE and REQUIRE to indicate what flags
    should be set (REQUIRE) or trigger an error (REFUSE).
    '''
    
    REFUSE = 0
    REQUIRE = 0
    
    def __init__(self, parser_state, graph):
        '''
        Create an engine instance.
        
        - `parser_state` is an instance of `ParserState` and contains things
          like alphabet and flags.
          
        - `graph` is the entry node into a graph of opcodes
        '''
        self._parser_state = parser_state
        self._graph = graph

    #noinspection PyUnusedLocal
    def run(self, text, pos=0, search=False):
        '''
        Search or match the given text.
        
        - `text` is the input to match (terminated appropriately)
        
        - `pos` is the initial position to start matching at
        
        - `search` is `True` if characters (from `pos` on) can be discarded
          while searching for a match; if `False` the match must start at
          `text[pos]`.
        
        A `Groups` instance should be returned.
        '''
        raise UnimplementedMethod('Engines must implement run()')

