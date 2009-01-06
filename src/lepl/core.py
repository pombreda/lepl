

                                  
        
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
        

class CircularFifo():
    
    def __init__(self, size):
        '''
        Stores up to size entries.  Once full, appending a further value
        will discard (and return) the oldest still present.
        '''
        self.__size = 0
        self.__next = 0
        self.__buffer = [None] * size
        
    def append(self, value):
        '''
        This returns a value on overflow, otherwise None.
        '''
        capacity = len(self.__buffer)
        if self.__size == capacity:
            dropped = self.__buffer[self.__next]
        else:
            dropped = None
            self.__size += 1
        self.__buffer[self.__next] = value
        self.__next = (self.__next + 1) % capacity
        return dropped

    def __len__(self):
        return len(self.__buffer)
