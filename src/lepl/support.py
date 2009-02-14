
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Library routines / utilities (some unused).
'''


def assert_type(name, value, type_, none_ok=False):
    '''
    If the value is not of the given type, raise a syntax error.
    '''
    if none_ok and value is None: return
    if isinstance(value, type_): return
    raise TypeError('{0} (value {1}) must be of type {2}.'
                    .format(name, repr(value), type_.__name__))


class CircularFifo():
    '''
    A FIFO queue with a fixed maximum size that silently discards data on 
    overflow.  It supports iteration for reading current contents and so
    can be used for a "latest window".
    
    Might be able to use deque instead?  This may be more efficient
    if the entire contents are read often (as is the case when depth gets
    deeper)?
    '''
    
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
    
    def pop(self, index=0):
        if index != 0: raise IndexError('FIFO is only a FIFO')
        if self.__size < 1: raise IndexError('FIFO empty')
        popped = self.__buffer[(self.__next - self.__size) % len(self.__buffer)]
        self.__size -= 1
        return popped
    
    def __len__(self):
        return len(self.__buffer)

    def __iter__(self):
        capacity = len(self.__buffer)
        index = (self.__next - self.__size) % capacity
        for _ in range(self.__size):
            yield self.__buffer[index]
            index = (index + 1) % capacity


class BaseGeneratorDecorator(object):
    '''
    Base class for wrapping generators.
    '''
    
    def __init__(self, generator):
        super(BaseGeneratorDecorator, self).__init__()
        self.__generator = generator
    
    def __next__(self):
        try:
            self._before()
            return self._value(next(self.__generator))
        finally:
            self._after()
            
    # for 2.6
    def next(self):
        return self.__next__()
    
    def send(self, value):
        return self.__generator.send(value)
    
    def throw(self, value):
        return self.__generator.throw(value)
                
    def __iter__(self):
        return self
                
    def close(self):
        self.__generator.close()
        
    def _before(self):
        pass
    
    def _after(self):
        pass
    
    def _value(self, value):
        return value
    
    def getattr(self, name):
        return getattr(self.__generator, name)
    
    
class FastFifo():
    '''
    A FIFO that extends to accommodate data as required.
    
    Use deque instead.
    '''
    
    def __init__(self):
        self.__front = []
        self.__back = []
    
    def append(self, value):
        self.__front.append(value)
        
    def pop(self, index=0):
        if index != 0: raise IndexError('FIFO is only a FIFO')
        if not self.__back:
            self.__front.reverse()
            self.__back = self.__front
            self.__front = []
        return self.__back.pop(-1)
    
    def __len__(self):
        return len(self.__front) + len(self.__back)
    

def open_stop(spec):
    '''
    In Python 2.6 open [] appears to use maxint or similar, which is not
    available in Python 3.  This uses a minimum value for maxint I found
    somewhere; hopefully no-one ever wants finite repeats larger than this.
    '''
    return spec.stop == None or spec.stop > 2147483647


def lmap(function, values):
    '''
    A map that returns a list rather than an iterator.
    '''
    return list(map(function, values))


def compose(f, g):
    '''
    Functional composition.
    '''
    def fun(*args, **kargs):
        return f(g(*args, **kargs))
    return fun

