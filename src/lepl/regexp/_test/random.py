
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Tests for the lepl.regexp package.  We generate random expressions and
test the results against the python regexp matcher.
'''

#from logging import basicConfig, DEBUG, getLogger
from random import randint, choice
from re import compile as compile_
from sys import exc_info
from unittest import TestCase

from lepl.regexp.matchers import DfaRegexp
from lepl.support import format

def randbool(weight=1):
    return choice([True] * weight + [False])

def random_expression(depth_left, alphabet):
    '''
    Generate an expression.  If depth_left is 0 then the result must be
    a simple character; other levels build on this.  Alphabet is a list of
    possible regular characters.
    '''
    if depth_left:
        return choice([random_sequence,
                       random_option,
                       random_repeat,
                       random_choice,
                       random_range,
                       random_expression])(depth_left-1, alphabet)
    else:
        return choice(alphabet + '.')

def random_sequence(depth_left, alphabet):
    return ''.join(random_expression(depth_left, alphabet)
                   for _ in range(randint(1, 3)))

def random_option(depth_left, alphabet):
    subexpr = random_expression(depth_left, alphabet)
    if len(subexpr) > 1:
        return format('({0})?', subexpr)
    else:
        return subexpr + '?'

def random_repeat(depth_left, alphabet):
    subexpr = random_expression(depth_left, alphabet)
    if len(subexpr) > 1:
        return format('({0})*', subexpr)
    else:
        return subexpr + '*'

def random_choice(depth_left, alphabet):
    return format('({0})', '|'.join(random_expression(depth_left, alphabet)
                                    for _ in range(randint(1, 3))))

def random_range(_depth_left, alphabet):
    def random_chars():
        subexpr = ''
        for _ in range(randint(1, 2)):
            if randbool():
                subexpr += choice(alphabet)
            else:
                a, b = choice(alphabet), choice(alphabet)
                if a > b:
                    a, b = b, a
                subexpr += format('{0}-{1}', a, b)
        return subexpr
    def random_content():
        if randbool(len(alphabet)):
            return random_content()
        else:
            return '.'
    # cannot use random_content below with current lepl regexp
    if randbool():
        return format('[{0}]', random_chars())
    else:
        return format('[^{0}]', random_chars())

def random_string(depth_left, alphabet):
    if depth_left:
        return choice(alphabet) + random_string(depth_left-1, alphabet)
    else:
        return ''

class RandomTest(TestCase):
    
    def test_random(self):
        '''
        Compares lepl + python expressions.  This runs 'til it fails, and it
        always does fail, because lepl's expressions are guarenteed greedy
        while python's aren't.  This is "normal" (Perl is the same as Python)
        but I cannot fathom why it should be - it seems *harder* to make them
        wwork that way... 
        '''
        #basicConfig(level=DEBUG)
        #log = getLogger('lepl.reexgp._test.random')
        match_alphabet = '012'
        string_alphabet = '013'
        for _ in range(100):
            expression = random_expression(3, match_alphabet) 
            string = random_string(3, string_alphabet)
            lepl_result = DfaRegexp(expression).parse(string)
            if lepl_result:
                lepl_result = lepl_result[0]
            #log.debug(format('{0} {1} {2}', expression, string, lepl_result))
            try:
                python_result = compile_(expression).match(string) 
                if python_result:
                    python_result = python_result.group()
                assert lepl_result == python_result, \
                    format('{0} != {1}\n{2} {3}', 
                           lepl_result, python_result, expression, string)
            except:
                (e, v, _t) = exc_info()
                if repr(v) == "error('nothing to repeat',)":
                    pass
                else:
                    raise e
                