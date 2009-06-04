
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
'''

from lepl.bin.node import BaseValue


class BitString(object):
    '''
    A sequence of bits, of arbitrary length.  Has similar semantics to
    strings, in that a single index is itself a BitString (of unit length).
    
    This is intended as a standard format for arbitrary binary data, to help
    with conversion between other types.  In other words, convert to and from
    this, and then chain conversions.
    
    Bits are stored as a contiguous sequence in an array of bytes.  The bytes
    are ordered by increasing array index; bits within a byte are ordered from
    lsb to msb ("bit little endian" but "byte big endian").
    
    The bit sequence starts at bit 'offset' in the first byte and there are
    a total of 'length' bits.  The number of bytes stored is the minimum
    implied by those two values, with zero padding.
    '''
    
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
        if offset < 0:
            raise ValueError('Negative offset: {0!r}'.format(offset))
        self.__bytes = value[offset // 8:] if offset else value
        self.__length = unpack_length(length) - offset // 8
        self.__offset = offset % 8
        if len(value) != bytes_for_bits(self.__length, self.__offset):
            raise ValueError('Inconsistent length: {0!r}/{1!r}'
                             .format(value, length))
        
    def bytes(self, offset=0):
        '''
        Return a series of bytes values, which encode the data for len(self)
        bits when offset=0.  When 0 < offset < 8 then the data are zero-padded
        by offset bits first.
        
        It is the caller's responsibility to discard any trailing bits.
        '''
        return ByteIterator(self.__bytes, self.__length, self.__offset, offset)
    
    def bits(self):
        '''
        Return a series of bits (encoded as booleans) that contain the contents.
        '''
        return BitIterator(self.__bytes, self.__length, self.__offset)

    def __str__(self):
        '''
        For 64 bits or less, show bits grouped by byte (octet), with bytes
        running from left to right and bits running from right to left within
        a byte.  This is the "usual" way of displaying bits, but means that
        reading literally from left to right does *not* give the bit sequence.
        
        For more than 64 bits, give a hex encoding of bytes (right padded
        with zeros).
        
        In both cases, the length in bits is given after a trailing slash.
        '''
        if self.__length > 64:
            hx = ''.join(hex(x)[2:] for x in self.__bytes)
            return '{0}x0/{1}'.format(hx, self.__length)
        else:
            chars = []
            byte = []
            count = 0
            for bit in self.bits():
                if not count % 8:
                    chars.extend(reversed(byte))
                    byte = []
                    if count:
                        chars.append(' ')
                if bit.zero():
                    byte.append('0')
                else:
                    byte.append('1')
                count += 1
            chars.extend(reversed(byte))
            return '{0}/{1}'.format(''.join(chars), self.__length)
    
    def __repr__(self):
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
        if self.__offset == offset:
            return self.__bytes
        else:
            return bytes(self.bytes(offset))
    
    def to_int(self, big_endian=False):
        i = 0
        value = self.__bytes
        if not big_endian:
            value = reversed(value)
        for b in value:
            i <<= 8
            i += b
        return i
    
    def to_str(self, encoding=None, errors='strict'):
        if encoding:
            return self.__bytes.decode(encoding=encoding, errors=errors)
        else:
            return self.__bytes.decode(errors=errors)

    @staticmethod
    def from_byte(value):
        return BitString.from_int_length(value, 8)
    
    @staticmethod
    def from_int32(value):
        return BitString.from_int_length(value, 32)
    
    @staticmethod
    def from_int64(value):
        return BitString.from_int_length(value, 64)
    
    @staticmethod
    def from_bit(value):
        if isinstance(value, bool):
            value = 1 if value else 0
        return BitString.from_int(value, 1)
            
    @staticmethod
    def from_extended_int(value):
        '''
        An extended int is a string that has a leading or trailing base tag
        (0b, 0o, 0x).  The position of the tag indicates byte endianness 
        (leading is little, back big).  The number of characters indicates 
        length.  Because we must define a contiguous set of bits, little
        endian values must specify a whole number of bytes.
        '''
        if not isinstance(value, str):
            raise TypeError('Extended int must be a string: {0!r}'.format(value))
        value = value.strip()
        # don't include decimal as doesn't naturally imply a bit length
        bigendian, format = None, {'b': (2, 1), 'o': (8, 3), 'x': (16, 4)}
        if is_bigendian(value):
            (base, bits) = format.get(value[-2].lower(), (None, None))
            iv, bigendian = extended_int(value), True
        elif value.startswith('0') and not value[1].isdigit():
            (base, bits) = format.get(value[1].lower(), (None, None))
            iv, bigendian = extended_int(value), False
        if bigendian is None:
            raise ValueError('No base tag: {0!r}'.format(value))
        if not base:
            raise ValueError('Base unsupported for inferred length: {0!r}'
                             .format(value)) 
        length = bits * (len(value) - 2)
        if length % 8 and not bigendian:
            raise ValueError('A little-endian extended int with a length '
                             'that is not an integer number of bytes cannot '
                             'be encoded as a stream of bits: {0!r}/{1!r}'
                             .format(value,  length))
        a = []
        for i in range(bytes_for_bits(length)):
            print('iv', iv)
            a.append(iv & 0xff)
            iv >>= 8
        if length % 8:
            a[-1] <<= 8 - length % 8
        print('a', a, 8 - length % 8)
        if not a:
            a = [0]
        if bigendian:
            b = bytes(reversed(a))
        else:
            b = bytes(a)
        print('b', b)
        return BitString(b, length, 8 - length % 8 if length % 8 else 0)
        
    @staticmethod
    def from_int_length(value, length):
        '''
        This can be an int, or a string with a leading or trailing tag.
        A plain int, or no tag, is byte little-endian.  Because we must define 
        a contiguous set of bits, little endian values must specify a whole 
        number of bytes.
        '''
        length = unpack_length(length)
        bigendian = is_bigendian(value)
        if length % 8 and not bigendian:
            raise ValueError('A little-endian int with a length that '
                             'is not an integer number of bytes cannot be '
                             'encoded as a stream of bits: {0!r}/{1!r}'
                             .format(value,  length))
        a, v = bytearray(), extended_int(value)
        for i in range(bytes_for_bits(length)):
            a.append(v & 0xff)
            v >>= 8
        if v > 0:
            raise ValueError('Value contains more bits than length: %r/%r' % 
                             (value, length))
        if bigendian:
            a = reversed(a)
        return BitString(bytes(a), length)
        
    @staticmethod
    def from_sequence(value, unpack):
        '''
        Unpack is called for each item in turn (so should be, say, from_byte).
        '''
        accumulator = BitString()
        for item in value:
            accumulator += unpack(item)
        return accumulator
            
    @staticmethod
    def from_bytes(value):
        if not isinstance(value, bytes):
            value = bytes(value)
        return BitString(value, len(value) * 8)
            
    @staticmethod
    def from_str(value, encoding=None, errors='strict'):
        if encoding:
            return BitString.from_bytes(value.encode(encoding=encoding, errors=errors))
        else:
            return BitString.from_bytes(value.encode(errors=errors))


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


def is_bigendian(value):
    '''
    Test for a big-endian format integer (trailing base tag).
    '''
    if isinstance(value, str):
        value = value.strip()
        return value.endswith('0') and len(value) > 2 and not value[-2].isdigit()
    else:
        return False


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


def bytes_for_bits(bits, offset=0):
    '''
    The number of bytes required to specify the given number of bits.
    '''
    return (bits + 7 + offset) // 8


def pad_bytes(value, length):
    '''
    Make sure value has sufficient bytes for length bits (and clone).
    '''
    if len(value) * 8 < length:
        v = bytearray(value)
        # is this documented anywhere - it inserts zeroes
        v[0:0] = length - 8 * bytes_for_bits(len(v))
        return bytes(v[0:bytes_for_bits(length)])
    else:
        return bytes(value[0:bytes_for_bits(length)])


class BitIterator(object):
    
    def __init__(self, value, length, offset):
        assert 0 <= offset < 8
        self.__bytes = value
        self.__length = length + offset
        self.__offset = offset
        
    def __iter__(self):
        return self
    
    def __next__(self):
        print('offset', self.__offset)
        if self.__offset < self.__length:
            b = self.__bytes[self.__offset // 8]
            print('b1', b)
            b >>= self.__offset % 8
            print('b2', b)
            self.__offset += 1
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
            if self.__index < 0 and self.__bytes:
                # initial offset chunk
                b = 0xff & (self.__bytes[0] << (self.__required - self.__existing))
                self.__index += 1
                return b
            else:
                if self.__index < len(self.__bytes):
                    b = 0xff & (self.__bytes[self.__index] >> (8 - self.__required + self.__existing))
                    self.__index += 1
                else:
                    raise StopIteration()
                if self.__index < len(self.__bytes):
                    b |= 0xff & (self.__bytes[self.__index] << (self.__required - self.__existing))
                return b
        else:
            # need to correct for additional offset
            if self.__index < len(self.__bytes):
                b = 0xff & (self.__bytes[self.__index] >> (self.__existing - self.__required))
                print('from first byte', b, self.__bytes[self.__index], self.__existing, self.__required)
                self.__index += 1
            else:
                raise StopIteration()
            if self.__index < len(self.__bytes):
                b |= 0xff & (self.__bytes[self.__index] << (8 - self.__existing + self.__required))
                print('from second', b)
            return b


ONE = BitString(b'\x01', 1)
ZERO = BitString(b'\x00', 1)

