
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
    preamble  = [10101010b0]*7,
    start     = 10101011b0,
    destn     = 123456x0,
    source    = 890abcx0,
    ethertype = 0800x0
  ),
  Data([1,2,3,4]),
  CRC(234d0/4.)
)
''')
        print(b)