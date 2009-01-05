

def assert_type(name, value, type, none_ok=False):
    '''
    If the value is not of the given type, raise a syntax error.
    '''
    if none_ok and value == None: return
    if isinstance(value, type): return
    raise TypeError('{0} (value {1}) must be of type {2}.'
                    .format(name, repr(value), type.__name__))

