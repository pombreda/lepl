
from lepl.bin.literal import parse
from lepl._example.support import Example


class ParseExample(Example):
    
    def test_parse(self):
        '''
        An 803.3 MAC frame - see http://en.wikipedia.org/wiki/Ethernet
        '''
        b = parse('''
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
        print(b)