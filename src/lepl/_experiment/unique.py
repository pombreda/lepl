
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

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401, W0232


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
    pass

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
