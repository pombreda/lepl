#LICENCE


from lepl.rxpy.compat.module import Re
from lepl.rxpy.parser.pattern import parse_pattern
from lepl.stream.factory import DEFAULT_STREAM_FACTORY
from lepl.support.lib import unimplemented


class BaseTest(object):

    @unimplemented
    def default_engine(self):
        '''
        Should return an engine class
        '''
        
    def default_alphabet(self):
        return None
    
    def setUp(self):
        self._alphabet = self.default_alphabet()
        self._re = Re(self.default_engine(), 'Test engine')
        
    def parse(self, regexp, flags=0, alphabet=None):
        return parse_pattern(regexp, self.default_engine(),
                             alphabet=alphabet if alphabet else self._alphabet, 
                             flags=flags)
    
    def engine(self, parse, text, factory=None,
               search=False, ticks=None, max_depth=None, **kargs):
        engine = self.default_engine()(*parse, **kargs)
        if not factory:
            factory = DEFAULT_STREAM_FACTORY.from_string
        stream = factory(text)
        result = engine.run(stream, search=search)
        if ticks is not None:
            assert engine.ticks == ticks, engine.ticks
        if max_depth is not None:
            assert engine.max_depth == max_depth, engine.max_depth
        return result

    def assert_groups(self, pattern, text, groups):
        results = self.engine(self.parse(pattern), text)
        assert results.groups == groups, results.groups 
