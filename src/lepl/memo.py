
from itertools import count

from lepl.matchers import BaseMatcher


class Wrapper(object):
    
    def __init__(self, matcher, stream):
        self.__generator = matcher(stream)
        self.__stopped = False
        self.__table = []
        
    def __get(self, i):
        try:
            while i >= len(self.__table) and not self.__stopped:
                self.__extend()
        except StopIteration:
            self.__stopped = True
            self.__generator = None
        if self.__stopped:
            raise StopIteration()
        else:
            return self.__table[i]
        
    def __extend(self):
        self.__table.append(next(self.__generator))
    
    def proxy(self):
        for i in count():
            yield self.__get(i)


class Memo(BaseMatcher):
    
    def __init__(self, matcher, wrapper=Wrapper):
        super(Memo, self).__init__()
        self._arg(matcher=matcher)
        self._arg(wrapper=wrapper)
        self.__table = {}
        
    def __call__(self, stream):
        key = hash(stream) # try not to keep hold of resources?
        if key not in self.__table:
            self.__table[key] = self.wrapper(self.matcher, stream)
        return self.__table[key].proxy()
    

class LWrapper(Wrapper):
    
    def __init__(self, matcher, stream):
        super(LWrapper, self).__init__(matcher, stream)
        self.__counter = 0
        self.__limit = len(stream)
        
    def __extend(self):
        self.__counter += 1
        if self.__counter > self.__limit:
            raise StopIteration()
        self.__table.append(next(generator))
        self.__counter = 0


def LMemo(matcher):
    return Memo(matcher, wrapper=LWrapper)
    
