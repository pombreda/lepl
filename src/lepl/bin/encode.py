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

from functools import reduce
from operator import add

from lepl.bin.bits import BitString, STRICT
from lepl.graph import leaves
from lepl.node import Node


def dispatch_table(big_endian=True, encoding=None, errors=STRICT):
    return {int: lambda n: BitString.from_int(n, ordered=big_endian),
            str: lambda s: BitString.from_str(s, encoding, errors),
            bytes: lambda b: BitString.from_bytearray(b),
            bytearray: lambda b: BitString.from_bytearray(b),
            BitString: lambda x: x}


def make_converter(table):
    def converter(value):
        type_ = type(value)
        if type_ in table:
            return (type_, table[type_](value))
        for key in table:
            if isinstance(value, key):
                return (type_, table[key](value))
        raise TypeError('Cannot convert {0!r}:{1!r}'.format(value, type_))
    return converter


def simple_serialiser(node, table):
    stream = leaves(node, Node)
    converter = make_converter(table)
    result = BitString()
    return reduce(add, [converter(value)[1] for value in stream])
