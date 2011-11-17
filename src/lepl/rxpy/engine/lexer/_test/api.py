#LICENCE


from unittest import TestCase

from lepl.rxpy.engine._test.api import ReTest
from lepl.rxpy.engine.lexer.engine import LexerEngine


class LexerReTest(ReTest, TestCase):
    
    def default_engine(self):
        return LexerEngine

    def test_zero(self):
        pass
    
    def test_numbered(self):
        pass
    
    def test_split_from_docs(self):
        pass
    
    def test_match(self):
        pass
    
    def test_findall(self):
        pass

    # search

    def test_end_of_line(self):
        pass
    
    def test_find_from_docs(self):
        pass

    def test_findall_empty(self):
        pass

    def test_findall_sub(self):
        pass

    def test_search(self):
        pass
    