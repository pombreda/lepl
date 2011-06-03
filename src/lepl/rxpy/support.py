#LICENCE

'''
Support classes for the RXPY library.
'''


class RxpyError(Exception):
    '''
    Common base class for errors raised by the RXPY code.
    '''
    pass


class UnsupportedOperation(RxpyError):
    '''
    Raised by an interface when called in error.
    '''
    pass


(I, M, S, U, X, A, _L, _C, _E, _U, _G) = map(lambda x: 2**x, range(11))
(IGNORE_CASE, MULTILINE, DOT_ALL, UNICODE, VERBOSE, ASCII, _LOOP_UNROLL, _CHARS, _EMPTY, _UNSAFE, _GROUPS) = (I, M, S, U, X, A, _L, _C, _E, _U, _G)
_FLAGS = (I, M, S, U, X, A, _L, _C, _E, _U, _G, IGNORE_CASE, MULTILINE, DOT_ALL, UNICODE, VERBOSE, ASCII, _LOOP_UNROLL, _CHARS, _EMPTY, _UNSAFE, _GROUPS)

FLAG_NAMES = {I: 'I/IGNORECASE',
              M: 'M/MULTILINE',
              S: 'S/DOTALL',
              U: 'U/UNICODE',
              X: 'X/VERBOSE',
              A: 'A/ASCII',
              _L: '_L/_LOOP_UNROLL',
              _C: '_C/_CHARS',
              _E: '_E/_EMPTY',
              _U: '_U/_UNSAFE',
              _G: '_G/_GROUPS'}
