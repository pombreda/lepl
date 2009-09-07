
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
Convert structured Python data to a binary stream.

Writing a good API for binary encoding of arbitrary objects does not seem to
be easy.  In addition, this is my first attempt.  My apologies in advance.
This is a very basic library - the hope is that something like ASN.1 can
then be built on this (if someone buys me a copy of the spec...!)

The most obvious solution might be to require everything that must be encoded
implement some method.  Given Python's dynamic nature, ABCs, etc, this might
be possible, but it does seem that it could require some rather ugly hacks in
some cases, when using existing types.

The next simplest approach seems to be to use some kind of separate dispatch
(rather than the classes themselves) to convert things to a standard 
intermediate format.  That is what I do here.  The intermediate format
is the pair (type, BitString), where "type" can be any value (but will be the
type of the value in all implementations here - value could be used, but we're
trying to give some impression of a layered approach).

Encoding a structure then requires three steps:

1. Defining a serialisation of composite structures.  Only acyclic structures
   are considered (I am more interested in network protocols than pickling,
   which already has a Python solution)
    
2. Converting individual values in the serial stream to the intermediate 
   representation.

3. Encoding the intermediate representation into a final BitString.   

Support for each of these steps is provided by LEPL.  Stage 1 comes from the
graph and node modules; 2 is provided below (leveraging BitString's class 
methods); 3 is only supported in a simple way below, with the expectation
that future modules might extend both encoding and matching to, for example, 
ASN.1.
'''

if bytes is str:
    print('Binary parsing unsupported in this Python version')
else:

    from functools import reduce as reduce_
    from operator import add
    
    from lepl.bin.bits import BitString, STRICT
    from lepl.graph import leaves
    from lepl.node import Node
    
    
    def dispatch_table(big_endian=True, encoding=None, errors=STRICT):
        '''
        Convert types appropriately.
        '''
        # pylint: disable-msg=W0108
        # consistency
        return {int: lambda n: BitString.from_int(n, ordered=big_endian),
                str: lambda s: BitString.from_str(s, encoding, errors),
                bytes: lambda b: BitString.from_bytearray(b),
                bytearray: lambda b: BitString.from_bytearray(b),
                BitString: lambda x: x}
    
    
    def make_converter(table):
        '''
        Given a table, create the converter.
        '''
        def converter(value):
            '''
            The converter.
            '''
            type_ = type(value)
            if type_ in table:
                return (type_, table[type_](value))
            for key in table:
                if isinstance(value, key):
                    return (type_, table[key](value))
            raise TypeError('Cannot convert {0!r}:{1!r}'.format(value, type_))
        return converter
    
    
    def simple_serialiser(node, table):
        '''
        Serialize using the given table.
        '''
        stream = leaves(node, Node)
        converter = make_converter(table)
        return reduce_(add, [converter(value)[1] for value in stream])
