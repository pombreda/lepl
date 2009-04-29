
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
A stream interface to the input, implemented using singly linked lists.
'''

from abc import ABCMeta, abstractmethod
from io import StringIO

from lepl.support import open_stop


# Python 2.6
#class SimpleStream(metaclass=ABCMeta):
SimpleStream = ABCMeta('SimpleStream', (object, ), {})
'''ABC used to identify streams.'''


class SimpleStreamInterface(SimpleStream):
    '''
    The minimal interface that matchers expect to be implemented.
    '''

    @abstractmethod
    def __getitem__(self, spec):
        '''
        [n] returns a character (string of length 1)
        [n:] returns a new SimpleStream instance that starts at the offset n
        [n:m] returns a sequence (ie string, list, etc)
        '''
        pass
    
    @abstractmethod
    def __bool__(self):
        '''
        Non-empty?
        '''
        pass
    
    def __nonzero__(self):
        '''
        Called only by 2.6 (when __bool__ not called).
        '''
        return self.__bool__() 
    
    @abstractmethod
    def __len__(self):
        '''
        Amount of remaining data.
        
        This may be expensive if the data are in a file, but is needed for
        left recursion handling.
        '''
        pass
    
    @abstractmethod
    def __repr__(self):
        pass
    
    @abstractmethod
    def __str__(self):
        pass
    
    @abstractmethod
    def __hash__(self):
        pass
    
    @abstractmethod
    def __eq__(self, other):
        pass
    
    
SimpleStream.register(str)
SimpleStream.register(list)


class LocationStream(SimpleStreamInterface):
    '''
    Additional methods available on "real" streams.
    '''
    
    @abstractmethod
    def location(self):
        '''
        A tuple containing line number, line offset, character offset,
        the line currently being processed, and a description of the source.
        
        The line number is -1 if this is past the end of the file.
        '''
        pass
   
    def text(self):
        '''
        The line of text in the underlying line indexed by this stream,
        starting at the offset.  Needed by ``Regexp`` for strings.
        '''
        raise Exception('This stream does not support Regexp.')
    


class SequenceByLine(LocationStream):
    '''
    A wrapper for sequence data that includes location information.  
    
    Each instance is a pointer into a linked list of lines. This allows files
    to be parsed without having all data in memory (unless left recursion
    forces this to get the total length remaining).  Care has been taken to 
    avoid circular pointer references and avoid needing all data to be in
    memory at once.

    The offset for a stream should always lie within the associated line.
    Also, streams are only every used in the context of a single source, so
    equality and hashing do not check for this. 
    
    The above only works for files; for string data already in memory the
    lines are still managed (to keep the code simple), but are implemented
    as slices of the persistent in-memory data (I assume - in practice we
    just use StringIO).
    '''
    
    def __init__(self, line, offset=0):
        '''
        Create a stream, given the appropriate line and offset.
        '''
        self.__line = line
        self.__offset = offset

    def __getitem__(self, spec):
        '''
        [n] returns a character (string of length 1)
        [n:] returns a new Stream instance
        [n:m] returns a string
        These are all relative to the internal offset.
        '''
        return self.__line.getitem(spec, self.__offset)
    
    def __bool__(self):
        '''
        Non-empty?
        '''
        return not self.__line.empty_at(self.__offset)
    
    def __len__(self):
        '''
        This may be expensive if the data are in a file, but is needed for
        left recursion handling.
        '''
        return self.__line.len(self.__offset)
    
    def __repr__(self):
        return '{0!r}[{1:d}:]'.format(self.__line, self.__offset)
    
    def __str__(self):
        return self.__line.describe(self.__offset)
    
    def __hash__(self):
        return self.__line.hash(self.__offset)
    
    def __eq__(self, other):
        return isinstance(other, SequenceByLine) and \
            self.__line == other.__line and \
            self.__offset == other.__offset

    def location(self):
        '''
        A tuple containing line number, line offset, character offset,
        the line currently being processed, and a description of the source.
        
        The line number is -1 if this is past the end of the file.
        '''
        return self.__line.location(self.__offset)
    
    def text(self):
        '''
        The line of text in the underlying line indexed by this stream,
        starting at the offset.
        '''
        return self.__line.read(self.__offset)
    
    @staticmethod
    def from_path(path):
        '''
        Open the file with line buffering.
        '''
        return SequenceByLine(Line(open(path, 'rt', buffering=1), source=path))
    
    @staticmethod
    def from_string(text):
        '''
        Wrap a string.
        '''
        return SequenceByLine(Line(StringIO(text), source='<string>'))
    
    @staticmethod
    def from_list(data):
        '''
        We can parse any list (not just lists of characters as strings).
        '''
        return SequenceByLine(Line(ListIO(data), source='<list>'))
    
    @staticmethod
    def from_file(file):
        '''
        Wrap a file.
        '''
        return SequenceByLine(Line(file, source=gettatr(file, 'name', '<file>'))) 
        
    @staticmethod
    def null(stream):
        '''
        Return the underlying data with no modification.
        '''
        return stream
    

class Line(object):
    '''
    A linked list (cons cell) of lines from the stream.
    
    `SequenceByLine()` is a pointer to a Line that includes an offset;
    the Lines form a singly linked list that contains the input data.
    '''
    
    def __init__(self, stream, distance=0, lineno=1, source=None, hash_=None):
        try:
            self.__text = next(stream)
            self.__empty = False
            self.__lineno = lineno
        except StopIteration:
            self.__empty = True
            self.__lineno = -1
        self.__next = None
        self.__stream = stream
        self.__distance = distance
        self.__source = source
        self.__hash = hash(stream) if hash_ is None else hash_
        self.__len = None
        
    def read(self, offset=0, start=0, stop=None):
        '''
        Read a string.
        
        Works something like self.__text[start:stop], but shifted to offset,
        and allowing stop to be None.  If stop is specified and overshoots the
        line appropriate for start then data are pulled in from the next
        line.
        '''
        if stop == 0: return ''
        if self.__empty:
            if start == 0 and stop is None:
                return ''
            else:
                raise IndexError()
        size = len(self.__text)
        start = start + offset
        if stop is None:
            stop = size
        else:
            stop = stop + offset
        if start >= size:
            return self.next().read(0, start-size, stop-size)
        elif stop <= size:
            return self.__text[start:stop]
        else:
            return self.__text[start:] + self.next().read(0, start-size, stop-size)
        
    def next(self):
        '''
        The next line from the stream.
        '''
        if self.__empty:
            raise IndexError()
        if not self.__next:
            self.__next = Line(self.__stream, lineno=self.__lineno + 1,
                                distance=self.__distance + len(self.__text),
                                hash_=self.__hash)
        return self.__next
    
    def __iter__(self):
        return self
    
    def stream(self, offset=0):
        '''
        Return a new pointer to the line containing the data indicated.
        '''
        return SequenceByLine(*self.__to(offset))
    
    def __to(self, offset):
        '''
        Return an (line, offset) pair for the given offset.
        '''
        if offset == 0:
            return (self, 0)
        elif self.__empty:
            raise IndexException('No line available')
        elif offset < len(self.__text):
            return (self, offset)
        else: 
            return self.next().__to(offset - len(self.__text))

    def getitem(self, spec, offset=0):    
        if isinstance(spec, int):
            return self.read(offset, spec, spec+1)[0]
        elif isinstance(spec, slice) and spec.step is None:
            if open_stop(spec):
                return self.stream(offset + spec.start)
            elif spec.stop >= spec.start:
                return self.read(offset, spec.start, spec.stop)
        raise TypeError()

    def empty_at(self, offset=0):
        '''
        Used by streams to test whether more data available at their current
        offset.
        '''
        return self.__empty or offset >= len(self.__text)

    def describe(self, offset, length=None):
        '''
        This has to work even when the underlying stream is not a string
        but a list of some kind (so does everything else, but here the
        addition of "..." causes problems).
        '''
        size = 6 if length is None else length
        if self.empty_at(offset):
            return repr('')
        else:
            stop = min(offset + size, len(self.__text))
            content = self.__text[offset:stop]
            # the empty check avoids receiving '' from next line
            remaining = size - len(content)
            if remaining and not self.empty_at(stop):
                content = content + self.next().describe(0, remaining)
            if length is None: # original call
                # convert to string
                content = repr(content)
                # indicate if more data available
                if not self.empty_at(offset + size):
                    content = content[0:-1] + '...' + content[-1]
            return content
        
    def location(self, offset=0):
        '''
        A tuple containing line number, line offset, character offset,
        the line currently being processed, and a description of the source.
        
        The line number is -1 if this is past the end of the file.
        '''
        depth = self.__distance + offset
        return (self.__lineno, offset, depth, self.read(0), self.__source)
        
    def __repr__(self):
        return 'Line(%r)' % ('' if self.__empty else self.__text)
    
    def len(self, offset=0):
        '''
        Remaining length.
        '''
        if self.__len is None:
            if self.__empty:
                self.__len = 0
            else:
                self.__len = len(self.__text) + self.next().len() - offset
        return self.__len
    
    def hash(self, offset=0):
        return self.__hash ^ offset ^ self.__lineno
    

class ListIO():
    '''
    Minimal wrapper for lists - returns entire list as single line.
    '''
    
    def __init__(self, data):
        self.__data = data
        
    def close(self):
        self.__data = None

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.__data != None:
            (data, self.__data) = (self.__data, None)
            return data
        else:
            raise StopIteration()

    # for 2.6
    def next(self):
        return self.__next__()        


class SimpleGeneratorStream(SimpleStream):
    '''
    Wrap a generator in the SimpleStream interface (is there nothing in the 
    standard lib for this?).
    
    We try to unroll gradually, but if __len__ is called then we do a full
    unrolling and store the list.
    '''
    
    def __init__(self, generator, join=list, unrolled=None):
        self.__generator = generator
        self.__join = join
        self.__unrolled = unrolled
        self.__cached_next = None
        if self.__unrolled is None:
            try:
                (self.__value, self.__empty) = (next(generator), False)
            except StopIteration:
                (self.__value, self.__empty) = (None, True)
        else:
            self.__empty = len(self.__unrolled) == 0
            if self.__empty:
                self.__value = None
            else:
                self.__value = self.__unrolled[0]
        
    def __getitem__(self, spec):
        '''
        [n] returns a character (string of length 1)
        [n:] returns a new SimpleStream instance that starts at the offset n
        [n:m] returns a sequence (ie string, list, etc)
        '''
#        if self.__unrolled is not None:
#            return self.__unrolled.__getitem__(spec)
        if isinstance(spec, int):
            if spec == 0 and not self.__empty:
                return self.__value
            elif spec > 0:
                return self.__next()[spec-1]
        elif isinstance(spec, slice) and isinstance(spec.start, int):
            if spec.step is None and spec.stop is None:
                if spec.start == 0:
                    return self
                elif spec.start == 1:
                    return self.__next()
                elif spec.start > 1:
                    return self.__next()[spec.start-1:]
            elif spec.step is None and isinstance(spec.stop, int):
                if spec.start == 0:
                    if spec.stop == 0:
                        return self.__join([])
                    elif spec.stop > spec.start:
                        return self.__accumulate([], spec.stop)
                elif spec.start > 0:
                    return self.__next()[spec.start-1:spec.stop-1]
        raise IndexError()
    
    def __next(self):
        '''
        Return the next stream (ie the wrapped for the next item in the
        generator).
        '''
        if self.__empty:
            raise IndexError()
        if not self.__cached_next:
            if self.__unrolled:
                unrolled = self.__unrolled[1:]
            else:
                unrolled = None
            self.__cached_next = SimpleGeneratorStream(
                                    self.__generator, self.__join, unrolled)
        return self.__cached_next
    
    def __accumulate(self, accumulator, stop):
        '''
        Accumulate values, then join and return.
        '''
        if stop == 0:
            return self.__join(accumulator)
        elif self.__empty:
            raise IndexError()
        else:
            accumulator.append(self.__value)
            return self.__next().__accumulate(accumulator, stop-1)
    
    def __bool__(self):
        '''
        Non-empty?
        '''
        if self.__unrolled is not None:
            return bool(self.__unrolled)
        else:
            return not self.__empty
    
    def __nonzero__(self):
        '''
        Called only by 2.6 (when __bool__ not called).
        '''
        return self.__bool__() 
    
    def __len__(self):
        '''
        Amount of remaining data.
        
        We need to be careful to avoid calling the generator more than once
        for any value.  So if we have already generated the next stream we
        must delegate to that; alternatively we can unroll and then construct
        the next stream (if needed) with the unrolled data.
        '''
        if self.__cached_next is not None:
            return 1 + len(self.__cached_next)
        else:
            if self.__unrolled is None:
                if self.__empty:
                    unrolled = []
                else:
                    unrolled = [self.__value]
                    unrolled.extend(list(self.__generator))
                self.__unrolled = self.__join(unrolled)
                self.__cached_next = None
            return len(self.__unrolled)
    
    def __repr__(self):
        if self.__unrolled is None:
            return '<SimpleGeneratorStream>'
        else:
            return '<SimpleGeneratorStream {0}>'.format(self.__unrolled)
    
    def __str__(self):
        return 'Wrapped generator: ' + \
            "compact" if self.__unrolled is None else str(self.__unrolled)
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        return self == other
