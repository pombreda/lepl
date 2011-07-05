#LICENCE


from unittest import TestCase

from lepl.rxpy.engine.support import StreamTargetMixin
from lepl.stream.factory import DEFAULT_STREAM_FACTORY


class StreamTargetTest(TestCase):

    def new_target(self, text, offset, previous=None):
        stream = DEFAULT_STREAM_FACTORY.from_string(text)
        target = StreamTargetMixin()
        target._reset(offset, stream, previous)
        return target

    def assert_target(self, target, offset, previous, current, final,
                      excess=None):
        assert target._offset == offset, target._offset
        assert target._previous == previous, target._previous
        assert target._current == current, target._current
        assert target._final == final, target._final
        if excess is not None:
            assert target._excess == excess, target._excess

    def test_empty(self):

        target = self.new_target('', 0)
        self.assert_target(target, 0, None, None, False, 1)
        target._advance(1)
        self.assert_target(target, 1, None, None, False, 2)

        target = self.new_target('', 1)
        self.assert_target(target, 1, None, None, False, 1)
        target._advance(2)
        self.assert_target(target, 3, None, None, False, 3)

        target = self.new_target('', 0, previous='x')
        self.assert_target(target, 0, 'x', None, False, 1)
        target._advance(1)
        self.assert_target(target, 1, None, None, False, 2)

    def test_char(self):

        target = self.new_target('x', 0)
        self.assert_target(target, 0, None, 'x', True)
        target._advance(1)
        self.assert_target(target, 1, 'x', None, False, 1)
        target._advance(1)
        self.assert_target(target, 2, None, None, False, 2)

        target = self.new_target('x', 1)
        self.assert_target(target, 1, None, 'x', True, 0)
        target._advance(2)
        self.assert_target(target, 3, None, None, False, 2)

        target = self.new_target('x', 0, previous='y')
        self.assert_target(target, 0, 'y', 'x', True, 0)
        target._advance(1)
        self.assert_target(target, 1, 'x', None, False, 1)
        target._advance(1)
        self.assert_target(target, 2, None, None, False, 2)

    def test_string(self):

        target = self.new_target('xz', 0)
        self.assert_target(target, 0, None, 'x', False, 0)
        target._advance(1)
        self.assert_target(target, 1, 'x', 'z', True, 0)
        target._advance(1)
        self.assert_target(target, 2, 'z', None, False, 1)

        target = self.new_target('xz', 1)
        self.assert_target(target, 1, None, 'x', False, 0)
        target._advance(2)
        self.assert_target(target, 3, 'z', None, False, 1)

        target = self.new_target('xz', 0, previous='y')
        self.assert_target(target, 0, 'y', 'x', False, 0)
        target._advance(1)
        self.assert_target(target, 1, 'x', 'z', True, 0)
        target._advance(1)
        self.assert_target(target, 2, 'z', None, False, 1)
        target._advance(1)
        self.assert_target(target, 3, None, None, False, 2)

        target = self.new_target('xz', 0, previous='y')
        self.assert_target(target, 0, 'y', 'x', False, 0)
        target._advance(2)
        self.assert_target(target, 2, 'z', None, False, 1)
        target._advance(1)
        self.assert_target(target, 3, None, None, False, 2)

        target = self.new_target('xz', 0, previous='y')
        self.assert_target(target, 0, 'y', 'x', False, 0)
        target._advance(3)
        self.assert_target(target, 3, None, None, False, 2)

