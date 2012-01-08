
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
Performance related tests.
'''

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401
#@PydevCodeAnalysisIgnore


#from logging import basicConfig, DEBUG

from lepl import *


def full_left():
    '''
    Extreme test of left-recursion.
    '''
    #basicConfig(level=DEBUG)
    ab  = Delayed()
    with Separator(Regexp(r'\s*')):
        ab += (ab & 'b') | 'a'
#        ab += 'a' | (ab & 'b')
    m = ab & Eos()
    m.config.clear().auto_memoize()
    p = m.get_match_string()
    results = list(p('a' + ('\nb' * 1000)))
    assert len(results) == 1
    print('done')


def time():
    from timeit import Timer
    t = Timer("full_left()", "from __main__ import full_left")
    print(t.timeit(number=10)) 
    # 17.6 for 10 (x100 bs)
    # 0.6 when rewritten 'a' | (ab & 'b')
    # 0.4 with auto_memoize
    

def profile():
    '''
import pstats
p=pstats.Stats('full_left.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(40)
    '''
    import cProfile
    cProfile.run('full_left()', 'full_left.prof')

if __name__ == '__main__':
    time()
#    profile()
#    full_left()

    
    
