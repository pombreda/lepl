
from lepl.match import *
from lepl.node import make_dict

print(next(Literal('hello')('hello world')))
print(Literal('hello').parse_string('hello world'))
