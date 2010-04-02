
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

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401, R0903
#@PydevCodeAnalysisIgnore


from lepl import *


def floats():
        
    class Term(Node): pass
    class Factor(Node): pass
    class Expression(Node): pass
        
    expr   = Delayed()
    number = Float()                                > 'number'
    spaces = Drop(Regexp(r'\s*'))
    
    with Separator(spaces):
        term    = number | '(' & expr & ')'         > Term
        muldiv  = Any('*/')                         > 'operator'
        factor  = term & (muldiv & term)[:]         > Factor
        addsub  = Any('+-')                         > 'operator'
        expr   += factor & (addsub & factor)[:]     > Expression
        line    = Trace(expr) & Eos()
    
    #basicConfig(level=DEBUG)
    line.config.auto_memoize()
    parser = line.get_parse_string()
    
    print(repr(parser.matcher))
    for _i in range(3000): # increased from 30 to 3000 for new code
        results = parser('1.2e3 + 2.3e4 * (3.4e5 + 4.5e6 - 5.6e7)')
        assert isinstance(results[0], Expression)
    print(results[0])


def time():
    from timeit import Timer
    t = Timer("floats()", "from __main__ import floats")
    print(t.timeit(number=1))
    # 5.8 for default
    # second values after improving rewrite
    # 4.9,3.5,2.8,1.3 for dfa
    # 5.0,3.7,2.9,3.1 for nfa
    # wow - new code, with standard config, functions etc, 0.5
    # increase to 300, avoids parser building bias: 2.2
    # increase to 3000, improved memo: 20
    # before changing GeneratorWrapper: 18.8,19.8,18.9; after: 17.8,18.3,18.1
    

def profile():
    '''
import pstats
p=pstats.Stats('floats.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('floats()', 'floats.prof')

if __name__ == '__main__':
    time()
#    profile()
#    floats()

    
    
