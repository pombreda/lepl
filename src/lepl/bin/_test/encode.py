
if bytes is str:
    print('Binary parsing unsupported in this Python version')
else:

    from unittest import TestCase
    
    from lepl.bin.bits import BitString
    from lepl.bin.encode import dispatch_table, simple_serialiser
    from lepl.bin.literal import parse
    from lepl.node import Node
    
    
    
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
            for i in range(7):
                b = next(bs)
                assert b == BitString.from_int('0b10101010').to_int(), b
            b = next(bs)
            assert b == BitString.from_int('0b10101011').to_int(), b
            