
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

try:
    from io import StringIO
except ImportError:
    def StringIO(text):
        return text

from lepl.core import Core
from lepl.support import open_stop


class Stream():
    '''
    A wrapper for the input data.
    
    This serves two purposes.  First, it wraps the central, persistent store
    for things like debug info and backtrace stack management while doing a 
    parse.  Second, it provides moderately space-efficient access to the string 
    data, allowing both back-tracking and background clean-up of unused data by 
    the GC.
    
    We support the GC by making Stream instances pointers into the data,
    which is itself managed in a linked list of chunks (one per line).  Back 
    tracking is then handled by keeping a copy of an "old" Stream instance; 
    when no old instances are in use the linked list can be reclaimed.
    
    The above only works for files; for string data already in memory the
    chunks are still managed (to keep the code simple), but are implemented
    as slices of the persistent in-memory data (I assume - in practice we
    just use StringIO).
    
    Note that Stream() provides only a very limited impression of the
    string interface via [n] and [n:m].
    '''
    
    @staticmethod
    def from_path(path, **options):
        '''
        Open the file with line buffering.
        '''
        return Stream(Chunk(open(path, 'rt', buffering=1), source=path, 
                            **options))
    
    @staticmethod
    def from_string(text, **options):
        '''
        Wrap a string.
        '''
        return Stream(Chunk(StringIO(text), source='<string>', **options))
    
    @staticmethod
    def from_list(data, **options):
        '''
        We can parse any list (not just lists of characters as strings).
        '''
        return Stream(Chunk(ListIO(data), source='<list>', **options))
    
    @staticmethod
    def from_file(file, **options):
        '''
        Wrap a file.
        '''
        return Stream(Chunk(file, source=gettatr(file, 'name', '<file>'), 
                            **options)) 
    
    def __init__(self, chunk, offset=0, core=None):
        '''
        Create a stream, given the appropriate chunk and offset.
        '''
        self.__chunk = chunk
        self.offset = offset
        self.core = chunk.core
        
    def __getitem__(self, spec):
        '''
        [n] returns a character (string of length 1)
        [n:] returns a new Stream instance
        [n:m] returns a string
        These are all relative to the internal offset.
        '''
        return self.__chunk.getitem(spec, self.offset)
    
    def __bool__(self):
        '''
        Non-empty?
        '''
        return not self.__chunk.empty_at(self.offset)
    
    def __len__(self):
        '''
        Called only by 2.6 (when __bool__ not called).
        '''
        return 1 if self.__bool__() else 0
    
    def location(self):
        '''
        A pair containing line number and line offset.
        The line number is ``None`` if this is past the end of the file.
        '''
        return self.__chunk.location(self.offset)
    
    def depth(self):
        '''
        The file offset.
        '''
        return self.__chunk.depth(self.offset)
        
    def __repr__(self):
        return '%r[%d:]' % (self.__chunk, self.offset)
    
    def __str__(self):
        return self.__chunk.describe(self.offset)
    
    def line(self):
        return self.__chunk.line()
    
    def text(self):
        return self.__chunk.text(self.offset)
    
        
class Chunk(object):
    '''
    A linked list (cons cell) of lines from the stream.
    
    `lepl.stream.Stream()` is a pointer to a Chunk that includes an offset;
    the Chunks form a singly linked list that contains the input data.
    '''
    
    def __init__(self, stream, distance=0, lineno=1, core=None, **options):
        try:
            self.__text = next(stream)
            self.__empty = False
        except StopIteration:
            self.__empty = True
        self.__next = None
        self.__stream = stream
        self.distance = distance
        self.lineno = lineno
        self.core = core if core else Core(**options)
        
    def read(self, offset=0, start=0, stop=None):
        '''
        Read a string.
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
            raise StopIteration()
        if not self.__next:
            self.__next = Chunk(self.__stream, core=self.core, 
                                lineno=self.lineno + 1,
                                distance=self.distance + len(self.__text))
        return self.__next
    
    def __iter__(self):
        return self
    
    def stream(self, offset=0):
        '''
        Return a new pointer to the chunk containing the data indicated.
        '''
        return Stream(*self.__to(offset))
    
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
        try:
            (chunk, offset) = self.__to(offset)
            return chunk.__empty
        except:
            return True

    def __to(self, offset):
        if offset == 0:
            return (self, 0)
        elif self.__empty:
            raise IndexException('No chunk available')
        elif offset < len(self.__text):
            return (self, offset)
        else: 
            return self.next().__to(offset - len(self.__text))

    def describe(self, offset, length=None):
        '''
        Return up to core.description_length characters.
        
        This has to work even when the underlying stream is not a string
        but a list of some kind (so does everything else, but here the
        addition of "..." causes problems).
        '''
        size = self.core.description_length if length is None else length
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
        The line number is ``None`` if this is past the end of the file.
        '''
        if self.__empty:
            return (None, offset)
        elif offset > len(self.__text):
            return next().location(offset - len(self.__text))
        else:
            return (self.lineno, offset)
        
    def depth(self, offset=0):
        '''
        The file offset.
        '''
        return self.distance + offset
    
    def __repr__(self):
        return 'Chunk(%r)' % ('' if self.__empty else self.__text)
    
    def line(self, offset=0):
        return self.__to(offset)[0].__text
    
    def text(self, offset=0):
        return self.read(offset)
    

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


class StreamMixin(object):
    '''
    Helper functions that forward to __call__.
    '''
    
    def __init__(self, *args, **kargs):
        super(StreamMixin, self).__init__(*args, **kargs)
    
    def match_string(self, **options):
        '''
        Create a parser for a string.  For options see `lepl.core.Core`.
        '''
        return lambda text: self(Stream.from_string(text, **options))

    def match_path(self, **options):
        '''
        Create a parser for a file from a given path.  For options see 
        `lepl.core.Core`.
        '''
        return lambda path: self(Stream.from_path(path, **options))

    def match_list(self, **options):
        '''
        Create a parser for a list of values.  For options see `lepl.core.Core`.
        '''
        return lambda list_: self(Stream.from_list(list_, **options))

    def match_file(self, **options):
        '''
        Create a parser for a file.  For options see `lepl.core.Core`.
        '''
        return lambda file_: self(Stream.from_string(file_, **options))

    def parse_string(self, text, **options):
        '''
        Parse a string, returning only a single result.  
        For options see `lepl.core.Core`.
        '''
        try:
            return next(self(Stream.from_string(text, **options)))[0]
        except StopIteration:
            return None

    def parse_path(self, path, **options):
        '''
        Parse a file from a given path, returning only a single result.  
        For options see `lepl.core.Core`.
        '''
        return next(self(Stream.from_path(path, **options)))[0]

    def parse_list(self, list_, **options):
        '''
        Parse a list of values, returning only a single result.  
        For options see `lepl.core.Core`.
        '''
        return next(self(Stream.from_list(list_, **options)))[0]

    def parse_file(self, file_, **options):
        '''
        Parse a file, returning only a single result.  
        For options see `lepl.core.Core`.
        '''
        return next(self(Stream.from_string(file_, **options)))[0]
