

def assert_type(name, value, type, none_ok=False):
    '''
    If the value is not of the given type, raise a syntax error.
    '''
    if none_ok and value == None: return
    if isinstance(value, type): return
    raise TypeError('{0} (value {1}) must be of type {2}.'
                    .format(name, repr(value), type.__name__))


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

        