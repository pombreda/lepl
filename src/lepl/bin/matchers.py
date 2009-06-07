
from lepl.bin.bits import unpack_length, BitString, STRICT
from lepl.matchers import OperatorMatcher, Transformable
from lepl.parser import tagged


class _Constant(Transformable):

    def __init__(self, value):
        '''
        Match a given bit string.
        
        This is typically not used directly, but via the functions below
        (which specify a value as integer, bytes, etc).
        '''
        super(_Constant, self).__init__()
        self._arg(value=value)
        
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).

        Need to be careful here to use only the restricted functionality
        provided by the stream interface.
        '''
        try:
            if self.value == stream[0:len(self.value)]:
                yield self.function([self.value], stream, stream[len(self.value):])
        except IndexError:
            pass
        
        
class _Variable(Transformable):
    
    def __init__(self, length):
        '''
        Match a given number of bits.
        '''
        super(_Variable, self).__init__()
        self._arg(length=unpack_length(length))
        
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).

        Need to be careful here to use only the restricted functionality
        provided by the stream interface.
        '''
        try:
            yield self.function([self._convert(stream[0:length])], stream, 
                                stream[length:])
        except IndexError:
            pass

    def _convert(self, bits):
        return bits
    
    
class _Bytes(_Variable):
    '''
    Match a given number of bytes.
    '''
    
    def __init__(self, length):
        '''
        Match a given number of bytes.
        '''
        if not isinstance(length, int):
            raise TypeError('Number of bytes must be an integer')
        super(_Bytes, self).__init__(length)
    
    def _convert(self, bits):
        return bits.to_bytes()
    

class BEnd(_Variable):
    '''
    Convert a given number of bits (multiple of 8) to a big-endian number.
    '''
    
    def __init__(self, length):
        '''
        Match a given number of bits, converting them to a big-endian int.
        '''
        length = unpack_length(length)
        if length % 8:
            raise ValueError('Big endian int must a length that is a multiple of 8.')
        super(_BigEndian, self).__init__(length)
    
    def _convert(self, bits):
        return bits.to_int(big_endian=True)
    

class LEnd(_Variable):
    '''
    Convert a given number of bits to a little-endian number.
    '''
    
    def _convert(self, bits):
        return bits.to_int()
    

def Bits(value):
    '''
    Match or read a bit string (to read a value, give the number of bits).
    '''
    if isinstance(value, int):
        return _Variable(value)
    else:
        return _Constant(value)
    
    
def Byte(value=None):
    '''
    Match or read a byte (if a value is given, it must match).
    '''
    if value is None:
        return BEnd(8)
    else:
        return _Constant(BitString.from_byte(value))


def Bytes(value):
    '''
    Match or read an array of bytes (to read a value, give the number of bytes).
    '''
    if isinstance(value, int):
        return _Bytes(value)
    else:
        return _Constant(BitString.from_bytes(value))
    
    
def _bint(length):
    '''
    Factory method for big-endian values. 
    '''
    def matcher(value=None):
        if value is None:
            return BEnd(length)
        else:
            return _Constant(BitString.from_int(value, length=length, big_endian=True))

def _lint(length):
    '''
    Factory method for little-endian values. 
    '''
    def matcher(value=None):
        if value is None:
            return LEnd(length)
        else:
            return _Constant(BitString.from_int(value, length=length, big_endian=False))


BInt16 = _bint(16)
'''
Match or read an 16-bit big-endian integer (if a value is given, it must match).
'''

LInt16 = _lint(16)
'''
Match or read an 16-bit little-endian integer (if a value is given, it must match).
'''

BInt32 = _bint(32)
'''
Match or read an 32-bit big-endian integer (if a value is given, it must match).
'''

LInt32 = _lint(32)
'''
Match or read an 32-bit little-endian integer (if a value is given, it must match).
'''

BInt64 = _bint(64)
'''
Match or read an 64-bit big-endian integer (if a value is given, it must match).
'''

LInt64 = _lint(64)
'''
Match or read an 64-bit little-endian integer (if a value is given, it must match).
'''


class _String(_Bytes):
    
    def __init__(self, length, encoding=None, errors=STRICT):
        super(_String, self).__init__(length)
        self._arg(encoding=encoding)
        self._arg(errors=errors)
    
    def _convert(self, bits):
        return bits.to_str(encoding=self.encoding, errors=self.errors)
    
    
def String(value, encoding=None, errors=STRICT):
    '''
    Match or read a string (to read a value, give the number of bytes).
    '''
    if isinstance(value, int):
        return _String(value, encoding=encoding, errors=errors)
    else:
        return _Constant(BitString.from_str(value, encoding=encoding, errors=errors))

