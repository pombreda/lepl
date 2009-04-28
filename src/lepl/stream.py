
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

from io import StringIO

from lepl.support import open_stop


class Stream(object):
    '''
    A wrapper for the input data.
    
    This associates the input data with source information and allows files
    to be parsed without having all data in memory (unless left recursion
    forces this to get the total length remaining).

    We support the GC by making Stream instances pointers into the data,
    which is itself managed in a linked list of chunks (one per line).  Back 
    tracking is then handled by keeping a copy of an "old" Stream instance; 
    when no old instances are in use the linked list can be reclaimed.
    
    The offset for a stream should always lie within the associated chunk.
    Also, streams are only every used in the context of a single source, so
    equality and hashing do not check for this. 
    
    The above only works for files; for string data already in memory the
    chunks are still managed (to keep the code simple), but are implemented
    as slices of the persistent in-memory data (I assume - in practice we
    just use StringIO).
    
    Note that Stream() provides only a very limited impression of the
    string/list interface.
    '''
    
    @staticmethod
    def from_path(path):
        '''
        Open the file with line buffering.
        '''
        return Stream(Chunk(open(path, 'rt', buffering=1), source=path))
    
    @staticmethod
    def from_string(text):
        '''
        Wrap a string.
        '''
        return Stream(Chunk(StringIO(text), source='<string>'))
    
    @staticmethod
    def from_list(data):
        '''
        We can parse any list (not just lists of characters as strings).
        '''
        return Stream(Chunk(ListIO(data), source='<list>'))
    
    @staticmethod
    def from_file(file):
        '''
        Wrap a file.
        '''
        return Stream(Chunk(file, source=gettatr(file, 'name', '<file>'))) 
        
    @staticmethod
    def null(stream):
        '''
        Return the underlying data with no modification.
        '''
        return stream
    
    def __init__(self, chunk, offset=0):
        '''
        Create a stream, given the appropriate chunk and offset.
        '''
        self.__chunk = chunk
        self.__offset = offset

    def source(self):
        '''
        A description of where the data came from.
        '''
        return self.__chunk.source
        
    def location(self):
        '''
        A pair containing line number and line offset.
        The line number is ``None`` if this is past the end of the file.
        '''
        return self.__chunk.location(self.__offset)
    
    def depth(self):
        '''
        The file offset.
        '''
        return self.__chunk.depth(self.__offset)
        
    def line(self):
        '''
        The line of text in the underlying chunk indexed by this stream.
        '''
        return self.__chunk.read(0)
    
    def text(self):
        '''
        The line of text in the underlying chunk indexed by this stream,
        starting at the offset.
        '''
        return self.__chunk.read(self.__offset)
    
    def __getitem__(self, spec):
        '''
        [n] returns a character (string of length 1)
        [n:] returns a new Stream instance
        [n:m] returns a string
        These are all relative to the internal offset.
        '''
        return self.__chunk.getitem(spec, self.__offset)
    
    def __bool__(self):
        '''
        Non-empty?
        '''
        return not self.__chunk.empty_at(self.__offset)
    
    def __nonzero__(self):
        '''
        Called only by 2.6 (when __bool__ not called).
        '''
        return self.__bool__() 
    
    def __len__(self):
        '''
        This may be expensive if the data are in a file, but is needed for
        left recursion handling.
        '''
        return self.__chunk.len(self.__offset)
    
    def __repr__(self):
        return '{0!r}[{1:d}:]'.format(self.__chunk, self.__offset)
    
    def __str__(self):
        return self.__chunk.describe(self.__offset)
    
    def __hash__(self):
        '''
        Combine underlying stream and depth.
        '''
        return self.__chunk.hash ^ self.depth()
    
    def __eq__(self, other):
        '''
        Streams are only ever used in contexts where they share the same source.
        '''
        return isinstance(other, Stream) and \
            self.depth() == other.depth()


class Chunk(object):
    '''
    A linked list (cons cell) of lines from the stream.
    
    `Stream()` is a pointer to a Chunk that includes an offset;
    the Chunks form a singly linked list that contains the input data.
    '''
    
    def __init__(self, stream, distance=0, lineno=1, source=None, hash_=None):
        try:
            self.__text = next(stream)
            self.__empty = False
        except StopIteration:
            self.__empty = True
        self.__next = None
        self.__stream = stream
        self.__distance = distance
        self.__lineno = lineno
        self.source = source
        self.hash = hash(stream) if hash_ is None else hash_
        self.__len = None
        
    def read(self, offset=0, start=0, stop=None):
        '''
        Read a string.
        
        Works something like self.__text[start:stop], but shifted to offset,
        and allowing stop to be None.  If stop is specified and overshoots the
        chunk appropriate for start then data are pulled in from the next
        chunk.
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
            self.__next = Chunk(self.__stream, lineno=self.__lineno + 1,
                                distance=self.__distance + len(self.__text),
                                hash_=self.hash)
        return self.__next
    
    def __iter__(self):
        return self
    
    def stream(self, offset=0):
        '''
        Return a new pointer to the chunk containing the data indicated.
        '''
        return Stream(*self.__to(offset))
    
    def __to(self, offset):
        '''
        Return an (chunk, offset) pair for the given offset.
        '''
        if offset == 0:
            return (self, 0)
        elif self.__empty:
            raise IndexException('No chunk available')
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
            # the empty check avoids receiving '' from next chunk
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
        A pair containing line number and offset.
        The line number is -1 if this is past the end of the file.
        '''
        if self.__empty:
            return (-1, offset)
        else:
            return (self.__lineno, offset)
        
    def depth(self, offset=0):
        '''
        The file offset.
        '''
        return self.__distance + offset
    
    def __repr__(self):
        return 'Chunk(%r)' % ('' if self.__empty else self.__text)
    
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
    

class ListIO(object):
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

