 

from lepl.support import CircularFifo


def limited_depth(f):
    def call(self, stream):
        generator = f(self, stream)
        stream.core.register_generator(generator)
        return generator
    return call

def no_depth(f):
    def call(self, stream):
        generator = f(self, stream)
        def single():
            try:
                yield next(generator)
            finally:
                generator.close()
        return single()
    return call
        

class Core():
    '''
    Data store for a single parse; embedded in the streams used to wrap the
    text being parsed.
    '''

    def __init__(self, search_depth=0):
        self.search_depth = dsearch_depth
        
    @property
    def search_depth():
        return len(self.__generators)
        
    @search_depth.setter
    def search_depth(self, depth):
        self.__generators = GeneratorLimiter(depth)
            
    def register_generator(self, generator):
        self.__generators.append(generator)
        

class GeneratorLimiter():
    '''
    If size is greater than zero then only that many generators are kept
    during a parse; oldest generators are closed as necessary.
    
    It would be nice to also expire them by distance from the current parse
    position.
    '''

    def __init__(self, size):
        if size > 0:
            self.__fifo = CircularFifo(size)
        else:
            self.__fifo = None
    
    def append(self, generator):
        if self.__fifo:
            expired = self.__fifo.append(generator)
            if expired:
                expired.close()
                
    def __len__(self):
        len(self.__fifo) if self.__fifo else 0
        

