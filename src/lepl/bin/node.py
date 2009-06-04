
'''
A representation of a binary structure within Python.  This allows binary
data to be accessed in a a hierarchical, structured manner with named fields.

Since this is based on `Node`, data can be stored in three ways: as anonymous
values, named values, or nested nodes.  In this way, the structure of data 
and the "kind" of each value are separated.

Different kinds of values should implement the `Value` interface.

The default `Value` implementation, `RawBits` stores values as an array
of bytes, together with a bit length.
'''


from abc import ABCMeta, abstractmethod
from traceback import print_exc

from lepl.node import Node


# Python 2.6
#class Value(metaclass=ABCMeta):
Value = ABCMeta('Value', (object, ), {})

class BaseValue(Value):
    '''
    The interface values should implement.
    '''
    
    @abstractmethod
    def encode(self, encoding=None):
        '''
        Generate (len, bytes) encoded bits
        '''


class BitArray(BaseValue):
    '''
    An array of bits, or arbitrary length.
    '''
    
    def __init__(self, arg=None):
        if arg is None:
            self.__value = bytearray()
            self.__length = 0
        else:
            (self.__value, self.__length) = normalize(arg)
        
    def encode(self, encoding=None):
        return (self._value, self._length)
    
    def bytes(self, shift=0):
        '''
        Return a series of (value, length) values, where value is an integer
        and length is the number of significant bits from the lsb, which is
        8 except for the first value, which will have the first shift bits set 
        to zero (and which are not included in the length).
        '''
        return ByteIterator(self.__value, self.__length, shift)
    
    def bits(self):
        '''
        Return a series of (bit, 1) values that contain the contents.
        '''
        return BitIterator(self.__value, self.__length)

    def __str__(self):
        hx = ''.join(hex(x)[2:] for x in self.__value)
        return '{0}x0/{1}'.format(hx, self.__length)
    
    def __repr__(self):
        return 
        
    def __len__(self):
        return self.__length
    
    def raw_bytes(self):
        return self.__value

    def __iter__(self):
        return self.bits()
        
    def append(self, arg):
        '''
        Append bits in any of the supported formats.
        '''
        self.extend(BitArray(arg))
    
    def extend(self, other):
        '''
        Append another BitArray.
        '''
        stub = self.__length % 8
        for (value, length) in other.bytes(stub):
            if stub:
                self.__value[-1] |= value
                sub = False
            else:
                self.__value.append(value)
            self.__length += length
            

class BitIterator(object):
    
    def __init__(self, value, length):
        self.__value = value
        self.__length = length
        self.__offset = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.__offset < self.__length:
            b = self.__value[self.__offset // 8]
            b >>= self.__offset % 8
            self.__offset += 1
            return (b & 1, 1)
        else:
            raise StopIteration()
        

class ByteIterator(object):
    
    def __init__(self, value, length, shift):
        assert 0 <= shift < 8
        self.__value = value
        self.__length = length
        self.__shift = shift
        self.__offset = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.__shift:
            if self.__offset:
                # general case, where we need to combine two bytes
                remain = self.__length - self.__offset
                if remain > 0:
                    b = self.__value[self.__offset // 8] >> (8 - self.__shift)
                    bits = min(remain, self.__shift)
                    self.__offset += bits
                    remain -= bits
                    if remain > 0:
                        b |= self.__value[self.__offset // 8] << self.__shift
                        b &= 0xff
                        extra = min(remain, 8 - self.__shift)
                        self.__offset += extra
                        bits += extra
                    return (b, bits)
                else:
                    raise StopIteration()
            else:
                # initial shifted chunk (could fold into above, but...)
                b = self.__value[0] << self.__shift
                b &= 0xff
                bits = min(self.__length, 8 - self.__shift)
                self.__offset = bits
                return (b, bits)
        else:
            # byte aligned, so life is simple
            remain = self.__length - self.__offset
            if remain > 0:
                b = self.__value[self.__offset // 8]
                self.__offset += 8
                return (b, min(remain, 8))
            else:
                raise StopIteration()


def normalize(arg):
    '''
    Convert a range of arguments to (bytes, length) 

    Endianness is an issue here because we want to naturally "do the right 
    thing" and unfortunately this varies, depending on context.  Most target 
    hardware (x86) is little-endian, but network protocols are typically 
    big-endian.
    
    I personally prefer big-endian for long hex strings - it seems obvious that
    0x123456 should be encoded as [0x12, 0x34, 0x56].  On the other hand, it
    also seems reasonable that the integer 1193046 (=0x123456) should be stored 
    small-endian as [0x56, 0x34, 0x12, 0x00] because that is how it is 
    stored in memory.  Unfortunately we cannot implement both because integer
    values do not contain any flag to say how the user specified them (hex or
    decimal).
    
    A very similar issue - that integers do not carry any information to say
    how many leading zeroes were entered by the user - suggests a solution to
    this problem.  To solve the leading zeroes issue we accept integers as 
    strings and do the conversion ourselves.  Since we are dealing with strings 
    we can invent an entirely new encoding to specify endianness.  We will use 
    little-endian for ints and the "usual" notation since this reflects the 
    hardware (it appeals to the idea that we are simply taking the chunk of 
    memory in which the integer existed and using it directly).  For big endian, 
    we will use a trailing type flag (ie change "ends") in strings.
    
    So 1193046, "1193046", 0x123456, "0x123456" all encode to [0x56, 0x34, 0x12]
    (module some questions about implicit lengths).
    
    But "123456x0" encodes to [0x12, 0x34, 0x56].  This does have a slight
    wrinkle - 100b0 looks like a hex value (but is not, as it does not start 
    with 0x).
    
    There is a separate issue about arrays of values.  To avoid complicating
    things even further, an array must contain only byte values.  
    So [0x12, 0x34, 0x56] is OK, but [Ox1234, 0x56] is not.
    
    A separate design issue is the use of tagged values here (length, bytes)
    rather than an object.  It's not very "OO", but I think it makes sense in
    this context.  It does assume that this is the dominant representation.
    '''
    value, length = arg, None
    if isinstance(arg, BitArray):
        value, length = arg.raw_bytes, len(arg)
    elif isinstance(arg, tuple):
        try:
            (value, length) = arg
        except ValueError:
            pass
        except TypeError:
            pass
    if length is not None:
        length = unpack_length(length)
    # handle direct bytes
    if isinstance(value, bytes) or isinstance(value, bytearray):
        if length is None:
            length = len(value) * 8
        return (pad_bytes(value, length), length)
    # otherwise, try more complex solutions
    if length:
        return coerce_known_length(value, length)
    else:
        return coerce_unknown_length(value)
    

def coerce_known_length(value, length):
    # knowing length means we can handle integers
    if isinstance(value, int) or isinstance(value, str):
        bigendian = is_bigendian(value)
        a, v = [], extended_int(value)
        for i in range(bytes_for_bits(length)):
            a.append(v % 0x100)
            v = v // 0x100
        if v > 0:
            raise ValueError('Value contains more bits than length: %r/%r' % 
                             (value, length))
        else:
            if bigendian:
                a = reversed(a)
            return (bytes(a), length) # little-endian
        
    # for anything else, we'll use unknown length and then pad
    (v, _) = coerce_unknown_length(value)
    if len(v) > bytes_for_bits(length):
        raise ValueError('Coerced value exceeds length: %r/%r < %r' % 
                         (value, length, v))
    return (pad_bytes(v, length), length)


def coerce_unknown_length(value):
    # integers as strings with encoding have an implicit length
    # (except for decimals!)
    if isinstance(value, str):
        value = value.strip()
        # don't include decimal as doesn't naturally imply a bit length
        bigendian, format = None, {'b': (2, 1), 'o': (8, 3), 'x': (16, 4)}
        if is_bigendian(value):
            (base, bits) = format.get(value[-2].lower(), (None, None))
            iv, bigendian = extended_int(value), True
        elif value.startswith('0') and not value[1].isdigit():
            (base, bits) = format.get(value[1].lower(), (None, None))
            iv, bigendian = extended_int(value), False
        if bigendian is not None:
            if not base:
                raise ValueError('Base unsupported for unknown length: %r' % 
                                 value)
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
            return (b, bits * (len(value) - 2))
        else:
            value = int(value) # int handled below
    # treat plain ints as byte values
    if isinstance(value, int):
        return (bytes([to_byte(value)]), 8)
    # otherwise, attempt to treat as a sequence of some kind
    accumulate = BitArray()
    for arg in value:
        accumulate.append(arg)
    return (accumulate.raw_bytes(), len(accumulate))


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
            length = extended_int(length) # support explicit base prefix
        except ValueError:
            length = float(length)
    if isinstance(length, int):
        return length
    if isinstance(length, float):
        return unpack_float(length)
    raise TypeError('Cannot infer length from %r' % length)


def extended_int(value):
    '''
    Convert a string to an integer.
    
    This works like int(string, 0), but supports '0d' for decimals, and
    accepts both 0x... and ...x0 forms.
    '''
    if isinstance(value, str):
        value = value.strip()
        # convert postfix to prefix
        if value.endswith('0') and len(value) > 1 and not value[-2].isdigit():
            value = '0' + value[-2] + value[0:-2]
        # drop 0d for decimal
        if value.startswith('0d') or value.startswith('0D'):
            value = value[2:]
        return int(value, 0)
    else:
        return int(value)


def to_byte(value):
    v = extended_int(value)
    if v < 0 or v > 255:
        raise ValueError('Non-byte value: %r' % value)
    else:
        return v
    
    
def is_bigendian(value):
    '''
    Test for a big-endian format integer.
    '''
    if isinstance(value, str):
        value = value.strip()
        return value.endswith('0') and len(value) > 2 and not value[-2].isdigit()
    else:
        return False


def bytes_for_bits(bits):
    '''
    The number of bytes required to specify the given number of bits.
    '''
    return (bits + 7) // 8


def pad_bytes(value, length):
    '''
    Make sure value has sufficient bytes for length bits (and clone).
    '''
    if len(value) * 8 < length:
        v = bytearray(v)
        # is this documented anywhere - it inserts zeroes
        v[0:0] = length - 8 * bytes_for_bits(len(v))
    return bytearray(v[0:bytes_for_bits(length)])


class Binary(Node):

    def __init__(self, args, unpack=BitArray):
        super(Binary, self).__init__(args, value=unpack)
