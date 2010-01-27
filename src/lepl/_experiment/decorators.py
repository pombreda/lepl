

def decorator(f):
    def result(*args, **kargs):
        print(f)
        print('args', args)
        print('kargs', kargs)
        return f(*args, **kargs)
    return result

@decorator
def twice(x):
    return 2*x

def buildTwice():
    def twice(x):
        return 2*x
    return decorator(twice)

class Twice(object):
    
    @decorator
    def twice(self, x):
        return 2*x
        
if __name__ == '__main__':
    print(twice(3))
    t2 = buildTwice()
    print(t2(3))
    t3 = Twice()
    t3.twice(3)
    
    
    