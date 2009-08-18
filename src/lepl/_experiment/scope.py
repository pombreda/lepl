
'''
Seem to be having problems with scoping.  This is to test some ideas out.
'''

# these have no effect
bar = 'x'
foo = 'y'

# this works just fine
class Outer(object):
    @staticmethod
    def __call__(foo):
        class Inner(object):
            bar = foo
        return Inner()
    
if __name__ == '__main__':
    outer = Outer()
    inner = outer('baz')
    print(type(inner).bar)
    print(inner.bar)
