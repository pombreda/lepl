

from io import StringIO

from lepl.core import Core, LimitedGeneratorStack
from lepl.trace import SelfDocumentingGenerator


def new_stack(stream):
    '''
    Generate a stack for managing generators in breadth-first searches.
    '''
    if isinstance(stream, Stream):
        size = stream.core.max_width
    else:
        size = 0
    return LimitedGeneratorStack(size)


def limited_depth(f):
    '''
    Generators should be decorated with this so that the depth of the search
    can be limited, freeing resources that are no longer needed.
    '''
    def call(self, stream):
        core = stream.core if isinstance(stream, Stream) else None
        try:
            generator = SelfDocumentingGenerator(f(self, stream), self, stream)
            if core and core.down(): generator.close()
            return generator
        finally:
            if core: core.up()
    return call


def no_depth(f):
    '''
    When a match generator is known to only return one value (or none)
    there is no need to bother with the fifo in the core; instead we simply
    read and then discard the generator.
    '''
    def call(self, stream):
        generator = SelfDocumentingGenerator(f(self, stream), self, stream)
        value = None
        ok = False
        try:
            value = next(generator)
            ok = True
        finally:
            generator.close()
        if ok:
            yield value
    return call

        
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
    def from_path(path):
        '''
        Open the file with line buffering.
        '''
        return Stream(Chunk(open(path, 'rt', buffering=1)))
    
    @staticmethod
    def from_string(text):
        '''
        Wrap a string.
        '''
        return Stream(Chunk(StringIO(text)))
    
    @staticmethod
    def from_list(data):
        '''
        We can parse any list (not just lists of characters as strings).
        '''
        return Stream(Chunk(ListIO(data)))
    
    @staticmethod
    def from_file(file):
        '''
        Wrap a file.
        '''
        return Stream(Chunk(file))
    
    def __init__(self, chunk, offset=0, core=None):
        self.__chunk = chunk
        self.__offset = offset
        self.core = chunk.core
        
    def __getitem__(self, spec):
        '''
        [n] returns a character (string of length 1)
        [n:] returns a new Stream instance
        [n:m] returns a string
        These are all relative to 
        '''
        if isinstance(spec, int):
            return self.__chunk.read(self.__offset, spec, spec+1)[0]
        elif isinstance(spec, slice) and spec.step == None:
            if spec.stop == None:
                return self.__chunk.stream(self.__offset, spec.start)
            elif spec.stop >= spec.start:
                return self.__chunk.read(self.__offset, spec.start, spec.stop)
        raise TypeError()
    
    def __bool__(self):
        return not self.__chunk.empty_at(self.__offset)
        
    def __repr__(self):
        return '%r[%d:]' % (self.__chunk, self.__offset)
    
    def __str__(self):
        return self.__chunk.describe(self.__offset)
        
        
class Chunk():
    '''
    A linked list (cons cell) of lines from the stream. 
    '''
    
    def __init__(self, stream, core=None):
        super().__init__()
        try:
            self.__text = next(stream)
            self.__empty = False
        except StopIteration:
            self.__empty = True
        self.__next = None
        self.__stream = stream
        self.core = core if core else Core()
        
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
        if not self.__next:
            self.__next = Chunk(self.__stream, self.core)
        return self.__next
    
    def stream(self, offset, start):
        '''
        Return a new pointer to the chunk containing the data indicated.
        '''
        start = start + offset
        if start == 0 or (not self.__empty and start <= len(self.__text)):
            return Stream(self, start)
        elif self.__empty:
            raise IndexException()
        else:
            return self.next().stream(start-len(self.__text), 0)
        
    def empty_at(self, offset):
        '''
        Used by streams to test whether more data available at their current
        offset.
        '''
        if self.__empty:
            return True
        elif offset < len(self.__text):
            return False
        else:
            return self.next().empty_at(offset - len(self.__text))

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
        
    def __repr__(self):
        return 'Chunk(%r...)' % ('' if self.__empty else self.__text)
    

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
