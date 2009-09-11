

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *
from lepl.offside.config import OffsideConfiguration

class PithonTest(TestCase):
    
    @property
    def parser(self):
        
        word = Token(Word(Lower()))
        continuation = Token(r'\\')
        symbol = Token(Any('()'))
        introduce = Token(':')
        comma = Token(',')
        
        CLine = CLineFactory(continuation)
        
        statement = word[1:]
        args = Extend(word[:, comma]) > tuple
        function = word[1:] & ~symbol('(') & args & ~symbol(')')

        block = Delayed()
        line = (CLine(statement) | block | Line(Empty())) > list
        block += CLine((function | statement) & ~introduce) & Block(line[1:])
        
        program = (line[:] & Eos())
        return program.string_parser(
                    OffsideConfiguration(policy=2,
                                         monitors=[TraceResults(True)]))
    
    def test_blocks(self):
        basicConfig(level=DEBUG)
        program1 = '''
kopo fjire ifejfr
ogptkr jgitr gtr
ffjireofr(kfkorp, freopk):
  jifr fireo
  frefre jifoji
  jio frefre:
    jiforejifre fiorej
    jfore fire
    jioj
  jioj
jiojio
'''
        result = self.parser(program1)
        assert result == [[], 
                          [u'kopo', u'fjire', u'ifejfr'], 
                          [u'ogptkr', u'jgitr', u'gtr'], 
                          [u'ffjireofr', (u'kfkorp', u',', u'freopk'), 
                           [u'jifr', u'fireo'], 
                           [u'frefre', u'jifoji'], 
                           [u'jio', u'frefre',
                            [u'jiforejifre', u'fiorej'], 
                            [u'jfore', u'fire'], 
                            [u'jioj']], 
                           [u'jioj']], 
                          [u'jiojio']], result
        