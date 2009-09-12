

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *
from lepl.offside.config import OffsideConfiguration
from lepl.lexer.matchers import LexerError

class PithonTest(TestCase):
    
    @property
    def parser(self):
        
        word = Token(Word(Lower()))
        continuation = Token(r'\\')
        symbol = Token(Any('()'))
        introduce = ~Token(':')
        comma = ~Token(',')
        
        CLine = CLineFactory(continuation)
        
        statement = word[1:]
        args = Extend(word[:, comma]) > tuple
        function = word[1:] & ~symbol('(') & args & ~symbol(')')

        block = Delayed()
        line = (CLine(statement) | block | Line(Empty())) > list
        block += CLine((function | statement) & introduce) & Block(line[1:])
        
        program = (line[:] & Eos())
        return program.string_parser(
                    OffsideConfiguration(policy=2,
                                         monitors=[TraceResults(True)]))
    
    def test_blocks(self):
        #basicConfig(level=DEBUG)
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
                          ['kopo', 'fjire', 'ifejfr'], 
                          ['ogptkr', 'jgitr', 'gtr'], 
                          ['ffjireofr', ('kfkorp', 'freopk'), 
                           ['jifr', 'fireo'], 
                           ['frefre', 'jifoji'], 
                           ['jio', 'frefre',
                            ['jiforejifre', 'fiorej'], 
                            ['jfore', 'fire'], 
                            ['jioj']], 
                           ['jioj']], 
                          ['jiojio']], result
        
    def test_no_lexer(self):
        #basicConfig(level=DEBUG)
        try:
            print(self.parser('123'))
            assert False, 'expected exception'
        except LexerError as error:
            assert str(error) == 'No lexer for \'123\' at ' \
                'line 1 character 0 of str: \'123\'.', str(error)
                
    def test_extend(self):
        #basicConfig(level=DEBUG)
        result = self.parser('''
def foo(abc, def,
        ghi):
  jgiog
''')
        assert result == [[], 
                          ['def', 'foo', ('abc', 'def', 'ghi'), 
                           ['jgiog']]], result
        
