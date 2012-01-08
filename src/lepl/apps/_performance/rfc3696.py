
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

from lepl import Eos
from lepl.apps.rfc3696 import _HttpUrl


http = _HttpUrl() & Eos()

# values are before/after adding IP addresses
# value in pares is char count; other values are timing in secs

# (89041/115471) 1.17/1.20
#http.config.clear()

# (89441/115951) 1.02/1.08
#http.config.clear().direct_eval()

# (3089/7835) 0.48/0.53
#http.config.clear().compile_to_nfa()
# (3089/7835) 0.45/0.51
#http.config.clear().compile_to_dfa()
# (3352/10148) 0.23/0.29
#http.config.clear().compile_to_re()
# (1288/3693) 0.50/0.53 
#http.config

# (1640/6287) 0.26/0.29
#http.config.compile_to_re().no_direct_eval()
# (1695/6422) 0.21/0.24
http.config.compile_to_re()

# (2775/9906) 0.05/0.05
#http.config.compile_to_re().auto_memoize(full=True)


def assert_literal(text):
    result = http.parse(text)
    assert result == [text], result

def task():
    assert_literal(r'http://www.acooke.org')
    assert_literal(r'http://www.acooke.org/')
    assert_literal(r'http://www.acooke.org:80')
    assert_literal(r'http://www.acooke.org:80/')
    assert_literal(r'http://www.acooke.org/andrew')
    assert_literal(r'http://www.acooke.org:80/andrew')
    assert_literal(r'http://www.acooke.org/andrew/')
    assert_literal(r'http://www.acooke.org:80/andrew/')
    assert_literal(r'http://www.acooke.org/?foo')
    assert_literal(r'http://www.acooke.org:80/?foo')
    assert_literal(r'http://www.acooke.org/#bar')
    assert_literal(r'http://www.acooke.org:80/#bar')
    assert_literal(r'http://www.acooke.org/andrew?foo')
    assert_literal(r'http://www.acooke.org:80/andrew?foo')
    assert_literal(r'http://www.acooke.org/andrew/?foo')
    assert_literal(r'http://www.acooke.org:80/andrew/?foo')
    assert_literal(r'http://www.acooke.org/andrew#bar')
    assert_literal(r'http://www.acooke.org:80/andrew#bar')
    assert_literal(r'http://www.acooke.org/andrew/#bar')
    assert_literal(r'http://www.acooke.org:80/andrew/#bar')
    assert_literal(r'http://www.acooke.org/andrew?foo#bar')
    assert_literal(r'http://www.acooke.org:80/andrew?foo#bar')
    assert_literal(r'http://www.acooke.org/andrew/?foo#bar')
    assert_literal(r'http://www.acooke.org:80/andrew/?foo#bar')

def time():
    from timeit import Timer
    t = Timer("task()", "from __main__ import task")
    print(min(t.repeat(repeat=10, number=10)))

def profile():
    '''
    import pstats
    p=pstats.Stats('task.prof')
    p.strip_dirs()
    p.sort_stats('cumulative')
    p.sort_stats('time')
    p.print_stats(35)
    '''
    import cProfile
    cProfile.run('task()', 'task.prof')

if __name__ == '__main__':

    tree = http.get_parse().matcher.tree()
    print(tree)
    print(len(tree))
    
    time()
#    profile()
#    floats()


    
