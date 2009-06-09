
from unittest import TestCase

from lepl.bin.bits import BitString
from lepl.bin.literal import parse
from lepl.bin.matchers import BEnd, Const
from lepl.node import Node


class MatcherTest(TestCase):
    '''
    Test whether we correctly match some data.
    '''
    mac = parse('''
Frame(
  Header(
    preamble  = 0b10101010*7,
    start     = 0b10101011,
    destn     = 123456x0,
    source    = 890abcx0,
    ethertype = 0800x0
  ),
  Data(1/8,2/8,3/8,4/8),
  CRC(234d0/4.)
)
''')
    
    preamble  = ~Const('0b10101010')[7]
    start     = ~Const('0b10101011')
    destn     = BEnd(6.0)
    source    = BEnd(6.0)
    ethertype = ~Const('0800x0') 
    header    = preamble & start & destn & source & ethertype
    
    print(mac)
    b = ...
    print(header.parse(b))
    