#LICENCE


from unittest import TestCase
from lepl.rxpy.parser.support import GroupState
from lepl.rxpy.support import RxpyError


class GroupStateTest(TestCase):
    
    def test_basic(self):
        state = GroupState()
        assert 1 == state.new_index()
        assert 2 == state.new_index()
        assert 2 == state.count
        
    def test_alias(self):
        state = GroupState()
        assert 1 == state.new_index()
        assert 1 == state.new_index(name='1', extended=True)
        assert 1 == state.count
        try:
            state.new_index(name='1', extended=False)
            assert False, 'expected error'
        except RxpyError:
            pass
    
    def test_non_contiguous(self):
        state = GroupState()
        assert 1 == state.new_index()
        assert 7 == state.new_index(name='7', extended=True)
        assert 2 == state.count
        try:
            state.new_index(name='8', extended=False)
            assert False, 'expected error'
        except RxpyError:
            pass
        assert 2 == state.new_index()
        assert 3 == state.count
    
    def test_names(self):
        state = GroupState()
        assert 1 == state.new_index()
        assert 2 == state.new_index(name='bob')
        assert 2 == state.count
        try:
            assert 2 == state.new_index(name='bob')
            assert False, 'expected error'
        except RxpyError:
            pass
        assert 2 == state.count
        assert 2 == state.new_index(name='bob', extended=True)
        assert 2 == state.count
