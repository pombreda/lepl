
'''
A stream interface to the parsed string, implemented as a linked list.
'''


from io import StringIO

from lepl.core import Core


class Stream():
    '''
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
        '''
        self.__chunk = chunk
        self.offset = offset
        self.lineno = chunk.lineno
        self.core = chunk.core
        self.lineno = chunk.lineno
        
    def __getitem__(self, spec):
        '''
        [n] returns a character (string of length 1)
        [n:] returns a new Stream instance
        [n:m] returns a string
        These are all relative to the internal offset.
        '''
        if isinstance(spec, int):
            return self.__chunk.read(self.offset, spec, spec+1)[0]
        elif isinstance(spec, slice) and spec.step == None:
            if spec.stop == None:
                return self.__chunk.stream(self.offset + spec.start)
            elif spec.stop >= spec.start:
                return self.__chunk.read(self.offset, spec.start, spec.stop)
        raise TypeError()
    
    def __bool__(self):
        return not self.__chunk.empty_at(self.offset)
    
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
        return self.__chunk.line(self.offset)
        
        
class Chunk():
    '''
    A linked list (cons cell) of lines from the stream. 
    '''
    
    def __init__(self, stream, distance=0, lineno=1, core=None, **options):
        super().__init__()
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
        
    def read(self, offset, start, stop):
        '''
        Read a string.
        '''
        if stop == 0: return ''
        if self.__empty: raise IndexError()
        start = start + offset
        stop = stop + offset
        size = len(self.__text)
        if stop <= size:
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
    
    def stream(self, offset):
        '''
        Return a new pointer to the chunk containing the data indicated.
        '''
        return Stream(*self.__to(offset))
        
    def empty_at(self, offset):
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
        size = self.core.description_length if length == None else length
        if self.empty_at(offset):
            return repr('')
        else:
            stop = min(offset + size, len(self.__text))
            content = self.__text[offset:stop]
            # the empty check avoids receiving '' from next chunk
            remaining = size - len(content)
            if remaining and not self.empty_at(stop):
                content = content + self.next().describe(0, remaining)
            if length == None: # original call
                # convert to string
                content = repr(content)
                # indicate if more data available
                if not self.empty_at(offset + size):
                    content = content + '...'
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
        return 'Chunk(%r...)' % ('' if self.__empty else self.__text)
    
    def line(self, offset=0):
        return self.__to(offset)[0].__text
    

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


class StreamMixin():
    '''
    Helper functions that forward to __call__.
    '''
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
    
    def match_string(self, **options):
        '''
        Create a parser for a string.  For options see lepl.core.Core.
        '''
        return lambda text: self(Stream.from_string(text, **options))

    def match_path(self, **options):
        '''
        Create a parser for a file from a given path.  For options see lepl.core.Core.
        '''
        return lambda path: self(Stream.from_path(path, **options))

    def match_list(self, **options):
        '''
        Create a parser for a list of values.  For options see lepl.core.Core.
        '''
        return lambda list_: self(Stream.from_list(list_, **options))

    def match_file(self, **options):
        '''
        Create a parser for a file.  For options see lepl.core.Core.
        '''
        return lambda file_: self(Stream.from_string(file_, **options))

    def parse_string(self, text, **options):
        '''
        Parse a string, returning only a single result.  
        For options see lepl.core.Core.
        '''
        try:
            return next(self(Stream.from_string(text, **options)))[0]
        except StopIteration:
            return None

    def parse_path(self, path, **options):
        '''
        Parse a file from a given path, returning only a single result.  
        For options see lepl.core.Core.
        '''
        return next(self(Stream.from_path(path, **options)))[0]

    def parse_list(self, list_, **options):
        '''
        Parse a list of values, returning only a single result.  
        For options see lepl.core.Core.
        '''
        return next(self(Stream.from_list(list_, **options)))[0]

    def parse_file(self, file_, **options):
        '''
        Parse a file, returning only a single result.  
        For options see lepl.core.Core.
        '''
        return next(self(Stream.from_string(file_, **options)))[0]
