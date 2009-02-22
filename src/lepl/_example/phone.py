
from lepl import *

name    = Word()              > 'name'
phone   = Integer()           > 'phone'
matcher = name / ',' / phone  > make_dict

parser = matcher.string_parser()
print(parser('andrew, 3333253'))
#print(parser.matcher)

print(next(Word().match('hello world')))
print(next(Integer()('123 four five')))

print(next(And(Word(), Space(), Integer()).match('hello 123')))
print(next( (Word() & Space() & Integer()).match('hello 123')) )
print(next( (Word() / Integer()).match('hello 123')) )
print((Word() / Integer()).parse('hello 123'))

print('----')
print(matcher.parse('andrew, 3333253')[0])

print(next( (Word() > 'name').match('andrew') ))
print(next( (Integer() > 'phone').match('3333253') ))
print(dict([('name', 'andrew'), ('phone', '3333253')]))
print(next( (name / ',' / phone)('andrew, 3333253') ))

print('----')

spaces  = Space()[0:]
name    = Word()              > 'name'
phone   = Integer()           > 'phone'
line    = name / ',' / phone  > make_dict
newline = spaces & Newline() & spaces
matcher = line[0:,~newline]
parsed = matcher.parse('andrew, 3333253\n bob, 12345')
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
parsed = matcher.parse('andrew, 3333253\n bob, 12345')
print(parsed)

    