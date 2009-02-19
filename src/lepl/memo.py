
from itertools import count

from lepl.matchers import BaseMatcher
from lepl.parser import tagged, GeneratorWrapper
from lepl.support import LogMixin



class RMemo(BaseMatcher):
    '''
    A simple memoizer for grammars that do not have left recursion.
    '''
    
    def __init__(self, matcher):
        super(RMemo, self).__init__()
        self._arg(matcher=matcher)
        self.__table = {}
        self.tag(self.matcher.describe)
        
    @tagged
    def __call__(self, stream):
        if stream not in self.__table:
            # we have no cache for this stream, so we need to generate the
            # entry.  we do not care about nested calls with the same stream
            # because this memoization is not for left recursion.  that means
            # that we can return a table around this generator immediately.
            self.__table[stream] = RTable(self.matcher(stream))
        return self.__table[stream].generator(self.matcher, stream)


class RTable(LogMixin):
    '''
    Wrap a generator so that separate uses all call the same core generator,
    which is itself tabulated as it unrolls.
    '''
    
    def __init__(self, generator):
        self.__generator = generator
        self.__table = []
        self.__stopped = False
        
    def __read(self, i):
        try:
            while i >= len(self.__table) and not self.__stopped:
                result = yield self.__generator
                self.__table.append(result)
        except StopIteration:
            self._stopped = True
        if i < len(self.__table):
            yield self.__table[i]
        else:
            raise StopIteration()
    
    def generator(self, matcher, stream):
        for i in count():
            yield (yield GeneratorWrapper(self.__read(i), 
                            DummyMatcher(self.__class__.__name__, matcher.describe), 
                            stream))


class DummyMatcher(object):
    
    def __init__(self, outer, inner):
        self.describe = '{0}({1})'.format(outer, inner)
        