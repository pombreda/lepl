
'''
A representation of a binary structure within Python.  This allows binary
data to be accessed in a a hierarchical, structured manner with named fields.
Internally, values a re stored as (length, bytes) pairs, where length is 
measured in bits and bytes is a byte array that contains a value for those
bits (possibly with zero padding).

Endianness is an issue here because we want to naturally "do the right thing"
and unfortunately this varies, depending on context.  Most target hardware
(x86) is little-endian, but network protocols are typically big-endian.

I personally prefer big-endian for long hex strings - it seems obvious that
0x123456 should be encoded as [0x12, 0x34, 0x56].  On the other hand, it
also seems reasonable that the integer 1193046 (=0x123456) should be stored 
small-endian as [0x56, 0x34, 0x12, 0x00] because that is how it is 
stored in memory.  Unfortunately we cannot implement both because integer
values do not contain any flag to say how the user specified them (hex or
decimal).

A very similar issue - that integers do not carry any information to say
how many leading zeroes were entered by the user - suggests a solution to
this problem.  To solve the leading zeroes issue we accept integers as strings
and do the conversion ourselves.  Since we are dealing with strings we can 
invent an entirely new encoding to specify endianness.  We will use 
little-endian for ints and the "usual" notation since this reflects the 
hardware (it appeals to the idea that we are simply taking the chunk of memory 
in which the integer existed and using it directly).  For big endian, we will 
use a trailing type flag (ie change "ends") in strings.

So 1193046, "1193046", 0x123456, "0x123456" all encode to [0x56, 0x34, 0x12]
(module some questions about implicit lengths).

But "123456x0" encodes to [0x12, 0x34, 0x56].    This does have a slight
wrinkle - 100b0 looks like a hex value (but is not, as it does not start with
0x).

There is a separate issue about arrays of values.  To avoid complicating
things even further, an array must contain only byte values.  
So [0x12, 0x34, 0x56] is OK, but [Ox1234, 0x56] is not.

A separate design issue is the use of tagged values here (length, bytes)
rather than an object.  It's not very "OO", but I think it makes sense in
this context.  It does assume that this is the dominant representation.
'''


from lepl.node import Node


def unpack_standard_form(arg):
    '''
    Detect args that do not need coercion.
    '''
    def standard_value(value):
        if isinstance(value, Binary):
            return True
        try:
            (l, b) = value
            if isinstance(l, int) and \
                    isinstance(b, bytes) or isinstance(b, bytearray):
                return True
        except ValueError:
            pass
        return False
    # anonymous value
    if standard_value(arg):
        return arg
    # named value
    (first, second) = arg
    if isinstance(first, str) and standard_value(second):
        return arg
    # non-standard
    raise ValueError('Not a standard form: {0!r}'.format(arg))
    
    
def unpack(arg):
    '''
    This processes the argument list to `Binary`, generating an argument list 
    suitable for `Node`.
    
    Possible forms are:
      Binary - an anonymous sub-node, which will be named after its class
      (name, Binary) - a named sub-node
      (length, bytes) - a binary value
      (name, (length, bytes)) - a named binary value
    In addition, we try to support:
      value - coerced to (length, bytes)
      (name, value) - coerced to (name, (length, bytes))
      (length, value) - coerce to (length, bytes)
      (name, (length, value)) - coerced to (name, (length, bytes))
    but there is considerable ambiguity here.
    '''
    try:
        return unpack_standard_form(arg)
    except ValueError:
        pass
    
    # we only expand tuples (not arbitrary sequences) for the various possible
    # structures because other sequences (eg lists of bytes) may be coerced as
    # values
    if isinstance(arg, tuple):
        (first, second) = arg
        # if first value is a string, we take it to be a name
        if isinstance(first, str):
             # if the second arg is also a tuple, we take it to be a 
             # (length, value) pair
             if isinstance(second, tuple):
                 (length, value) = second
                 return (first, coerce_known_length(length, value))
             # otherwise, we take it to be a single value for which we
             # must infer a length
             else:
                 return (first, coerce_unknown_length(second))
        # we don't have a named pair, so assume first is a length
        else:
            return coerce_known_length(first, second)
    # arg is not a tuple, so perhaps it's a raw value
    else:
        return coerce_unknown_length(arg)

    
def to_byte(v):
    if isinstance(v, str):
        iv = int(v.strip(), 0)
    else:
        iv = int(v)
    if iv < 0 or iv > 255:
        raise ValueError('Non-byte value: %r' % v)
    else:
        return iv
    
    
def bytes_for_bits(bits):
    '''
    The number of bytes required to specify the given number of bits.
    '''
    return (bits + 7) // 8


def int_as_string(value):
    '''
    Is the value a string formatted in the standard way for integers?
    '''
    if isinstance(value, str):
        try:
            int(value, 0)
            return True
        except ValueError:
            pass
    return False


def coerce_known_length(length, value):
    l = unpack_length(length)
    if isinstance(value, int) or int_as_string(value):
        a, v = [], int(value, 0) if isinstance(value, str) else value
        for i in range(bytes_for_bits(l)):
            a.append(v % 0x100)
            v = v // 0x100
        if v > 0:
            raise ValueError('Value contains more bits than length: %r/%r' % 
                             (value, length))
        else:
            return (l, bytes(a)) # little-endian
    # for anything else, we'll use unknown length and then pad
    (_l, v) = coerce_unknown_length(value)
    if len(v) > bytes_for_bits(l):
        raise ValueError('Coerced value exceeds length: %r/%r < %r' % 
                         (value, length, v))
    if len(v) * 8 < l:
        v = bytearray(v)
        # is this documented anywhere - it inserts zeroes
        v[0:0] = l - 8 * bytes_for_bits(v)
    return (l, v)


def coerce_unknown_length(value):
    # these are strictly not necessary for the use above, since they will be
    # considered standard form, but we'll include them in case this is used
    # elsewhere
    if isinstance(value, bytes):
        return (len(value) * 8, value)
    if isinstance(value, bytearray):
        return (len(value) * 8, value)
    # integers as strings with encoding have an implicit length
    if isinstance(value, str):
        value = value.strip()
        # don't include decimal as doesn't naturally imply a bit length
        bigendian, format = None, {'b': (2, 1), 'o': (8, 3), 'x': (16, 4)}
        if value.endswith('0') and not value[-2].isdigit():
            (base, bits) = format.get(value[-2].lower(), (None, None))
            iv, bigendian = int('0' + value[-2] + value[0:-2], 0), True
        elif value.startswith('0') and not value[1].isdigit():
            (base, bits) = format.get(value[1].lower(), (None, None))
            iv, bigendian = int(value, 0), False
        if bigendian is not None:
            if not base:
                raise ValueError('Unknown base: %r' % value)
            a = []
            while iv:
                a.append(iv % 0x100)
                iv = iv // 0x100
            if not a:
                a = [0]
            if bigendian:
                b = bytes(reversed(a))
            else:
                b = bytes(a)
            return (bits * (len(value) - 2), b)
        else:
            value = int(value) # int handled below
    # treat plain ints as byte values
    if isinstance(value, int):
        return (8, bytes([to_byte(value)]))
    # otherwise, attempt to treat as a sequence of some kind
    b = bytes([to_byte(v) for v in value])
    return (8 * len(b), b)


def unpack_length(length):
    '''
    Length is in bits, unless a decimal is specified, in which case it
    it has the structure bytes.bits.  Obviously this is ambiguous with float
    values (eg 3.1 or 3.10), but since we only care about bits 0-7 we can
    avoid any issues by requiring that range. 
    '''
    def unpack_float(l):
        bytes = int(l)
        bits = int(10 * (l - bytes) + 0.5)
        if bits < 0 or bits > 7:
            raise ValueError('Bits specification must be between 0 and 7')
        return bytes * 8 + bits
    if isinstance(length, str):
        try:
            length = int(length, 0) # support explicit base prefix
        except ValueError:
            length = float(length)
    if isinstance(length, int):
        return length
    if isinstance(length, float):
        return unpack_float(length)
    raise TypeError('Cannot infer length from %r' % length)


class Binary(Node):

    def __init__(self, args, unpack=unpack):
        self.___unpack = unpack
        super(Binary, self).__init__([unpack(arg) for arg in args])
