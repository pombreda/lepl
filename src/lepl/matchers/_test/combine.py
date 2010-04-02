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
Tests for the combining matchers.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers.combine import DepthFirst, BreadthFirst
from lepl.matchers.core import Any


class DirectionTest1(TestCase):
    
    def matcher(self):
        return Any()
    
    def test_depth(self):
        #basicConfig(level=DEBUG)
        matcher = DepthFirst(self.matcher(), 1, 2)
        matcher.config.no_full_first_match()
        matcher = matcher.get_match()
        results = list(map(''.join, map(lambda x: x[0], matcher('123'))))
        assert results == ['12', '1'], results
        
    def test_breadth(self):
        matcher = BreadthFirst(self.matcher(), 1, 2)
        matcher.config.no_full_first_match()
        matcher = matcher.get_match()
        results = list(map(''.join, map(lambda x: x[0], matcher('123'))))
        assert results == ['1', '12'], results
        
class DirectionTest2(TestCase):
    
    def matcher(self):
        return ~Any()[:] & Any()
    
    def test_depth(self):
        matcher = DepthFirst(self.matcher(), 1, 2)
        matcher.config.no_full_first_match()
        matcher = matcher.get_match()
        results = list(map(''.join, map(lambda x: x[0], matcher('123'))))
        assert results == ['3', '23', '2', '13', '12', '1'], results
        
    def test_breadth(self):
        matcher = BreadthFirst(self.matcher(), 1, 2)
        matcher.config.no_full_first_match()
        matcher = matcher.get_match()
        results = list(map(''.join, map(lambda x: x[0], matcher('123'))))
        assert results == ['3', '2', '1', '23', '13', '12'], results
