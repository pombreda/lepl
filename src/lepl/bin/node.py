
'''
A representation of a binary structure within Python.  This allows binary
data to be accessed in a a hierarchical, structured manner with named fields.
Internally, values a re stored as (length, value) pairs, where length is the
number of bits and value is a byte array that contains a value for those
bits (Possibly with implicit zero padding).  Externally, values can be
read and set in a variety of forms.
'''