
'''
A utility class for binary values of arbitrary length.

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
(module some questions about implicit/explicit lengths).

But "123456x0" encodes to [0x12, 0x34, 0x56].  This does have a slight
wrinkle - 100b0 looks like a hex value (but is not, as it does not start 
with 0x).

Note: No attempt is made to handle sign (complements etc).
'''

from lepl.matchers import ApplyArgs


STRICT = 'strict'


class Int(int):
    '''
    An integer with a length (the number of bits).  This extends Python's type
    system so that we can distinguish between different integer types, which
    may have different encodings.
    '''
    
    def __new__(cls, value, length):
        return super(Int, cls).__new__(cls, str(value), 0)
    
    def __init__(self, value, length):
        super(Int, self).__init__()
        self.__length = length
        
    def __len__(self):
        return self.__length

    def __repr__(self):
        return 'Int({0},{1})'.format(super(Int, self).__str__(), self.__length)


def swap_table():
    '''
    Table of reversed bit patterns for 8 bits.
    '''
    table = [0] * 256
    power = [1 << n for n in range(8)]
    for n in range(8):
        table[1 << n] = 1 << (7 - n)
    for i in range(256):
        if not table[i]:
            for p in power:
                if i & p:
                    table[i] |= table[p]
        table[table[i]] = i
    return table


class BitString(object):
    '''
    A sequence of bits, of arbitrary length.  Has similar semantics to
    strings, in that a single index is itself a BitString (of unit length).
    
    This is intended as a standard format for arbitrary binary data, to help
    with conversion between other types.  In other words, convert to and from
    this, and then chain conversions.
    
    BitStr are stored as a contiguous sequence in an array of bytes.  Both bits
    and bytes are "little endian" - this allows arbitrary lengths of bits,
    at arbitrary offsets, to be given values without worrying about
    alignment.
    
    The bit sequence starts at bit 'offset' in the first byte and there are
    a total of 'length' bits.  The number of bytes stored is the minimum
    implied by those two values, with zero padding.
    '''
    
    __swap = swap_table() 
    
    def __init__(self, value=None, length=0, offset=0):
        '''
        value is a bytes() instance that contains the data.
        
        length is the number of valid bits.  If given as a float it is the
        number of bytes (bits = int(float) * 8 + decimal(float) * 10)
        
        offset is the index of the first valid bit in the value. 
        '''
        if value is None:
            value = bytes()
        if not isinstance(value, bytes):
            raise TypeError('BitString wraps bytes: {0!r}'.format(value))
        if length < 0:
            raise ValueError('Negative length: {0!r}'.format(length))
        if not 0 <= offset < 8 :
            raise ValueError('Non-byte offset: {0!r}'.format(offset))
        self.__bytes = value
        self.__length = unpack_length(length)
        self.__offset = offset
        if len(value) != bytes_for_bits(self.__length, self.__offset):
            raise ValueError('Inconsistent length: {0!r}/{1!r}'
                             .format(value, length))
        
    def bytes(self, offset=0):
        '''
        Return a series of bytes values, which encode the data for len(self)
        bits when offset=0 (with final padding in the last byte if necessary).
        It is the caller's responsibility to discard any trailing bits.
        
        When 0 < offset < 8 then the data are zero-padded by offset bits first.
        '''
#        if self.__offset and offset == 0:
#            # normalize our own value
#            self.__bytes = \
#                bytes(ByteIterator(self.__bytes, self.__length, 
#                                   self.__offset, offset))
#            self.__offset = 0
        return ByteIterator(self.__bytes, self.__length, self.__offset, offset)
    
    def bits(self):
        '''
        Return a series of bits (encoded as booleans) that contain the contents.
        '''
        return BitIterator(self.__bytes, 0, self.__length, 1, self.__offset)

    def __str__(self):
        '''
        For 64 bits or less, show bits grouped by byte (octet), with bytes
        and bits running from left to right.  This is a "picture" of the bits.
        
        For more than 64 bits, give a hex encoding of bytes (right padded
        with zeros), shown in big-endian format.
        
        In both cases, the length in bits is given after a trailing slash.
        
        Whatever the internal offset, values are displayed with no initial
        padding.
        '''
        if self.__length > 64:
            hx = ''.join(hex(x)[2:] for x in self.bytes())
            return '{0}x0/{1}'.format(hx, self.__length)
        else:
            chars = []
            byte = []
            count = 0
            for bit in self.bits():
                if not count % 8:
                    chars.extend(byte)
                    byte = []
                    if count:
                        chars.append(' ')
                if bit.zero():
                    byte.append('0')
                else:
                    byte.append('1')
                count += 1
            chars.extend(byte)
            return '{0}b0/{1}'.format(''.join(chars), self.__length)
    
    def __repr__(self):
        '''
        An explicit display of internal state, including padding and offset.
        '''
        return 'BitString({0!r}, {1!r}, {2!r})'.format(self.__bytes, self.__length, self.__offset)
        
    def __len__(self):
        return self.__length
    
    def zero(self):
        for b in self.__bytes:
            if b != 0:
                return False
        return True
    
    def offset(self):
        '''
        The internal offset.  This is not useful as an external API, but helps
        with debugging.
        '''
        return self.__offset
    
    def __iter__(self):
        return self.bits()
        
    def __add__(self, other):
        '''
        Combine two sequences, appending then together.
        '''
        bb = bytearray(self.to_bytes())
        matching_offset = self.__length % 8
        for b in other.bytes(matching_offset):
            if matching_offset:
                bb[-1] |= b
                matching_offset = False
            else:
                bb.append(b)
        return BitString(bytes(bb), self.__length + len(other))
    
    def to_bytes(self, offset=0):
        '''
        Return a bytes() object, right-padded with zero bits of necessary.
        '''
        if self.__offset == offset:
            return self.__bytes
        else:
            return bytes(self.bytes(offset))
    
    def to_int(self, big_endian=False):
        '''
        Convert the entire bit sequence (of any size) to an integer.
        
        Big endian conversion is only possible if the bits form a whole number
        of bytes.
        '''
        if big_endian and self.__length % 8:
            raise ValueError('Length is not a multiple of 8 bits, so big '
                             'endian integer poorly defined: {0}'
                             .format(self.__length))
        b8 = self.bytes()
        if not big_endian:
            b8 = reversed(list(b8))
        value = 0
        for b in b8:
            value = (value << 8) + b
        return Int(value, self.__length)
    
    def to_str(self, encoding=None, errors='strict'):
        if encoding:
            return bytes(self.bytes()).decode(encoding=encoding, errors=errors)
        else:
            return bytes(self.bytes()).decode(errors=errors)

    def __int__(self):
        return self.to_int()
    
    def __index__(self):
        return self.to_int()
    
    def __invert__(self):
        inv = bytearray([0xff ^ b for b in self.bytes()])
        if self.__length % 8:
            inv[-1] &= 0xff >>  self.__length % 8
        return BitString(bytes(inv), self.__length) 
    
    def __getitem__(self, index):
        if not isinstance(index, slice):
            index = slice(index, index+1, None)
        (start, stop, step) = index.indices(self.__length)
        if step == 1:
            start += self.__offset
            stop += self.__offset
            bb = bytearray(self.__bytes[start // 8:bytes_for_bits(stop)])
            if start % 8:
                bb[0] &= 0xff << start % 8
            if stop % 8:
                bb[-1] &= 0xff >> 8 - stop % 8
            return BitString(bytes(bb), stop - start, start % 8)
        else:
            acc = BitString()
            for b in BitIterator(self.__bytes, start, stop, step, self.__offset):
                acc += b
            return acc
        
    def __eq__(self, other):
        if not isinstance(other, BitString) or self.__length != other.__length:
            return False
        for (a, b) in zip(self.bytes(), other.bytes()):
            if a != b:
                return False
        return True
    
    def __hash__(self):
        return hash(self.__bytes) ^ self.__length
    
    @staticmethod
    def from_byte(value):
        return BitString.from_int(value, 8)
    
    @staticmethod
    def from_int32(value, big_endian=None):
        return BitString.from_int(value, 32, big_endian)
    
    @staticmethod
    def from_int64(value, big_endian=None):
        return BitString.from_int(value, 64, big_endian)
    
    @staticmethod
    def from_int(value, length=None, big_endian=None):
        '''
        Value can be an int, or a string with a leading or trailing tag.
        A plain int, or no tag, or leading tag, is byte little-endian by 
        default.
        
        Length and big-endianness are inferred from the format for values 
        given as strings, but explicit parameters override these.
        If no length is given, and none can be inferred, 32 bits is assumed
        (bit length cannot be inferred for decimal values, even as strings).
        
        The interpretation of big-endian values depends on the base and is 
        either very intuitive and useful, or completely stupid.  Use at your
        own risk.
        
        Big-endian hex values must specify an exact number of bytes (even 
        number of hex digits).  Each separate byte is assigned a value 
        according to big-endian semantics, but with a byte small-endian
        order is used.  This is consistent with the standard conventions for
        network data.  So, for example, 1234x0 gives two bytes.  The first
        contains the value 0x12, the second the value 0x34.
        
        Big-endian binary values are taken to be a "picture" of the bits,
        with the array reading from left to right.  So 0011b0 specifies 
        four bits, starting with two zeroes.
        
        Big-endian decimal and octal values are treated as hex values.
        '''
        # order is very important below - edit with extreme care
        bits = None
        if isinstance(value, str):
            value.strip()
            # move postfix to prefix, saving endian hint
            if value.endswith('0') and len(value) > 1 and \
                    not value[-2].isdigit() \
                    and not (len(value) == 3 and value.startswith('0')):
                value = '0' + value[-2] + value[0:-2]
                if big_endian is None:
                    big_endian = True
            # drop 0d for decimal
            if value.startswith('0d') or value.startswith('0D'):
                value = value[2:]
            # infer implicit length
            if len(value) > 1 and not value[1].isdigit() and length is None:
                bits = {'b':1, 'o':3, 'x':4}.get(value[1].lower(), None)
                if not bits:
                    raise ValueError('Unexpected base: {0!r}'.format(value))
                length = bits * (len(value) - 2)
            if big_endian and bits == 1:
                # binary value is backwards!
                value = value[0:2] + value[-1:1:-1]
            value = int(value, 0)
        if length is None:
            if isinstance(value, Int):
                # support round-tripping of sized integers
                length = len(value)
            else:
                # assume 32 bits if nothing else defined
                length = 32
        length = unpack_length(length)
        if length % 8 and big_endian and bits != 1:
            raise ValueError('A big-endian int with a length that '
                             'is not an integer number of bytes cannot be '
                             'encoded as a stream of bits: {0!r}/{1!r}'
                             .format(value,  length))
        a, v = bytearray(), value
        for i in range(bytes_for_bits(length)):
            a.append(v & 0xff)
            v >>= 8
        if v > 0:
            raise ValueError('Value contains more bits than length: %r/%r' % 
                             (value, length))
        # binary was swapped earlier
        if big_endian and bits != 1:
            a = reversed(a)
        return BitString(bytes(a), length)
        
    @staticmethod
    def from_sequence(value, unpack=lambda x: x):
        '''
        Unpack is called for each item in turn (so should be, say, from_byte).
        '''
        accumulator = BitString()
        for item in value:
            accumulator += unpack(item)
        return accumulator
            
    @staticmethod
    def from_bytearray(value):
        if not isinstance(value, bytes):
            value = bytes(value)
        return BitString(value, len(value) * 8)
            
    @staticmethod
    def from_str(value, encoding=None, errors=STRICT):
        if encoding:
            return BitString.from_bytearray(value.encode(encoding=encoding, errors=errors))
        else:
            return BitString.from_bytearray(value.encode(errors=errors))
        
        
def unpack_length(length):
    '''
    Length is in bits, unless a decimal is specified, in which case it
    it has the structure bytes.bits.  Obviously this is ambiguous with float
    values (eg 3.1 or 3.10), but since we only care about bits 0-7 we can
    avoid any issues by requiring that range. 
    '''
    if isinstance(length, str):
        try:
            length = int(length, 0)
        except ValueError:
            length = float(length)
    if isinstance(length, int):
        return length
    if isinstance(length, float):
        bytes = int(length)
        bits = int(10 * (length - bytes) + 0.5)
        if bits < 0 or bits > 7:
            raise ValueError('BitStr specification must be between 0 and 7')
        return bytes * 8 + bits
    raise TypeError('Cannot infer length from %r' % length)


def bytes_for_bits(bits, offset=0):
    '''
    The number of bytes required to specify the given number of bits.
    '''
    return (bits + 7 + offset) // 8


class BitIterator(object):
    
    def __init__(self, value, start, stop, step, offset):
        assert 0 <= offset < 8
        self.__bytes = value
        self.__start = start
        self.__stop = stop
        self.__step = step
        self.__offset = offset
        self.__index = start
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if (self.__step > 0 and self.__index < self.__stop) \
            or (self.__step < 0 and self.__index > self.__stop):
            index = self.__index + self.__offset
            b = self.__bytes[index // 8] >> index % 8
            self.__index += self.__step
            return ONE if b & 0x1 else ZERO
        else:
            raise StopIteration()
        

class ByteIterator(object):
    
    def __init__(self, value, length, existing, required):
        assert 0 <= required < 8
        assert 0 <= existing < 8
        self.__bytes = value
        self.__length = length
        self.__required = required
        self.__existing = existing
        if self.__required > self.__existing:
            self.__index = -1
        else:
            self.__index = 0
        self.__total = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.__required == self.__existing:
            # byte aligned
            if self.__index < len(self.__bytes):
                b = self.__bytes[self.__index]
                self.__index += 1
                return b
            else:
                raise StopIteration()
        elif self.__required > self.__existing:
            # need to add additional offset
            if self.__index < 0:
                if self.__total < self.__length:
                    # initial offset chunk
                    b = 0xff & (self.__bytes[0] << (self.__required - self.__existing))
                    self.__index = 0
                    self.__total = 8 - self.__required
                    return b
                else:
                    raise StopIteration()
            else:
                if self.__total < self.__length:
                    b = 0xff & (self.__bytes[self.__index] >> (8 - self.__required + self.__existing))
                    self.__index += 1
                    self.__total += self.__required
                else:
                    raise StopIteration()
                if self.__total < self.__length:
                    b |= 0xff & self.__bytes[self.__index] << (self.__required - self.__existing)
                    self.__total += 8 - self.__required
                return b
        else:
            # need to correct for additional offset
            if self.__total < self.__length:
                b = 0xff & (self.__bytes[self.__index] >> (self.__existing - self.__required))
                self.__index += 1
                self.__total += 8 - self.__existing + self.__required
            else:
                raise StopIteration()
            if self.__total < self.__length:
                b |= 0xff & (self.__bytes[self.__index] << (8 - self.__existing + self.__required))
                self.__total += self.__existing - self.__required
            return b


ONE = BitString(b'\x01', 1)
ZERO = BitString(b'\x00', 1)

