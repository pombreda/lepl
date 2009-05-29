
'''
Specify and construct binary structures.

This is necessary for tests and may be useful in its own right.  Note that it
is also quite easy to construct `Binary` nodes directly in Python.

The construction of binary values is a two-stage process.  First, we describe
a Python structure.  Then we encode that structure as a binary value.  As is
standard in this package, the Python construct consists of `Binary` nodes.

The description of values has the form:
  Binary(byte=0xff/8, array=[1,2,3]/2.4, 0x1234/2., Binary(...), (...))
  
In more detail:
  () is used for grouping, must exist outside the entire description, and
     defines a binary node.  If preceded by a name, then that is used to create 
     a subclass of Binary (unless it is "Binary", in which case it is the 
     default).  For now, repeated names are not validated in any way for 
     consistency.
  [] defines an array of bytes
  name=value/length is used for defining a value, in various ways:
    value anonymous value (byte or array)
    value/length anonymous value with specified length
    name=value named byte or array
    name=value/length named value with given length
'''

from lepl.bin.node import Binary


def make_binary_parser():
    
    # avoid import loops
    from lepl import Word, Letter, Digit, UnsignedFloat, UnsignedInteger, \
        Regexp, Drop, Separator, Delayed, Optional, Any
        
    classes = {}
    
    def named_class(name, *args):
        '''
        Given a name and some args, create an sub-class of Binary and 
        create an instance with the given content.
        '''
        if name not in classes:
            classes[name] = type(name, (Binary,), {})
        return classes[name](args)
    
    mult    = lambda l, n: l * int(n) 
        
    # swap and create a tuple 
    # (because the spec has value/length, but we store (length, value)
    stuple  = lambda ab: (ab[1], ab[0])
    
    # an attribute or class name
    name    = Word(Letter(), Letter() | Digit() | '_')

    # lengths can be integers (bits) or floats (bytes.bits)
    length  = UnsignedFloat()

    # a literal decimal - treated as a byte
    decimal = UnsignedInteger()

    # the letters used for binary, octal and hex values (eg the 'x' in 0xffee)
    b, o, x = Any('bB'), Any('oO'), Any('xX')

    # a binary number (without pre/postfix)
    binary  = Any('01')[1:]

    # an octal number (without pre/postfix)
    octal   = Any('01234567')[1:]

    # a hex number (without pre/postfix)
    hex     = Regexp('[a-fA-F0-9]')[1:]

    # little-endian literals have normal prefix syntax (eg 0xffee) 
    little  = decimal | '0' + (b + binary | o + octal | x + hex)

    # big-endian literals have postfix (eg ffeex0)
    big     = (binary + b | octal + o | hex + x) + '0'

    # optional spaces - will be ignored
    spaces  = Drop(Regexp(r'\s*'))
        
    with Separator(spaces):
        
        # the grammar is recursive - expressions can contain expressions - so
        # we use a delayed matcher here as a placeholder, so that we can use
        # them before they are defined.
        expr   = Delayed()
        
        # a value can be big or little-endian
        value  = big | little
        
        # a list of values is defined with [...] - we drop those and pass
        # the whole thing to list so that they are grouped together in the
        # results
        values = Drop('[') & value[1:,Drop(',')] & Drop(']')  > list
        
        repeat = (values & Drop('*') & value)                 * mult
        
        # a value with a length is a tuple, but we need to swap the order
        lvalue = value & Drop('/') & length                   > stuple
        
        # a named value is also a tuple
        named  = name & Drop('=') & (value | lvalue)          > tuple
        
        # an entry in the expression could be any of these
        entry  = named | lvalue | value | expr | values | repeat
        
        # and an expression itself consists of a comma-separated list of
        # one or more entries, surrounded by paremtheses
        args   = Drop('(') & entry[1:,Drop(',')] & Drop(')')
        
        # the Binary node may be expliti or implicit and takes the list of
        # entries as an argument list
        binary = Optional(Drop('Binary')) & args              > Binary
        
        # alternatively, we can give a name and create a named sub-class
        # (the '*' gives name and ags as two separate arguments to the
        # function named_class, instead of bundling them in a list)
        other  = (name & args)                                * named_class
        
        # and finally, we "tie the knot' by giving a definition for the
        # delayed matcher we introduced earlier, which is either a binary
        # node or a subclass
        expr  += spaces & (binary | other) & spaces
    
    return expr.string_parser()


__PARSER = None

def parse(spec):
    global __PARSER
    if __PARSER is None:
        __PARSER = make_binary_parser()
    result = __PARSER(spec)
    if result:
        return result[0]
    else:
        raise ValueError('Cannot parse: {0!r}'.format(spec))
