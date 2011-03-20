
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
