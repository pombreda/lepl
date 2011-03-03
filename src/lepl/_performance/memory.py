
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
Generate a stream that would exceed available memory.  Process it without
crashing.

To do this, the stream is a sequence of numbers (as string): '1', '2', ...
and the parser returns the numerical sum of different combinations of digits 
from the numbers.  So for 1..9 there is only a single result: 45, but for
1..10 the result could be 45 or 46.  This requires backtracking, but does
not use a lot of space for the result.

Note that, because we treat an iterable as a series of lines, each number 
is a line (not a character).

See http://www.acooke.org/cute/Processing1.html
'''

from sys import getsizeof
from logging import basicConfig, DEBUG, ERROR
from itertools import count, takewhile
try:
    from itertools import imap
except ImportError:
    imap = map

from lepl import *
from lepl.support.lib import fmt
from lepl.stream.iter import Cons


if __name__ == '__main__':
    
    def source(n_max):
        '''
        A source of integers from 1 to n_max inclusive.
        '''
        #return map(str, takewhile(lambda n: n <= n_max, count(1)))
        # python 2
        return imap(str, takewhile(lambda n: n <= n_max, count(1)))
    
    
    @sequence_matcher
    def Digits(support, stream):
        '''
        A matcher that returns each digit (as an int) in turn.
        '''
        (number, next_stream) = s_line(stream, False)
        for digit in number:
            yield ([int(digit)], next_stream)
    
    
    def parser():
        
        # a reduce function and the associated zero - this will sum the values
        # returned by Digit() instead of appending them to a list.  this is
        # to avoid generating a large result that may confuse measurements of
        # how much memory the parser is using.
        sum = ([0], lambda a, b: [a[0] + b[0]])
        
        with Override(reduce=sum):
            total = Digits()[:] & Eos()
        
        # configure for reduced memory use
        # all the options below are needed:
        # - manage() reduces stack use (less backtracking information)
        # - no_direct_wval() makes sure matchers are not combined (which gives
        #   more scope for the manage() to change the behaviour)
        # - no_full_first_match() avoids storig the input for any error message 
        total.config.manage().no_direct_eval().no_memoize().no_full_first_match()
            
        return total
    
    # some basic tests to make sure everything works
    l = list(source(9))
    assert l == ['1', '2', '3', '4', '5', '6', '7', '8', '9'], l
    p = parser()
    
    r = list(p.parse_iterable_all(source(9)))
    # the sum of digits 1-9 is 45
    assert r == [[45]], r
    
    r = list(p.parse_iterable_all(source(10)))
    # the digits in 1-10 can sum to 45 ot 46 depending on whether we use the
    # '1' or the '0' from 10.
    assert r == [[46],[45]], r
    
    # if we have 10^n numbers then we have about 10^n * n characters which
    # is 2 * 10^n * n bytes for UTF16
    def size(n):
        gb = 10**n * (n * 2 + getsizeof(Cons(None))) / 1024**3.0
        return fmt('{0:4.2f}', gb)
    s = size(8)
    assert s == '8.94', s
    s = size(7)
    assert s == '0.88', s

    # we'll test with 10**7 - just under a GB of data, according to the above
    # (on python2.6)
    
    # guppy only works for python 2 afaict
    # and it's broken for 2.7
    from guppy import hpy
    from gc import get_count, get_threshold, set_threshold, collect
    #basicConfig(level=DEBUG)
    basicConfig(level=ERROR)
    
    r = p.parse_iterable_all(source(10**7))
    next(r) # force the parser to run once, but keep the parser in memory
    h = hpy()
    print(h.heap())
    
# Partition of a set of 50077 objects. Total size = 6924832 bytes.
#  Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
#      0  19758  39  1790456  26   1790456  26 str
#      1  11926  24   958744  14   2749200  40 tuple
#      2    149   0   444152   6   3193352  46 dict of module
#      3   3011   6   361320   5   3554672  51 types.CodeType
#      4    604   1   359584   5   3914256  57 dict (no owner)
#      5   2918   6   350160   5   4264416  62 function
#      6    334   1   303568   4   4567984  66 dict of type
#      7    334   1   299256   4   4867240  70 type
#      8    150   0   157200   2   5024440  73 dict of lepl.core.config.ConfigBuilder
#      9    140   0   149792   2   5174232  75 dict of class
# <178 more rows. Type e.g. '_.more' to view.>
