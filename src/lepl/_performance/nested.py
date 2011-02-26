
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


from random import choice

from lepl import *


def make_data(size):
    '''
    Generate a string about 2^(size+1) in size of nested parens with newlines.
    '''
    data = ""
    for _i in range(size):
        if choice([True, False]):
            data = '(' + data + ')' + data
        else:
            data = data + '(' + data + ')'
        if not data.endswith('\n') and len(data) > 10:
            data += '\n'
    return data


def right():
    pair = Delayed()
    with Separator(Regexp(r'\s*')):
        pair += '(' & Optional(pair) & ')' & Optional(pair)
    pair.config.clear().auto_memoize()
    p = pair.get_match_string()
    results = list(p(make_data(10)))
    print(len(results))


def left():
    '''
    This hammers the stream length method.
    
    Hmmm.  No it doesn't.  It does many more iterations than RMemo because it 
    has to "bottom out".  
    '''
    pair = Delayed()
    with Separator(Regexp(r'\s*')):
        pair += Optional(pair) & '(' & Optional(pair) & ')' 
    #p = pair.string_matcher(Configuration.dfa())
    pair.config.clear().auto_memoize()
    p = pair.get_match_string()
    results = list(p(make_data(6)))
    print(len(results))


def time(name='right'):
    from timeit import Timer
    t = Timer("{0}()".format(name), "from __main__ import {0}".format(name))
    print(t.timeit(number=10 if name == 'right' else 6)) 
    # right - 16.2 for 10
    # left - 82.5 for 6 (!)
    # after auto_memoize work
    # left - 30 for 6 (31 for conservative)
    # right - 15 for 10
    

def profile(name='right'):
    '''
import pstats
p=pstats.Stats('nested.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('{0}()'.format(name), 'nested.prof')

if __name__ == '__main__':
#    time('left')
    time('right')
#    profile('left')
#    right()
#    left()
    
    
