
from lepl.match import *
from lepl.node import make_dict

matcher = (Word() > 'name') / ',' / (UnsignedInteger() > 'phone') > make_dict
parsed = matcher.parse_string('andrew, 3333253')[0]
print(parsed)

matcher = (Word() > 'name') / ',' / (UnsignedInteger() > 'phone')
parsed = matcher.parse_string('andrew, 3333253')
print(parsed)

spaces  = Space()[0:,...]
name    = Word()                       > 'name'
phone   = Integer()                    > 'phone'
line    = spaces / name / ',' / phone  > make_dict
newline = spaces + Newline()
matcher = line[0:,~newline]
parsed = matcher.parse_string('andrew, 3333253\n bob, 12345')
print(parsed)
