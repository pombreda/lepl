
# LICENCE

from __future__ import print_function
from lepl._test.base import BaseTest
from lepl.lexer.matchers import Token
from lepl.support.lib import str
from tempfile import TemporaryFile


class FileTest(BaseTest):
    
    def test_file(self):
        f = TemporaryFile('w+', encoding='utf8')
        print("hello world\n", file=f)
        f.flush()
#        f.seek(0)
#        print(f.readlines())
        f.seek(0)
        w = Token('[a-z]+')
        s = Token(' +')
        v = w & s & w
        v.parse_iterable(f)
        
#    def test_default(self):
#        w = Token('[a-z]+')
#        s = Token(' +')
#        v = w & s & w
#        v.parse_string("hello world\n")
        
        
        
    