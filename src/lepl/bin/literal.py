
'''
Specify and construct binary values.

This is necessary for tests and may be useful in its own right.  Note that
this does not include any idea of types, so encoding is very simple.  Support
for, say, ASN.1, might come later in a separate package (but this isn't it).

The construction of binary values is a two-stage process.  First, we describe
a Python structure.  Then we encode that structure as a binary value.  As is
standard in this package, the Python construct consists of `Binary` nodes.
'''

