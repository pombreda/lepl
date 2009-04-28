
'''
Experimental code - exploring generators and Python 3.
'''

# what happens when we pass various things to []?

class CheckSlice(object):
    
    def __getattr__(self, attr):
        self.dump('__getattr__', attr)
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            raise AttributeError()
        
#    def __getslice__(self, *attr):
#        self.dump('__getslice__', attr)
        
    def __getitem__(self, *attr):
        self.dump('__getitem__', *attr)
        
    def dump(self, name, value):
        print(name, value)
        print(type(value))
        print(dir(value))
    
    def callable(self, *args, **kargs):
        print(args)
        print(kargs)
        
    def run(self):
        print("1")
        self[1]
        print("1:2")
        self[1:2]
        print("'a':'b'")
        self['a':'b']
        print("1:2:3")
        self[1:2:3]
        print("'a':'b':'c'")
        self['a':'b':'c']
        print("...")
        self[...]
        print("...,1:")
        self[...,1:]
        print("::")
        self[::]
        print("1:2:3,','")
        self[1:2:3,',']
        
        
class CheckDash(object):
    
    def __init__(self, name):
        self.name = name
    
    def __sub__(self, other):
        print(self, '__sub__', other)
        return CheckDash(str(self) + '-' + str(other))
        
    def __rsub__(self, other):
        print(self, '__rsub__', other)
        return CheckDash(str(self) + '-' + str(other))
        
    def __neg__(self):
        print('__neg__', self)
        return CheckDash('-' + str(self))
    
    def __rneg__(self):
        print('__rneg__', self)
        return CheckDash('-' + str(self))
    
    def __str__(self):
        return self.name
        
    @staticmethod
    def run():
        a = CheckDash('a')
        b = CheckDash('b')
        print("a-b")
        a-b
        print("a--b")
        a--b
        print("'a'-b")
        'a'-b
        print("'a'--b")
        a--b
        print("a-'b'")
        a-'b'
        print("a--'b'")
        a--'b'
        

class CheckReturnYield(object):
    
    def counter(self, n, direct):
        if direct:
            for i in range(n):
                yield i
        else:
            # this does not compile
            #return self.indirect(n)
            pass
        
    def indirect(self, n):
        for i in range(n):
            yield i
            
    def run(self):
        c = self.counter(3, True)
        print(type(c))
        for i in c:
            print(i)
        c = self.counter(3, False)
        print(type(c))
        for i in c:
            print(i)
            
            
class CheckGeneratorProxy(object):
    
    def __getattr__(self, name):
        return getattr(self.target, name)
    
    def run(self):
        self.target = Numbers()
        for i in self.numbers():
            print(i)

class Numbers(object):
    
    def numbers(self):
        for i in range(5):
            yield i
            
            
import inspect

class InvisibleScope(object):
    
    def __enter__(self):
        print('enter')
        inspect.currentframe().f_locals['foo'] = 'bar'
        for x in dict(inspect.currentframe().f_locals):
            print(x, inspect.currentframe().f_locals[x])
        try:
            print(foo)
        except:
            print('missing in enter')
        
    def __exit__(self, *args):
        print('exit')
        
    def method(self):
        try:
            print(foo)
        except:
            print('missing in method')
                    
    def run(self):
        try:
            print(foo)
        except:
            print('missing before')
        with self:
            try:
                print(foo)
            except:
                print('missing inside')
            self.method()
        try:
            print(foo)
        except:
            print('missing after')
        
        

        

if __name__ == '__main__':
    #CheckSlice().run()
    #CheckDash.run()
    #CheckReturnYield().run()
    #CheckGeneratorProxy().run()
    InvisibleScope().run()
    
    
