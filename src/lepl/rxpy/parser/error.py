#LICENCE


from lepl.rxpy.support import RxpyError


class ParseError(RxpyError):
    '''
    Identify the location of errors.
    '''

    def __init__(self, title, explanation):
        super(ParseError, self).__init__(title)
        self.title = title
        self.explanation = explanation

    def update(self, pattern, offset):
        if offset > 30:
            pattern = '...' + pattern[offset-33:]
            spaces = 30
        else:
            spaces = offset
        padding = spaces * ' '
        self.pattern = pattern
        self.offset = offset
        self.args = (
'''%s

  %s
  %s^
%s''' % (self.title, pattern, padding, self.explanation),)

    def __str__(self):
        try:
            return self.args[0]
        except IndexError:
            return self.title


class EmptyError(ParseError):
    '''
    Indicate that an empty expression is being repeated.  This is caught and
    converted into an EmptyError.
    '''

    def __init__(self):
        super(EmptyError, self).__init__('Repeated empty match.', '''
A sub-pattern that may match the empty string is being repeated.  This usually
indicates an error since an empty match can repeat indefinitely.

If you are sure that the pattern is correct then compile using the _EMPTY
flag to suppress this error; the engine will then match the empty string at
most once.

You can also suppress the "at most once" limitation with the _UNSAFE flag, but
this may result in a match that does not terminate.''')


class SimpleGroupError(ParseError):
    '''
    Indicate that group naming conventions have been broken.
    '''

    def __init__(self, title):
        super(SimpleGroupError, self).__init__(title, '''
By default, RXPY only allows simple, unaliased group names.  This reflects
normal Python standards and the pattern probably contains an error.

If you are sure that the pattern is correct then compile using the _GROUPS
flag to suppress this error; the engine will then allow groups to be reused
and for group indices to be non-contiguous.''')
