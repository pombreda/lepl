
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
Experimental code.
'''

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401, W0232, R0911, W0703


from itertools import count
from random import uniform
from types import GeneratorType


def node(level=0, p=0.0001):
    if uniform(0, 1) < p:
        yield str(level)
    else:
        child1 = node(level+1, p)
        child2 = node(level+1, p)
        yield (yield child1) + ',' + str(level) 
        yield (yield child2) + ',' + str(level) 
        yield (yield child1) + ',' + str(level) 


def trampoline(main):
    stack = []
    value = main
    exception = False
    while True:
        try:
            if type(value) is GeneratorType:
                stack.append(value)
                value = next(stack[-1])
            else:
                stack.pop()
                if stack:
                    if exception:
                        exception = False
                        value = stack[-1].throw(value)
                    else:
                        value = stack[-1].send(value)
                else:
                    if exception:
                        raise value
                    else:
                        yield value
                    value = main
        except Exception as e:
            if exception:
                raise value
            else:
                value = e
                exception = True
    
def fib(n):
    if n < 2:
        yield n
    else:
        yield (yield fib(n-1)) + (yield fib(n-2)) 
        
        
def add_attribute(f):
    def fun(*args, **kargs):
        gen = f(*args, **kargs)
        gen.attribute = 42
    return fun

# @add_attribute - doesn't work, generators have read-only attributes            
def sequence(n):
    for _i in range(n):
        yield n


def outer(n):
    for i in range(n):
        gen = sequence(i)
        try:
            while True:
                yield (yield gen)
        except StopIteration:
            pass
        
        
if __name__ == '__main__':
#    t = trampoline(node())
#    for i in t:
#        print(i)

#    for n in range(1, 10):
#        print(n, next(trampoline(fib(n))))
#    print(100, next(trampoline(fib(100))))

#    def stack_size(depth=0):
#        if 0 == depth % 100:
#            print(depth, ' ', end='')
#        stack_size(depth+1)
#    stack_size()
    
    generator = trampoline(outer(3))
    print(list(zip(count(), generator)))
            