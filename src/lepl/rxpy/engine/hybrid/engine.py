#LICENCE

from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.engine.simple.engine import SimpleEngine
from lepl.rxpy.engine.complex.engine import ComplexEngine
from lepl.rxpy.support import UnsupportedOperation


class HybridEngine(BaseMatchEngine):
    
    def __init__(self, parser_state, graph):
        super(HybridEngine, self).__init__(parser_state, graph)
        self.__simple = SimpleEngine(parser_state, graph)
        self.__cached_complex = None
    
    def run(self, stream, pos=0, search=False):

        try:
            groups = self.__simple.run(stream, pos, search, fail_on_groups=False)
            return LazyGroups(groups, self.__simple.group_defined,
                lambda: self.__complex.run(stream, pos=pos, search=search))
        except UnsupportedOperation:
            return self.__complex.run(stream, pos=pos, search=search)
        
    @property
    def __complex(self):
        if self.__cached_complex is None:
            self.__cached_complex = ComplexEngine(self._parser_state, self._graph)
        return self.__cached_complex

        
class LazyGroups(object):

    def __init__(self, zero, more, get_rest):
        self.__zero = zero
        self.__more = more
        self.__get_rest = get_rest
        self.__cached_rest = None

    @property
    def __rest(self):
        if self.__more:
            if self.__cached_rest is None:
                self.__cached_rest = self.__get_rest()
            return self.__cached_rest
        else:
            return self.__zero

    def __len__(self):
        return len(self.__rest)

    def __bool__(self):
        # zero is sufficient to indicate if empty
        return bool(self.__zero)

    def __nonzero__(self):
        return self.__bool__()

    def __eq__(self, other):
        '''
        Ignores values from context (so does not work for comparison across
        matches).
        '''
        return type(self) == type(other) and str(self) == str(other)

    def __hash__(self):
        '''
        Ignores values from context (so does not work for comparison across
        matches).
        '''
        return hash(self.__str__())

    def __str__(self):
        '''
        Unique representation, used for eq and hash.  Ignores values from
        context (so does not work for comparison across matches).
        '''
        return str(self.__rest)

    def data(self, number):
        if number:
            return self.__rest.data(number)
        else:
            return self.__zero.data(0)

    def group(self, number, default=None):
        if number:
            return self.__rest.group(number, default=default)
        else:
            return self.__zero.group(0, default=default)

    def start(self, number):
        if number:
            return self.__rest.start(number)
        else:
            return self.__zero.start(0)

    def end(self, number):
        if number:
            return self.__rest.end(number)
        else:
            return self.__zero.end(0)

    @property
    def last_index(self):
        return self.__rest.last_index

    @property
    def last_group(self):
        return self.__rest.last_group

    @property
    def indices(self):
        return self.__rest.indices

    @property
    def groups(self):
        return self.__rest.groups
    