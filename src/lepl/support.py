
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

from traceback import print_exc

from logging import getLogger


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
            
    def clear(self):
        self.__size = 0


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


def compose_tuple(f, g):
    '''
    Functional composition.
    '''
    def fun(*args, **kargs):
        return f(*g(*args, **kargs))
    return fun


class LogMixin(object):
    '''
    Add standard Python logging to a class.
    '''
    
    def __init__(self, *args, **kargs):
        super(LogMixin, self).__init__(*args, **kargs)
        self._log = getLogger(self.__module__ + '.' + self.__class__.__name__)
        self._debug = self._log.debug
        self._info = self._log.info
        self._warn = self._log.warn
        self._error = self._log.error
        self.describe = self.__class__.__name__
        
    def tag(self, *args):
        self.describe = '{0}({1})'.format(self.__class__.__name__, 
                                          ','.join(map(str, args)))
        return self
    

