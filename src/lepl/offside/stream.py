
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
       
