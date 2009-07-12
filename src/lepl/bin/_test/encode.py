
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
Tests for the lepl.bin.encode module.
'''

if bytes is str:
    print('Binary parsing unsupported in this Python version')
else:

    from unittest import TestCase
    
    from lepl.bin.bits import BitString
    from lepl.bin.encode import dispatch_table, simple_serialiser
    from lepl.bin.literal import parse
    
    
    # pylint: disable-msg=C0103, C0111, C0301
    # (dude this is just a test)

    
    class EncodeTest(TestCase):
        '''
        Test whether we correctly encode
        '''
        
        def test_encode(self):
            mac = parse('''
    Frame(
      Header(
        preamble  = 0b10101010*7,
        start     = 0b10101011,
        destn     = 010203040506x0,
        source    = 0708090a0b0cx0,
        ethertype = 0800x0
      ),
      Data(1/8,2/8,3/8,4/8),
      CRC(234d0/4.)
    )
    ''')
        
            serial = simple_serialiser(mac, dispatch_table())
            bs = serial.bytes()
            for _index in range(7):
                b = next(bs)
                assert b == BitString.from_int('0b10101010').to_int(), b
            b = next(bs)
            assert b == BitString.from_int('0b10101011').to_int(), b
            