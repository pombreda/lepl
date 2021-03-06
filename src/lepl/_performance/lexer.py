
# The contents of this file are subject to the Mozilla Public License
# (MPL) Version 1.1 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License
# at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#
# The Original Code is LEPL (http://www.acooke.org/lepl)
# The Initial Developer of the Original Code is Andrew Cooke.
# Portions created by the Initial Developer are Copyright (C) 2009-2010
# Andrew Cooke (andrew@acooke.org). All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms
# of the LGPL license (the GNU Lesser General Public License,
# http://www.gnu.org/licenses/lgpl.html), in which case the provisions
# of the LGPL License are applicable instead of those above.
#
# If you wish to allow use of your version of this file only under the
# terms of the LGPL License and not to allow others to use your version
# of this file under the MPL, indicate your decision by deleting the
# provisions above and replace them with the notice and other provisions
# required by the LGPL License.  If you do not delete the provisions
# above, a recipient may use your version of this file under either the
# MPL or the LGPL License.

'''
Performance related tests.
'''

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401, R0903, R0912, R0914
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=E1101

from __future__ import print_function
from logging import basicConfig, DEBUG
from math import sin, cos
from operator import add, sub, mul, truediv

from lepl import *


def lexer():
    
    #basicConfig(level=DEBUG)
        
    class BinaryExpression(Node):
        def __float__(self):
            return self.op(float(self[0]), float(self[1]))
    
    class Sum(BinaryExpression): op = add
    class Difference(BinaryExpression): op = sub
    class Product(BinaryExpression): op = mul
    class Ratio(BinaryExpression): op = truediv
    
    class Call(Node):
        funs = {'sin': sin,
                'cos': cos}
        def __float__(self):
            return self.funs[self[0]](self[1])
        
    # we use unsigned float then handle negative values explicitly;
    # this lets us handle the ambiguity between subtraction and
    # negation which requires context (not available to the the lexer)
    # to resolve correctly.
    number  = Token(UnsignedReal())
    name    = Token('[a-z]+')
    symbol  = Token('[^a-zA-Z0-9\\. ]')
    
    expr    = Delayed()
    factor  = Delayed()
    
    float_  = Or(number                             >> float,
                 ~symbol('-') & number              >> (lambda x: -float(x)))
    
    open_   = ~symbol('(')
    close   = ~symbol(')')
    trig    = name(Or('sin', 'cos'))
    call    = trig & open_ & expr & close           > Call
    parens  = open_ & expr & close
    value   = parens | call | float_
    
    # omitting symbol around "/" didn't give an error below.
    ratio   = value & ~symbol('/') & factor         > Ratio
    prod    = value & ~symbol('*') & factor         > Product
    factor += prod | ratio | value
    
    diff    = factor & ~symbol('-') & expr          > Difference
    sum_    = factor & ~symbol('+') & expr          > Sum
    expr   += sum_ | diff | factor
    
    line    = Trace(expr & Eos())
    line.config.auto_memoize(full=True)
    # this only gives crazy-fast times with the null parser because that
    # parser uses a "naive" source, which hashes the entire string and
    # so recognises that calls are duplicated.  if the string parser is
    # used the string is wrapped in a StringIO that reads line by line
    # and so hashing cannot recognise that the entire input is as before 
    parser  = line.get_parse()
#    parser  = line.get_parse_string()
    
    def myeval(text):
        result = parser(text)[0]
        return float(result)
    
    for i in range(1,1001):
        print('.', end='')
        p = i % 100 == 0
        if p: print()
        x = myeval('1')
        if p: print(x)
        x = myeval('1 + 2*3')
        if p: print(x)
        x = myeval('1 - 4 / (3 - 1)')
        if p: print(x)
        x = myeval('1 -4 / (3 -1)')
        if p: print(x)
        x = myeval('1 + 2*sin(3+ 4) - 5')
        if p: print(x)


def time():
    from timeit import Timer
    t = Timer("lexer()", "from __main__ import lexer")
    print(t.timeit(number=1))
    # 15.1772289276
    # 12.5665969849 with flatten, compose
    # 7.47127509117 without Trace() matcher
    # 7.02462887764 without trace monitor 
    # 6.95 with RMemo
    # rewrote to only compile once(!) and then run 1000 times
    # 243 without memo
    # 0.77 with RMemo
    # 0.69 with LMemo
    # 0.77 with auto_memoize
    # 1.7 after many changes to memoization, etc
    

def profile():
    '''
import pstats
p=pstats.Stats('lexer.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('lexer()', 'lexer.prof')

if __name__ == '__main__':
    time()
#    profile()
#    lexer()

    
    