
from lepl.match import *

print( Literal('hello').parse_string('hello world') )

print( Any().parse_string('hello world') )
print( Any('abcdefghijklm')[0:].parse_string('hello world') )

print( And(Any('h'), Any()).parse_string('hello world') )
print( And(Any('h'), Any('x')).parse_string('hello world') )

print( Or(Any('x'), Any('h'), Any('z')).parse_string('hello world') )
print( Or(Any('h'), Any()[3]).parse_string('hello world') )

generator = Or(Any('h'), Any()[3])('hello world')
print( next(generator) )
print( next(generator) )

print( Repeat(Any(), 3, 3).parse_string('12345') )

print( Repeat(Any(), 3).parse_string('12345') )
print( Repeat(Any(), 3).parse_string('12') )

generator = Repeat(Any(), 3)('12345')
print( next(generator) )
print( next(generator) )
print( next(generator) )
#print( next(generator) )

generator = Repeat(Any(), 3, None, 1)('12345')
print( next(generator) )
print( next(generator) )
print( next(generator) )

print( Lookahead(Literal('hello')).parse_string('hello world') )
print( Lookahead('hello').parse_string('goodbye cruel world') )
print( (~Lookahead('hello')).parse_string('hello world') )
print( (~Lookahead('hello')).parse_string('goodbye cruel world') )

print( (Drop('hello') / 'world').parse_string('hello world') )
print( (Lookahead('hello') / 'world').parse_string('hello world') )

def show(results):
    print('results:', results)
    return results

print( Apply(Any()[:,...], show).parse_string('hello world') )
print( Apply(Any()[:,...], show, raw=True).parse_string('hello world') )
