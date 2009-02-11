
from itertools import count

from lepl.matchers import BaseMatcher


class Wrapper(object):
    
    def __init__(self, matcher, stream):
        self._generator = matcher(stream)
        self.__stopped = False
        self._table = []
        
    def __get(self, i):
        try:
            while i >= len(self._table) and not self.__stopped:
                self._extend()
        except StopIteration:
            self.__stopped = True
            self._generator = None
        if self.__stopped:
            raise StopIteration()
        else:
            return self._table[i]
        
    def _extend(self):
        self._table.append(next(self._generator))
    
    def proxy(self):
        for i in count():
            yield self.__get(i)


class Memo(BaseMatcher):
    
    def __init__(self, matcher, wrapper=Wrapper):
        super(Memo, self).__init__()
        self._arg(matcher=matcher)
        self._karg(wrapper=wrapper)
        self.__table = {}
        
    def match(self, stream):
        key = hash(stream) # try not to keep hold of resources?
        if key not in self.__table:
            self.__table[key] = self.wrapper(self.matcher, stream)
        return self.__table[key].proxy()
    

class LWrapper(Wrapper):
    
    def __init__(self, matcher, stream):
        super(LWrapper, self).__init__(matcher, stream)
        self.__counter = 0
        self.__limit = 2
        
    def _extend(self):
        self.__counter += 1
        print(self.__counter)
        if self.__counter > self.__limit:
            raise StopIteration()
        self._table.append(next(self._generator))
        self.__counter = 0


def LMemo(matcher):
    return Memo(matcher, wrapper=LWrapper)
    
