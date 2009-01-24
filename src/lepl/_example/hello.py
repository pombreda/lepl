
from lepl import *

print(next(Literal('hello')('hello world')))
print(Literal('hello').parse_string('hello world'))
