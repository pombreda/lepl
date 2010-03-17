
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
The token streams.
'''

from logging import getLogger

from lepl.stream.filters import BaseDelegateSource
from lepl.lexer.support import RuntimeLexerError
from lepl.stream.stream import LocationStream, DEFAULT_STREAM_FACTORY
from lepl.support.lib import format, str


def lexed_simple_stream(tokens, discard, stream):
    '''
    Given a simple stream, create a simple stream of (terminals, match) pairs.
    '''
    log = getLogger('lepl.lexer.stream.lexed_simple_stream')
    def generator(stream=stream):
        '''
        This creates the sequence of tokens returned by the stream.
        '''
        try:
            while stream:
                try:
                    (terminals, match, stream_after) = tokens.match(stream)
                    if stream_after == stream:
                        raise RuntimeLexerError('Tokens matched an empty '
                            'string.\nChange your token definitions so that '
                            'they cannot be empty.')
                    else:
                        stream = stream_after
                    log.debug(format('Token: {0!r} {1!r} {2!r}', 
                                     terminals, match, stream))
                    yield (terminals, match)
                except TypeError:
                    (terminals, _size, stream) = discard.size_match(stream)
                    log.debug(format('Space: {0!r} {1!r}', terminals, discard))
        except TypeError:
            raise RuntimeLexerError(format('No lexer for \'{0}\'.', stream))
        except AttributeError:
            raise RuntimeLexerError(format('No discard for \'{0}\'.', stream))
    return DEFAULT_STREAM_FACTORY.from_items(generator())


# pylint: disable-msg=E1002
# (pylint bug?  this chains back to a new style abc)
class TokenSource(BaseDelegateSource):
    '''
    The source of tokens sent to Token matchers.
    
    Wrap a sequence of (terminals, size, stream_before) tuples.
    '''
    
    def __init__(self, tokens, stream):
        '''
        tokens is an iterator over the (terminals, size, stream_before) tuples.
        '''
        assert isinstance(stream, LocationStream)
        # join is unused(?) but passed on to ContentStream
        super(TokenSource, self).__init__(str(stream.source),
                                          stream.source.join, stream.source)
        self.__tokens = iter(tokens)
        self.__token_count = 0
    
    def __next__(self):
        '''
        Provide (terminals, text) values (used by matchers) along with
        the original stream as location_state.
        
        Note that this is infinite - it is the StreamView that detects when
        the Line is empty and terminates any processing by the user.
        '''
        try:
            (terminals, size, stream) = next(self.__tokens)
            self.__token_count += 1
            # there's an extra list here because this is a "line" containing
            # a single token
            return ([(terminals, stream[0:size])], stream)
        except StopIteration:
            self.total_length = self.__token_count
            return (None, None)
        
    def hash_line(self, line):
        '''
        Use hash of base + location.
        '''
        if line is None:
            return 0
        else:
            return hash(line.location_state) ^ hash(self)
        
    def eq_line(self, line, other):
        '''
        A line.line looks like [(['Tk0'], '1')], we extract the text.
        '''
        return line.location_state == other.location_state \
            and self == other.source
            
    def text(self, _offset, line):
        '''
        For tokens, this is used only for str() / debug.
        '''
        if line is None:
            return ''
        else:
            return line[0][1]

def lexed_location_stream(tokens, discard, stream, source=None):
    '''
    Given a location stream, create a location stream of regexp matches.
    '''
    log = getLogger('lepl.lexer.stream.lexed_location_stream')
    if source is None:
        source = TokenSource
    def generator(stream_before):
        '''
        This creates the sequence of tokens returned by the stream.
        '''
        try:
            while stream_before:
                try:
                    (terminals, size, stream_after) = \
                            tokens.size_match(stream_before)
                    if stream_after == stream_before:
                        raise RuntimeLexerError('Tokens matched an empty '
                            'string.\nChange your token definitions so that '
                            'they cannot be empty.')
                    log.debug(format('Token: {0!r} {1!r} {2!r}', 
                                     terminals, size, stream_before))
                    # stream_before here to give correct location
                    yield (terminals, size, stream_before)
                    stream_before = stream_after
                except TypeError:
                    (terminals, size, stream_before) = \
                            discard.size_match(stream_before)
                    log.debug(format('Space: {0!r} {1!r}', terminals, size))
        except TypeError:
            raise RuntimeLexerError(
                format('No lexer for \'{0}\' at line {1} character {2} of {3}.',
                       stream_before.text, stream_before.line_number,
                       stream_before.line_offset, stream_before.source))
    token_stream = generator(stream)
    return DEFAULT_STREAM_FACTORY(source(token_stream, stream))


class ContentSource(BaseDelegateSource):
    '''
    The source of text sent to embedded content in a Token matcher.
    '''
    
    def __init__(self, text, stream):
        '''
        There's just a single line from the token contents.
        '''
        super(ContentSource, self).__init__(str(stream.source),
                                            stream.source.join,
                                            base=text)
        self.__line = text
        self.__stream = stream
        self.__used = False
        self.total_length = len(text)
    
    def __next__(self):
        '''
        Return a single line.
        '''
        try:
            return (None if self.__used else self.__line, self.__stream)
        finally:
            self.__used = True

    def text(self, offset, line):
        '''
        Provide the remaining part of the line.
        '''
        if line:
            return line[offset:]
        else:
            return self.join([])

    def hash_line(self, line):
        return hash(line.line) ^ hash(line.location_state)

    def eq_line(self, line, other):
        return line.line == other.line \
            and self == other.source
    