#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.base import BaseTest
from lepl.rxpy.engine.lexer.engine import LexerEngine


class LexerTest(BaseTest, TestCase):

    def default_engine(self):
        return LexerEngine

    def test_unique_group(self):
        self.assert_groups('^(?:(a)|(b)|(c))', 'a', {0: ('a', 0, 1), 1: ('a', 0, 1)})
        self.assert_groups('^(?:(a)|(b)|(c))', 'b', {0: ('b', 0, 1), 2: ('b', 0, 1)})
        self.assert_groups('^(?:(a)|(b)|(c))', 'c', {0: ('c', 0, 1), 3: ('c', 0, 1)})

    def test_duplicate_group(self):
        self.assert_groups('^(?:(a)|(a)|(a))', 'a', {0: ('a', 0, 1), 1: ('a', 0, 1)})
        self.assert_groups('^(?:(a)|(b)|(b))', 'b', {0: ('b', 0, 1), 2: ('b', 0, 1)})
        self.assert_groups('^(?:(c)|(b)|(c))', 'c', {0: ('c', 0, 1), 1: ('c', 0, 1)})

    def test_length(self):
        self.assert_groups('^(?:(a)|(aa)|(aaa))', 'a', {0: ('a', 0, 1), 1: ('a', 0, 1)})
        self.assert_groups('^(?:(aaa)|(aa)|(a))', 'aaa', {0: ('aaa', 0, 3), 1: ('aaa', 0, 3)})

