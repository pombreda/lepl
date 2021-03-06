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

    # TODO - use decorator to apply
    '''
    pass


(I, M, S, U, X, A, _L, _C, _E, _U, _G ,_B) = map(lambda x: 2**x, range(12))
(IGNORECASE, MULTILINE, DOT_ALL, UNICODE, VERBOSE, ASCII,
 _LOOP_UNROLL, _CHARS, _EMPTY, _UNSAFE, _GROUPS, _LOOKBACK) = \
    (I, M, S, U, X, A, _L, _C, _E, _U, _G, _B)
_FLAGS = (I, M, S, U, X, A, _L, _C, _E, _U, _G, _B,
          IGNORECASE, MULTILINE, DOT_ALL, UNICODE, VERBOSE, ASCII,
          _LOOP_UNROLL, _CHARS, _EMPTY, _UNSAFE, _GROUPS, _LOOKBACK)

FLAG_NAMES = {I: 'I/IGNORECASE',
              M: 'M/MULTILINE',
              S: 'S/DOT_ALL',
              U: 'U/UNICODE',
              X: 'X/VERBOSE',
              A: 'A/ASCII',
              _L: '_L/_LOOP_UNROLL',
              _C: '_C/_CHARS',
              _E: '_E/_EMPTY',
              _U: '_U/_UNSAFE',
              _G: '_G/_GROUPS',
              _B: '_B/_LOOKBACK'}


def refuse_flags(flags):
    '''
    Raise an error for the flags given.
    '''
    names = [FLAG_NAMES[key] for key in FLAG_NAMES if key & flags]
    if names:
        raise RxpyError('Bad flag' + ('s' if len(names) > 1 else '')
                         + ': ' + '; '.join(names))


