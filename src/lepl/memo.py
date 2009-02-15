
from itertools import count

from lepl.matchers import BaseMatcher


class Wrapper(object):
    
    def __init__(self, matcher, stream):
        self._generator = matcher(stream)
        self._stopped = False
        self._table = []
        
    def _get(self, i):
        try:
            while i >= len(self._table) and not self._stopped:
                result = yield self._generator
                self._table.append(result)
        except StopIteration:
            self._stopped = True
            self._generator = None
        if not self._stopped:
            yield self._table[i]
        
    def proxy(self):
        for i in count():
            yield (yield self._get(i))
            

class Memo(BaseMatcher):
    
    def __init__(self, matcher, wrapper=Wrapper):
        super(Memo, self).__init__()
        self._arg(matcher=matcher)
        self._karg(wrapper=wrapper)
        self.__table = {}
        
    def __call__(self, stream):
        if stream not in self.__table:
            self.__table[stream] = self.wrapper(self.matcher, stream)
        return self.__table[stream].proxy()
    

class LWrapper(Wrapper):
    
    def __init__(self, matcher, stream):
        super(LWrapper, self).__init__(matcher, stream)
        self.__counter = 0
        self.__limit = 2
        
    def _get(self, i):
        self.__counter += 1
        print(self.__counter)
        if self.__counter > self.__limit:
            self._stopped = True
            
        try:
            while i >= len(self._table) and not self._stopped:
                result = yield self._generator
                print(len(self._table), '=', result)
                self._table.append(result)
                
                self.__counter = 0
                
        except StopIteration:
            self._stopped = True
            self._generator = None
        if not self._stopped:
            print('>>>>>>>>>>>>>', self._table[i])
            yield self._table[i]


def LMemo(matcher):
    return Memo(matcher, wrapper=LWrapper)
    
