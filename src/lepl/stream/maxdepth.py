# Copyright 2010 Andrew Cooke

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
Track the maximum depth of a stream.
'''

from lepl.stream.stream import LocationStream, SimpleStream
from lepl.matchers.support import trampoline_matcher_factory
from lepl.support.lib import open_stop, format


class Memory(object):
    
    def __init__(self, deepest):
        self.deepest = deepest


def facade_factory(stream):
    '''
    Generate a facade class (we need a class so that we can register as
    a subclass of the correct stream interface).
    '''
    
    class Facade(object):
        
        __slots__ = ['_Facade__stream', '_Facade__memory', '__weakref__']
        
        def __init__(self, stream, memory):
            self.__stream = stream
            self.__memory = memory
            memory.deepest = stream
                
        def __getitem__(self, spec):
            if isinstance(spec, slice) and open_stop(spec):
                return Facade(self.__stream.__getitem__(spec), self.__memory)
            else:
                return self.__stream.__getitem__(spec)

        def __bool__(self):
            return bool(self.__stream)
    
        def __nonzero__(self):
            return self.__bool__() 
    
        def __len__(self):
            return len(self.__stream)

        def __repr__(self):
            return repr(self.__stream)
    
        def __str__(self):
            return str(self.__stream)
    
        def __hash__(self):
            return hash(self.__stream)
        
        def __eq__(self, other):
            return isinstance(other, Facade) and self.__stream == other.__stream
        
        @property
        def location(self):
            return self.__stream.location

        @property
        def line_number(self):
            return self.__stream.line_number
        
        @property
        def line_offset(self):
            return self.__stream.line_offset
        
        @property
        def character_offset(self):
            return self.__stream.character_offset
   
        @property
        def text(self):
            # this is a hack needed for inter-op with python regexps, which
            # only accept strings.  it's identical to the hack in Regexp().
            try:
                return self.__stream.text
            except AttributeError:
                return self.__stream
    
        @property
        def source(self):
            return self.__stream.source
        
        @property
        def stream(self):
            return self.__stream

    if isinstance(stream, LocationStream):
        LocationStream.register(Facade)
    else:
        SimpleStream.register(Facade)
    memory = Memory(stream)
    facade = Facade(stream, memory)
    return (facade, memory)


@trampoline_matcher_factory()
def FullMatch(matcher, eos=False):
    
    def _matcher(support, stream1):
        (stream2, memory) = facade_factory(stream1)
        generator = matcher._match(stream2)
        first = True
        try:
            while True:
                (result2, stream3) = yield generator
                # drop stream wrapper
                stream4 = stream3.stream
                if first and eos and stream4:
                    break
                yield (result2, stream4)
                first = False
        except StopIteration:
            pass
        if first:
            raise FullMatchException(memory.deepest)
    return _matcher


class FullMatchException(Exception):
    
    def __init__(self, stream):
        try:
            msg = format("The match failed at '{0}',"
                         "\nLine {1}, character {2} of {3}.",
                         stream, stream.line_number, stream.line_offset,
                         stream.source)
        except AttributeError:
            msg = format("The match failed at '{0}'.", stream)
        super(FullMatchException, self).__init__(msg)
        self.stream = stream

