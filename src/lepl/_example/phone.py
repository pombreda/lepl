
from lepl.match import *
from lepl.node import make_dict

name    = Word()              > 'name'
phone   = Integer()           > 'phone'
matcher = name / ',' / phone  > make_dict

print(next(matcher('andrew, 3333253')))


print(next(Word()('hello world')))
print(next(Integer()('123 four five')))

print(next(And(Word(), Space(), Integer())('hello 123')))
print(next( (Word() & Space() & Integer())('hello 123')) )
print(next( (Word() / Integer())('hello 123')) )
print((Word() / Integer()).parse_string('hello 123'))

print(next( (Word() > 'name')('andrew') ))
print(dict([('name', 'andrew'), ('phone', '3333253')]))
print(next( (name / ',' / phone)('andrew, 3333253') ))

spaces  = Space()[0:]
name    = Word()              > 'name'
phone   = Integer()           > 'phone'
line    = name / ',' / phone  > make_dict
newline = spaces & Newline() & spaces
matcher = line[0:,~newline]
parsed = matcher.parse_string('andrew, 3333253\n bob, 12345')
print(parsed)

def combine(results):
    all = {}
    for result in results:
        all[result['name']] = result['phone']
    return all

spaces  = Space()[0:]
name    = Word()              > 'name'
phone   = Integer()           > 'phone'
line    = name / ',' / phone  > make_dict
newline = spaces & Newline() & spaces
matcher = line[0:,~newline]   > combine
parsed = matcher.parse_string('andrew, 3333253\n bob, 12345')
print(parsed)

    