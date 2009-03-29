

from unittest import TestCase


def default(**defaults):
    def decorator(fun):
        def replacement(*args, **kargs):
            for name in defaults:
                if name not in kargs:
                    template = defaults[name]
                    # is this the best way to clone values?
                    kargs[name] = type(template)(template)
            return fun(*args, **kargs)
        return replacement
    return decorator


class WithDefaults:
    
    @default(mylist=[1,2,3])
    def foo(self, target, mylist):
        assert target == mylist

    @default(mylist=[1,2,3])
    def mutable(self, target, mylist):
        assert target == mylist
        mylist.append(4)
        
        
class DefaultsTest(TestCase):
    
#    def test_foo(self):
#        wd = WithDefaults()
#        wd.foo([4,5], [4,5])
#        wd.foo([1,2,3])
#        wd.foo([4,5], mylist=[4,5])
#        wd.foo(target=[4,5], mylist=[4,5])
#        
#    def test_mutable(self):
#        wd = WithDefaults()
#        wd.foo([4,5], [4,5])
#        wd.foo([1,2,3])
#        wd.foo([4,5], mylist=[4,5])
#        wd.foo(target=[4,5], mylist=[4,5])
#        
