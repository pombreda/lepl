
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
Matchers specifically for binary data (most LEPL matchers can be used with
binary data, but additional support is needed when the matching involves a 
literal comparison or generation of a binary result). 
'''

if bytes is str:
    print('Binary parsing unsupported in this Python version')
else:

    from lepl.bin.bits import unpack_length, BitString, STRICT
    from lepl.matchers import OperatorMatcher
    from lepl.parser import tagged
    
    
    # pylint: disable-msg=C0103, R0901, R0904
    # lepl conventions
    # pylint: disable-msg=R0201
    # (allow over-riding in sub-classes)
    
    class _Constant(OperatorMatcher):
        '''
        Support class for matching constant values.
        '''
    
        # pylint: disable-msg=E1101
        # (using _arg to set attributes dynamically)
        
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
                    yield ([self.value], stream[len(self.value):])
            except IndexError:
                pass
            
            
    class Const(_Constant):
        '''
        Match a given value, which is parsed as for `BitString.from_int`.
        '''
    
        def __init__(self, value, length=None):
            if not isinstance(value, BitString):
                value = BitString.from_int(value, length)
            super(Const, self).__init__(value)
            
            
    class _Variable(OperatorMatcher):
        '''
        Support class for matching a given number of bits.
        '''
        
        # pylint: disable-msg=E1101
        # (using _arg to set attributes dynamically)

        def __init__(self, length):
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
                yield ([self._convert(stream[0:self.length])], 
                       stream[self.length:])
            except IndexError:
                pass
    
        def _convert(self, bits):
            '''
            By default, just return the bits.
            '''
            return bits
        
        
    class _ByteArray(_Variable):
        '''
        Support class for matching a given number of bytes.
        '''
        
        def __init__(self, length):
            '''
            Match a given number of bytes.
            '''
            if not isinstance(length, int):
                raise TypeError('Number of bytes must be an integer')
            super(_ByteArray, self).__init__(length)
        
        def _convert(self, bits):
            '''
            Convert from bits to bytes,
            '''
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
                raise ValueError('Big endian int must a length that is a '
                                 'multiple of 8.')
            super(BEnd, self).__init__(length)
        
        def _convert(self, bits):
            '''
            Convert to int.
            '''
            return bits.to_int(big_endian=True)
        
    
    class LEnd(_Variable):
        '''
        Convert a given number of bits to a little-endian number.
        '''
        
        def _convert(self, bits):
            '''
            Convert to int.
            '''
            return bits.to_int()
        
    
    def BitStr(value):
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
    
    
    def ByteArray(value):
        '''
        Match or read an array of bytes (to read a value, give the number 
        of bytes).
        '''
        if isinstance(value, int):
            return _ByteArray(value)
        else:
            return _Constant(BitString.from_bytearray(value))
        
        
    def _bint(length):
        '''
        Factory method for big-endian values. 
        '''
        def matcher(value=None):
            '''
            Generate the matcher, given a value.
            '''
            if value is None:
                return BEnd(length)
            else:
                return _Constant(BitString.from_int(value, length=length, 
                                                    big_endian=True))
        return matcher
    
    def _lint(length):
        '''
        Factory method for little-endian values. 
        '''
        def matcher(value=None):
            '''
            Generate the matcher, given a value.
            '''
            if value is None:
                return LEnd(length)
            else:
                return _Constant(BitString.from_int(value, length=length, 
                                                    big_endian=False))
        return matcher
    
    
    # pylint: disable-msg=W0105
    
    BInt16 = _bint(16)
    '''
    Match or read an 16-bit big-endian integer (if a value is given, it 
    must match).
    '''
    
    LInt16 = _lint(16)
    '''
    Match or read an 16-bit little-endian integer (if a value is given, it 
    must match).
    '''
    
    BInt32 = _bint(32)
    '''
    Match or read an 32-bit big-endian integer (if a value is given, it 
    must match).
    '''
    
    LInt32 = _lint(32)
    '''
    Match or read an 32-bit little-endian integer (if a value is given, it 
    must match).
    '''
    
    BInt64 = _bint(64)
    '''
    Match or read an 64-bit big-endian integer (if a value is given, it 
    must match).
    '''
    
    LInt64 = _lint(64)
    '''
    Match or read an 64-bit little-endian integer (if a value is given, it 
    must match).
    '''
    
    
    class _String(_ByteArray):
        '''
        Support class for reading a string.
        '''
        
        # pylint: disable-msg=E1101
        # (using _arg to set attributes dynamically)

        def __init__(self, length, encoding=None, errors=STRICT):
            super(_String, self).__init__(length)
            self._karg(encoding=encoding)
            self._karg(errors=errors)
        
        def _convert(self, bits):
            '''
            Convert to string.
            '''
            return bits.to_str(encoding=self.encoding, errors=self.errors)
        
        
    def String(value, encoding=None, errors=STRICT):
        '''
        Match or read a string (to read a value, give the number of bytes).
        '''
        if isinstance(value, int):
            return _String(value, encoding=encoding, errors=errors)
        else:
            return _Constant(BitString.from_str(value, encoding=encoding, 
                                                errors=errors))
    
