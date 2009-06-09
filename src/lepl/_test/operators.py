
'''
Test for thread safety.
'''

from operator import add

from logging import basicConfig, INFO, DEBUG
from threading import Thread
from unittest import TestCase

from lepl import *


class ThreadTest(TestCase):
    
    def test_safety(self):
        basicConfig(level=DEBUG)
        matcher3 = Delayed()
        matcher4 = Delayed()
        matcher1 = Any()[::'b',...] & Eos()
        with Separator(Drop(Any('a')[:])):
            matcher2 = Any()[::'b',...] & Eos()
            def target(matcher3=matcher3, matcher4=matcher4):
                matcher3 += Any()[::'b',...] & Eos()
                with Separator(Drop(Any('b')[:])):
                    matcher4 += Any()[::'b',...] & Eos()
            t = Thread(target=target)
            t.start()
            t.join()
            matcher5 = Any()[::'b',...] & Eos()
        matcher6 = Any()[::'b',...] & Eos()
        text = 'cababab'
        assert text == matcher1.parse_string(text)[0], matcher1.parse_string(text)
        assert 'cbbb' == matcher2.parse_string(text)[0], matcher2.parse_string(text)
        assert text == matcher3.parse_string(text)[0], matcher3.parse_string(text)
        assert 'caaa' == matcher4.parse_string(text)[0], matcher4.parse_string(text)
        assert 'cbbb' == matcher5.parse_string(text)[0], matcher5.parse_string(text)
        assert text == matcher6.parse_string(text)[0], matcher6.parse_string(text)


class SpaceTest(TestCase):
    
    def word(self):
        return Literal("a") & Literal("bc")[1:,...]

    def test_spaces(self):
        with Separator(~Space()):
            s1 = self.word()[1:].string_parser()
            assert not s1("abc"), s1('abc')
            assert s1("a bc")
            with Separator(None):
                s2 = self.word()[1:].string_parser()
                assert s2("abc")
                assert not s2("a bc")
