
from lepl.offside.support import LineAwareException
from lepl.stream import StreamFactory, LineSource, sample


def line_aware_stream_factory_factory(alphabet):

    class LineAwareStreamFactory(StreamFactory):
    
        def from_path(self, path):
            return self(LineAwareSource(alphabet, open(path, 'rt', buffering=1),
                                        path))
        
        def from_string(self, text):
            return self(LineAwareSource(alphabet, StringIO(text), 
                                        sample('str: ', repr(text))))
        
        def from_lines(self, lines, source=None, join=''.join):
            if source is None:
                source = sample('lines: ', repr(lines))
            return self(LineAwareSource(alphabet, lines, source, join))
        
        def from_items(self, items, source=None, line_length=80):
            raise LineAwareException('Only line-based sources are supported')
        
        def from_file(self, file_):
            return self(LineAwareSource(alphabet, file_, 
                                        getattr(file_, 'name', '<file>')) )
    
        def null(self, stream):
            raise LineAwareException('Only line-based sources are supported')


def top_and_tail(alphabet, lines):
    
    def extend(line):
        yield alphabet.min
        for char in line:
            yield char
        yield alphabet.max
    
    for line in lines:
        yield extend(line) 


class LineAwareSource(LineSource):
    
    def __init__(self, alphabet, lines, description=None, join=''.join):
        super(LineAwareSource, self).__init__(
                        top_and_tail(alphabet, lines),
                        repr(lines) if description is None else description,
                        join)
    
    def location(self, offset, line, location_state):
        (character_count, line_count) = location_state
        return (line_count, offset - 1, character_count + offset - 1, 
                line, str(self))
        
    def text(self, offset, line):
        if line:
            return line[offset:]
        else:
            return self.join([])
       
