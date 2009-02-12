
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
    try:
        stack = []
        value = main
        while True:
            if type(value) is GeneratorType:
                stack.append(value)
                value = next(stack[-1])
            else:
                stack.pop()
                if stack:
                    value = stack[-1].send(value)
                else:
                    yield value
                    value = main
    except StopIteration:
        pass
    
    
def fib(n):
    if n < 2:
        yield n
    else:
        yield (yield fib(n-1)) + (yield fib(n-2)) 
    
            
if __name__ == '__main__':
#    t = trampoline(node())
#    for i in t:
#        print(i)

    for n in range(1, 10):
        print(n, next(trampoline(fib(n))))
    print(100, next(trampoline(fib(100))))

#    def stack_size(depth=0):
#        if 0 == depth % 100:
#            print(depth, ' ', end='')
#        stack_size(depth+1)
#    stack_size()
    