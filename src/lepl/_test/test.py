

class Foo(object):
    
    def __rsub__(self, other):
        return self
    
if __name__ == '__main__':
    a -= Foo()
    print(a)
    