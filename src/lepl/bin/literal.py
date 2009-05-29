
'''
Specify and construct binary values.

This is necessary for tests and may be useful in its own right.  Note that
this does not include any idea of types, so encoding is very simple.  Support
for, say, ASN.1, might come later in a separate package (but this isn't it).

The construction of binary values is a two-stage process.  First, we describe
a Python structure.  Then we encode that structure as a binary value.  As is
standard in this package, the Python construct consists of `Binary` nodes.

The description of values has the form:
  Binary{byte/8=0xff, array/2.4=[1,2,3], 2.=0x1234, Binary{...}, {...}}
  
In more detail:
  {} is used for grouping, must exist outside the entire description, and
     defines a binary node.  If preceded by a capitalised name, then that
     is used to create a subclass of Binary (unless it is "Binary", in which
     case it is the default).  For now, repeated names are not validated in 
     any way for consistency.
  [] defines an array of bytes
  name/length=value is used for defining a value, in various ways:
    value anonymous value (byte or array)
    length=value anonymous value with specified length
    name=value named byte or array
    name/length=value named value with given length
    where length can be inferred from array length, or is taken to be 1 byte,
    and is distinguished from name since it parses as a float
'''

