

from logging import basicConfig, DEBUG, INFO
from unittest import TestCase

from lepl.custom import read, write


class ReadWriteTest(TestCase):

    def test_one_thread(self):
        write('foo', 'bar')
        assert 'bar' == read('foo')
        