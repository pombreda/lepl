
from lepl import *

#name = ('Mr' | 'Ms') // Word()

#name = ('Mr' // Word() > 'man' | 'Ms' // Word() > 'woman')


with Override(or_=And, and_=Or):
    pass