
from lepl import *

#name = ('Mr' | 'Ms') // Word()

#name = ('Mr' // Word() > 'man' | 'Ms' // Word() > 'woman')


with Override(or_=And, and_=Or):
    abcd = (Literal('a') & Literal('b')) | ( Literal('c') & Literal('d'))
    print(abcd.parse_string('ac'))
    print(abcd.parse_string('ab'))
    
word = Letter()[:,...]
with Separator(r'\s+'):
    sentence = word[1:]
print(sentence.parse_string('hello world'))
