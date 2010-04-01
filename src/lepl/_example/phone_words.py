
# Copyright 2010 Andrew Cooke

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


from lepl._example.support import Example

from lepl import *


@sequence_matcher
def Digit(support, stream):
    digits = {'1': '',     '2': 'abc',  '3': 'def',
              '4': 'ghi',  '5': 'jkl',  '6': 'mno',
              '7': 'pqrs', '8': 'tuv',  '9': 'wxyz',
              '0': ''}
    if stream:
        digit, tail = stream[0], stream[1:]
        yield ([digit], tail)
        if digit in digits:
            for letter in digits[digit]:
                yield ([letter], tail)


class LettersTest(Example):
    
    def test_painter(self):
        results = Digit()[13, ...].match('1-800-7246837')
        #print(type(results))
        words = map(lambda result: result[0][0], results)
        assert '1-800-painter' in words
        