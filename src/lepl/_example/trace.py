
from logging import basicConfig, INFO, DEBUG

from lepl import *

basicConfig(level=INFO)

spaces  = Space()[0:]
name    = Word()              > 'name'
phone   = Integer()           > 'phone'
line    = name / ',' / phone  > make_dict
matcher = line[0:,~Newline()]
parsed = matcher.parse_string('andrew, 3333253\n bob, 12345',
                              Configuration(monitors=[RecordDeepest()]))
print(parsed)


spaces  = Space()[0:]
name    = Word()              > 'name'
phone   = Trace(Integer())    > 'phone'
line    = name / ',' / phone  > make_dict
matcher = line[0:,~Newline()]
parsed = matcher.parse_string('andrew, 3333253\n bob, 12345')
print(parsed)
