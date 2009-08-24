
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
A stream that adds tokens at the start and end of lines.
'''

from io import StringIO

from lepl.offside.regexp import Token
from lepl.offside.support import LineAwareException
from lepl.stream import DefaultStreamFactory, LineSource, sample


class LineAwareStreamFactory(DefaultStreamFactory):
    
    def __init__(self, alphabet):
        self.alphabet = alphabet

    def from_path(self, path):
        return self(LineAwareSource(self.alphabet, 
                                    open(path, 'rt', buffering=1),
                                    path))
    
    def from_string(self, text):
        return self(LineAwareSource(self.alphabet, StringIO(text), 
                                    sample('str: ', repr(text))))
    
    def from_lines(self, lines, source=None, join_=''.join):
        if source is None:
            source = sample('lines: ', repr(lines))
        return self(LineAwareSource(self.alphabet, lines, source, join_))
    
    def from_items(self, items, source=None, line_length=80):
        raise LineAwareException('Only line-based sources are supported')
    
    def from_file(self, file_):
        return self(LineAwareSource(self.alphabet, file_, 
                                    getattr(file_, 'name', '<file>')) )

    def null(self, stream):
        raise LineAwareException('Only line-based sources are supported')


def top_and_tail(alphabet, lines):
    
    def extend(line):
        return [alphabet.min] + list(line) + [alphabet.max]
    
    for line in lines:
        yield extend(line)
        
        
def join(lines):
    # pylint: disable-msg=W0141
    return ''.join([''.join(filter(lambda x: not isinstance(x, Token), line))
                    for line in lines])

        
# pylint: disable-msg=E1002
# pylint can't find ABCs
class LineAwareSource(LineSource):
    
    def __init__(self, alphabet, lines, description=None, join_=join):
        super(LineAwareSource, self).__init__(
                        top_and_tail(alphabet, lines),
                        repr(lines) if description is None else description,
                        join_)
    
    def location(self, offset, line, location_state):
        (character_count, line_count) = location_state
        return (line_count, offset - 1, character_count + offset - 1, 
                line, str(self))
        
    def text(self, offset, line):
        if line:
            return self.join(line[offset:])
        else:
            return self.join([])
       
