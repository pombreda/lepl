
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

from lepl.stream import LocationStream, DEFAULT_STREAM_FACTORY, BaseSource


def lexed_simple_stream(tokens, discard, error, stream):
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
                    (terminals, match, stream) = tokens.match(stream)
                    log.debug('Token: {0!r} {1!r}'.format(terminals, match))
                    yield (terminals, match)
                except TypeError:
                    (terminals, _size, stream) = discard.size_match(stream)
                    log.debug('Space: {0!r} {1!r}'.format(terminals, discard))
        except TypeError:
            #log.debug(format_exc())
            raise error(stream)
    return DEFAULT_STREAM_FACTORY.from_items(generator())


def lexed_location_stream(tokens, discard, error, stream):
    '''
    Given a location stream, create a location stream of regexp matches.
    '''
    log = getLogger('lepl.lexer.stream.lexed_location_stream')
    def generator(stream_before):
        '''
        This creates the sequence of tokens returned by the stream.
        '''
        try:
            while stream_before:
                try:
                    (terminals, size, stream_after) = \
                            tokens.size_match(stream_before)
                    # stream_before here to give correct location
                    log.debug('Token: {0!r} {1!r}'.format(terminals, size))
                    yield (terminals, size, stream_before)
                    stream_before = stream_after
                except TypeError:
                    (terminals, size, stream_before) = \
                            discard.size_match(stream_before)
                    log.debug('Space: {0!r} {1!r}'.format(terminals, size))
        except TypeError:
            raise error(stream_before)
    (_line, _offset, _character, _line, description) = stream.location()
    return DEFAULT_STREAM_FACTORY(TokenSource(generator(stream),
                                              description=description,
                                              join=stream.join))


# pylint: disable-msg=E1002
# (pylint bug?  this chains back to a new style abc)
class TokenSource(BaseSource):
    '''
    Wrap a sequence of (terminals, size, stream_before) tuples.
    '''
    
    def __init__(self, tokens, description=None, join=''.join):
        '''
        tokens is an iterator over the (terminals, size, stream_before) tuples.
        '''
        super(TokenSource, self).__init__(
                        repr(tokens) if description is None else description,
                        join)
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
    
    def location(self, offset, line, location_state):
        '''
        A tuple containing line number, line offset, character offset,
        the line currently being processed, and a description of the source.
        
        location_state is the original stream.
        '''
        if location_state:
            shifted = location_state[offset:]
            return shifted.location()
        else:
            return (-1, -1, -1, None, None)
        
    def text(self, offset, line):
        '''
        The current line.
        '''
        if line:
            return line[offset:]
        else:
            return self.join([])



# TODO

#def lexed_location_stream(tokens, discard, error, stream):
#    '''
#    Given a location stream, create a location stream of regexp matches.
#    '''
#    log = getLogger('lepl.lexer.stream.lexed_location_stream')
#    def generator(stream_before):
#        '''
#        This creates the sequence of tokens returned by the stream.
#        '''
#        try:
#            while stream_before:
#                try:
#                    (terminals, size, stream_after) = \
#                            tokens.size_match(stream_before)
#                    # stream_before here to give correct location
#                    log.debug('Token: {0!r} {1!r}'.format(terminals, size))
#                    yield (terminals, size, stream_before)
#                    stream_before = stream_after
#                except TypeError:
#                    (terminals, size, stream_before) = \
#                            discard.size_match(stream_before)
#                    log.debug('Space: {0!r} {1!r}'.format(terminals, size))
#        except TypeError:
#            #log.debug(format_exc())
#            raise error(stream_before)
#    return LocationGeneratorStream(generator(stream))
#
#
#class LocationGeneratorStream(LocationStream):
#    '''
#    Adapt a SimpleGeneratorStream, which wraps a generator that returns 
#    (terminals, size, stream) triplets.
#    '''
#    
#    def __init__(self, generator, join=list, simple=None):
#        if simple is not None:
#            self.__simple = simple
#        else:
#            self.__simple = SimpleGeneratorStream(generator, join)
#        
#    def __getitem__(self, spec):
#        '''
#        [n] returns a character (string of length 1)
#        [n:] returns a new SimpleStream instance that starts at the offset n
#        [n:m] returns a sequence (ie string, list, etc)
#        '''
#        def translate(triplet):
#            '''Helper'''
#            (terminals, size, stream) = triplet
#            return (terminals, stream[0:size]) 
#        if isinstance(spec, int):
#            return translate(self.__simple[spec])
#        elif isinstance(spec, slice) and isinstance(spec.start, int):
#            if spec.step is None and spec.stop is None:
#                return LocationGeneratorStream(None, None, 
#                                               self.__simple.__getitem__(spec))
#            elif spec.step is None and isinstance(spec.stop, int):
#                # pylint: disable-msg=W0141
#                return list(map(translate, 
#                                self.__simple.__getitem__(spec)))
#        raise IndexError()
#    
#    def __bool__(self):
#        '''
#        Non-empty?
#        '''
#        return bool(self.__simple)
#    
#    # Python 2.6
#    def __nonzero__(self):
#        return self.__bool__()
#
#    def __len__(self):
#        '''
#        Amount of remaining data.
#        '''
#        return len(self.__simple)
#    
#    def __repr__(self):
#        return '<LocationGeneratorStream>'
#    
#    def __str__(self):
#        return 'Wrapped stream'
#    
#    def __hash__(self):
#        return hash(self.__simple)
#    
#    def __eq__(self, other):
#        # pylint: disable-msg=W0212
#        # (we test for the type and it's the same as us)
#        return isinstance(other, LocationGeneratorStream) and \
#            self.__simple == other.__simple
#    
#    def location(self):
#        '''
#        A tuple containing line number, line offset, character offset,
#        the line currently being processed, and a description of the source.
#        
#        The line number is -1 if this is past the end of the file.
#        '''
#        try:
#            return self.__simple[0][2].location()
#        except IndexError:
#            return (-1, -1, -1, None, None)
#   
#    def text(self):
#        '''
#        The line of text in the underlying line indexed by this stream,
#        starting at the offset.  Needed by ``Regexp`` for strings.
#        '''
#        return self.__simple[0][2].text()
