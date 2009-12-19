
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
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

from logging import getLogger

# this is an attempt to make 2.6 and 3 function equally with strings
try:
    str = unicode
    basestring = basestring
except:
    str = str
    basestring = str



def assert_type(name, value, type_, none_ok=False):
    '''
    If the value is not of the given type, raise a syntax error.
    '''
    if none_ok and value is None:
        return
    if isinstance(value, type_):
        return
    raise TypeError(format('{0} (value {1}) must be of type {2}.',
                           name, repr(value), type_.__name__))


class CircularFifo(object):
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
        '''
        Remove and return the next item.
        '''
        if index != 0:
            raise IndexError('FIFO is only a FIFO')
        if self.__size < 1:
            raise IndexError('FIFO empty')
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
        '''
        Clear the data (we just set the size to zero - this doesn't release
        any references).
        '''
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
    # pylint: disable-msg=W0141
    return list(map(function, values))


def compose(fun_a, fun_b):
    '''
    Functional composition (assumes fun_a takes a single argument).
    '''
    def fun(*args, **kargs):
        '''
        This assumes fun_a takes a single argument.
        '''
        return fun_a(fun_b(*args, **kargs))
    return fun


def compose_tuple(fun_a, fun_b):
    '''
    Functional composition (assumes fun_b returns a sequence which is supplied
    to fun_a via *args).
    '''
    def fun(*args, **kargs):
        '''
        Supply result from fun_b as *arg.
        '''
        # pylint: disable-msg=W0142
        return fun_a(*fun_b(*args, **kargs))
    return fun


def empty():
    '''
    An empty generator.
    '''
    if False:
        yield None
    
    
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
        '''
        Construct a tag from the class name and an optional set of extra values.
        '''
        # pylint: disable-msg=W0141
        self.describe = format('{0}({1})', self.__class__.__name__, 
                               ','.join(map(str, args)))
        return self
    

def safe_in(value, container, default=False):
    '''
    Test for membership without an error for unhashable items.
    '''
    try:
        return value in container
    except TypeError:
        log = getLogger('lepl.support.safe_in')
        log.warn(format('Cannot test for {0!r} in collection', value))
        return default
    
    
def safe_add(container, value):
    '''
    Ass items to a container, if they are hashable.
    '''
    try:
        container.add(value)
    except TypeError:
        log = getLogger('lepl.support.safe_add')
        log.warn(format('Cannot add {0!r} to collection', value))
        pass


def fold(fun, start, sequence):
    '''
    Fold over a sequence.
    '''
    for value in sequence:
        start = fun(start, value)
    return start


def sample(prefix, rest, size=40):
    '''
    Provide a small sample of a string.
    '''
    text = prefix + rest
    if len(text) > size:
        text = prefix + rest[0:size-len(prefix)-3] + '...'
    return text


__SINGLETONS = {}
'''
Map from factory (constructor/class) to singleton.
'''

def singleton(factory):
    '''
    Manage singletons for various types.
    '''
    if factory not in __SINGLETONS:
        __SINGLETONS[factory] = factory()
    return __SINGLETONS[factory]


def format(template, *args, **kargs):
    '''
    Guarantee that template is always unicode, as embedding unicode in ascii
    can cause errors.
    '''
    return str(template).format(*args, **kargs)
