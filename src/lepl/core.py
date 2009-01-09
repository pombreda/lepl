 

from lepl.trace import LogMixin
from lepl.support import CircularFifo


class Disposable():
    '''
    Add logging info and the delayed closing to generators.
    '''
    
    def __init__(self, generator, logMixin, stream):
        super().__init__()
        self.__generator = generator
        self.__tag = '%s@%s' % (logMixin.describe(), stream)
        logMixin._debug('Created %s' % self)
        self.__running = False
        self.__closing = False
        
    def __next__(self):
        try:
            self.__running = True
            return next(self.__generator)
        finally:
            self.__running = False
            if self.__closing:
                self.__generator.close()
    
    def __iter__(self):
        return self
    
    def close(self):
        if self.__running:
            self.__closing = True
        else:
            self.__generator.close()
    
    def __str__(self):
        return self.__tag


def limited_depth(f):
    '''
    Generators should be decorated with this so that the depth of the search
    can be limited, freeing resources that are no longer needed.
    '''
    def call(self, stream):
        generator = Disposable(f(self, stream), self, stream)
        try:
            stream.core.register_generator(generator)
        except AttributeError:
            pass # Allow non-stream sequences
        return generator
    return call


def no_depth(f):
    '''
    When a match generator is known to only return one value (or none)
    there is no need to bother with the fifo in the core; instead we simply
    read and then disacrd the generator.
    '''
    def call(self, stream):
        generator = f(self, stream)
        value = None
        ok = False
        try:
            value = next(generator)
            ok = True
        except:
            pass
        generator.close()
        if ok:
            yield value
    return call

        
class Core():
    '''
    Data store for a single parse; embedded in the streams used to wrap the
    text being parsed.
    '''

    def __init__(self, search_depth=0, description_length=6):
        self.search_depth = search_depth
        self.description_length = description_length
        
    @property
    def search_depth():
        return len(self.__generators)
        
    @search_depth.setter
    def search_depth(self, depth):
        self.__generators = GeneratorLimiter(depth)
            
    def register_generator(self, generator):
        self.__generators.append(generator)
        

class GeneratorLimiter(LogMixin):
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
            self.__fifo = None
    
    def append(self, generator):
        self._debug('Appending %s' % generator)
        if self.__fifo:
            expired = self.__fifo.append(generator)
            if expired:
                self._debug('Closing %s' % expired)
                expired.close()
                
    def __len__(self):
        len(self.__fifo) if self.__fifo else 0
        

