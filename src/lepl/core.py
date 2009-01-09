 

from lepl.trace import LogMixin
from lepl.support import CircularFifo


class Core():
    '''
    Data store for a single parse; embedded in the streams used to wrap the
    text being parsed.
    '''

    def __init__(self, max_depth=0, max_width=0, description_length=6):
        self.max_depth = max_depth
        self.max_width = max_width
        self.description_length = description_length
        self.__depth = 0
        
    def down(self):
        self.__depth += 1
        return self.max_depth > 0 and self.__depth > self.max_depth
        
    def up(self):
        self.__depth -= 1


class LimitedGeneratorStack(LogMixin):
    '''
    If size is greater than zero then only that many generators are kept
    during a parse; oldest generators are closed as necessary.
    
    It would be nice to also expire them by distance from the current parse
    position.
    '''

    def __init__(self, size):
        super().__init__()
        if size > 0:
            self.__fifo = CircularFifo(size)
        else:
            self.__fifo = []
    
    def append(self, generator, data):
        self._debug('Appending %s' % generator)
        expired = self.__fifo.append((generator, data))
        if expired:
            (generator, data) = expired
            self._debug('Expiring %s' % generator)
            generator.close()
            
    def pop(self):
        return self.__fifo.pop(-1)
                
    def __len__(self):
        return len(self.__fifo)
