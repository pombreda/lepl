
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
Tests for the lepl.bin.matchers module.
'''

if bytes is str:
    print('Binary parsing unsupported in this Python version')
else:

    #from logging import basicConfig, DEBUG
    from unittest import TestCase
    
    from lepl.bin.encode import dispatch_table, simple_serialiser
    from lepl.bin.literal import parse
    from lepl.bin.matchers import BEnd, Const
    from lepl.node import Node
    
    
    # pylint: disable-msg=C0103, C0111, C0301
    # (dude this is just a test)
    
    class MatcherTest(TestCase):
        '''
        Test whether we correctly match some data.
        '''
        
        def test_match(self):
            #basicConfig(level=DEBUG)
            
            # first, define some test data - we'll use a simple definition
            # language, but you could also construct this directly in Python
            # (Frame, Header etc are auto-generated subclasses of Node). 
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
        
            # next, define a parser for the header structure
            # this is mainly literal values, but we make the two addresses
            # big-endian integers, which will be read from the data
            
            # this looks very like "normal" lepl because it is - there's 
            # nothing in lepl that forces the data being parsed to be text. 
            
            preamble  = ~Const('0b10101010')[7]
            start     = ~Const('0b10101011')
            destn     = BEnd(6.0)                > 'destn'
            source    = BEnd(6.0)                > 'source'
            ethertype = ~Const('0800x0') 
            header    = preamble & start & destn & source & ethertype > Node
            
            # so, what do the test data look like?
#            print(mac)
    # Frame
    #  +- Header
    #  |   +- preamble BitString(b'\xaa\xaa\xaa\xaa\xaa\xaa\xaa', 56, 0)
    #  |   +- start BitString(b'\xab', 8, 0)
    #  |   +- destn BitString(b'\x01\x02\x03\x04\x05\x06', 48, 0)
    #  |   +- source BitString(b'\x07\x08\t\n\x0b\x0c', 48, 0)
    #  |   `- ethertype BitString(b'\x08\x00', 16, 0)
    #  +- Data
    #  |   +- BitString(b'\x01', 8, 0)
    #  |   +- BitString(b'\x02', 8, 0)
    #  |   +- BitString(b'\x03', 8, 0)
    #  |   `- BitString(b'\x04', 8, 0)
    #  `- CRC
    #      `- BitString(b'\x00\x00\x00\xea', 32, 0)    
    
            # we can serialize that to a BitString        
            b = simple_serialiser(mac, dispatch_table())
            assert str(b) == 'aaaaaaaaaaaaaaab123456789abc801234000eax0/240'
    
            # and then we can parse it
            p = header.parse(b)[0]
#            print(p)
    # Node
    #  +- destn Int(1108152157446,48)
    #  `- source Int(7731092785932,48)
    
            # the destination address
            assert hex(p.destn[0]) == '0x10203040506'
    
            # the source address
            assert hex(p.source[0]) == '0x708090a0b0c'
