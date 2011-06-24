#LICENCE


from lepl.rxpy.compat.module import Re
from lepl.rxpy.parser.pattern import parse_pattern
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
    
    def engine(self, parse, text, search=False, ticks=None, **kargs):
        engine = self.default_engine()(*parse, **kargs)
        result = engine.run(text, search=search)
        if ticks is not None:
            assert engine.ticks == ticks, engine.ticks
        return result

    def assert_groups(self, pattern, text, groups):
        results = self.engine(self.parse(pattern), text)
        assert results.groups == groups, results.groups 
