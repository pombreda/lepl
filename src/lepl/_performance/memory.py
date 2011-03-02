
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
'''

from itertools import count, takewhile
try:
    from itertools import imap
except ImportError:
    imap = map

from logging import basicConfig, DEBUG, ERROR
from sys import getsizeof

from lepl import *
from lepl.stream.iter import Cons
from lepl.support.lib import fmt
from lepl.matchers.complex import NO_STATE


def source(n_max):
    '''
    A source of integers from 1 to n_max inclusive.
    '''
    #return map(str, takewhile(lambda n: n <= n_max, count(1)))
    # python 2
    return imap(str, takewhile(lambda n: n <= n_max, count(1)))


@sequence_matcher
def Digits(support, stream):
    (number, next_stream) = s_line(stream, False)
    for digit in number:
        yield ([int(digit)], next_stream)


def parser():
    sum = ([0], lambda a, b: [a[0] + b[0]])
    with Override(reduce=sum):
        total = Digits()[:] & Eos()
    return total


p = parser()
from guppy import hpy
from gc import get_count, get_threshold, set_threshold, collect, get_objects, get_referrers
basicConfig(level=DEBUG)
p.config.add_monitor(GeneratorManager(10)).no_direct_eval()
p.config.no_memoize().no_full_first_match()
pp = p.get_parse_iterable_all()
print(pp.matcher.tree())
r = pp(source(10**3)) # keep generators open by not expanding
print(next(r))
print(get_count(), get_threshold())
h = hpy()
hp = h.heap()


if __name__ == '__main__':
    
    # some basic tests to make sure everything works
    l = list(source(9))
    assert l == ['1', '2', '3', '4', '5', '6', '7', '8', '9'], l
    p = parser()
    r = list(p.parse_iterable_all(source(9)))
    assert r == [[45]], r
    r = list(p.parse_iterable_all(source(10)))
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

    # let's try an initial stream of about 1GB
    #r = list(p.parse_iterable(source(10**7)))
    #assert r == [], r
    # ouch.  so that crashed my laptop
    
    #p.config.add_monitor(GeneratorManager(10))
    #r = list(p.parse_iterable(source(10**7)))
    #assert r == [], r
    # that doesn't work either, because (i think), the chain of generators is
    # all within Repeat().
    
    #basicConfig(level=DEBUG)
    #p.config.add_monitor(GeneratorManager(10)).no_direct_eval()
    #r = list(p.parse_iterable(source(10**7)))
    #assert r == [], r
    # that was better - memory increased more slowly, and debug messages
    # showed generators were being closed - but still kept going up til killed
    
    # guppy only works for python 2 afaict
    # and it's broken for 2.7
    from guppy import hpy
    from gc import get_count, get_threshold, set_threshold, collect
#    basicConfig(level=DEBUG)
    basicConfig(level=ERROR)
    p.config.add_monitor(GeneratorManager(10)).no_direct_eval()

#    r = p.parse_iterable_all(source(10**3)) # keep generators open by not expanding
#    print(next(r))
#    print(get_count(), get_threshold()) 
#    h = hpy()
#    print(h.heap())
#[4996]
#((250, 6, 4), (700, 10, 10))
#Partition of a set of 74882 objects. Total size = 10699192 bytes.
# Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
#     0  20646  28  1833424  17   1833424  17 str
#     1  16337  22  1297648  12   3131072  29 tuple
#     2   1008   1  1056384  10   4187456  39 dict of lepl.core.manager.GeneratorRef
#     3   1000   1  1048000  10   5235456  49 dict of 0x8471d0
#     4   1505   2   640280   6   5875736  55 dict (no owner)
#     5    149   0   444152   4   6319888  59 dict of module
#     6   4714   6   377120   4   6697008  63 types.MethodType
#     7   3012   4   361440   3   7058448  66 types.CodeType
#     8   2920   4   350400   3   7408848  69 function
#     9    334   0   303568   3   7712416  72 dict of type
#<182 more rows. Type e.g. '_.more' to view.>
    
#    r = p.parse_iterable_all(source(10**3.1)) # keep generators open by not expanding
#    print(next(r))
#    print(get_count(), get_threshold())
#    h = hpy()
#    print(h.heap())
#[5254]
#((510, 1, 5), (700, 10, 10))
#Partition of a set of 82364 objects. Total size = 11770392 bytes.
# Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
#     0  20903  25  1845768  16   1845768  16 str
#     1  17627  21  1396720  12   3242488  28 tuple
#     2   1266   2  1326768  11   4569256  39 dict of lepl.core.manager.GeneratorRef
#     3   1258   2  1318384  11   5887640  50 dict of 0x846620
#     4   1763   2   712520   6   6600160  56 dict (no owner)
#     5   5746   7   459680   4   7059840  60 types.MethodType
#     6    149   0   444152   4   7503992  64 dict of module
#     7   3012   4   361440   3   7865432  67 types.CodeType
#     8   2920   4   350400   3   8215832  70 function
#     9    334   0   303568   3   8519400  72 dict of type
#<182 more rows. Type e.g. '_.more' to view.>
#    print(list(r))
#    h = hpy()
#    print(h.heap())
#[[5255], [5258], [5261]]
#Partition of a set of 45559 objects. Total size = 6310176 bytes.
# Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
#     0  19492  43  1776264  28   1776264  28 str
#     1  11301  25   910920  14   2687184  43 tuple
#     2    149   0   444152   7   3131336  50 dict of module
#     3   3012   7   361440   6   3492776  55 types.CodeType
#     4   2910   6   349200   6   3841976  61 function
#     5    322   1   300208   5   4142184  66 dict of type
#     6    322   1   288408   5   4430592  70 type
#     7    296   1   276416   4   4707008  75 dict (no owner)
#     8     66   0   221232   4   4928240  78 dict of 0x8aaf80
#     9    151   0   158248   3   5086488  81 dict of lepl.core.config.ConfigBuilder
#<146 more rows. Type e.g. '_.more' to view.>

#    r = p.parse_iterable_all(source(10**4)) # keep generators open by not expanding
#    print(next(r))
#    print(get_count(), get_threshold())
#    h = hpy()
#    print(h.heap())
#[49996]
#((363, 9, 3), (700, 10, 10))
#Partition of a set of 335881 objects. Total size = 48804432 bytes.
# Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
#     0  10008   3 10488384  21  10488384  21 dict of lepl.core.manager.GeneratorRef
#     1  10000   3 10480000  21  20968384  43 dict of 0x846620
#     2  61337  18  4753648  10  25722032  53 tuple
#     3  10505   3  3897560   8  29619592  61 dict (no owner)
#     4  40714  12  3257120   7  32876712  67 types.MethodType
#     5  29645   9  2265384   5  35142096  72 str
#     6  20020   6  1923152   4  37065248  76 unicode
#     7  20596   6  1812448   4  38877696  80 __builtin__.weakref
#     8  10897   3  1466120   3  40343816  83 list
#     9  59638  18  1431312   3  41775128  86 int
#<182 more rows. Type e.g. '_.more' to view.>
#    for i in range(3):
#        print(i, collect(i)) # had very little effect
#        h = hpy()
#        print(h.heap())
    
    p.config.no_memoize()
    pp = p.get_parse_iterable_all()
    print(pp.matcher.tree())
    r = pp(source(10**3)) # keep generators open by not expanding
    print(next(r))
    print(get_count(), get_threshold())
    h = hpy()
    print(h.heap())
#    [49996]
#((343, 9, 3), (700, 10, 10))
#Partition of a set of 335873 objects. Total size = 48802656 bytes.
# Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
#     0  10008   3 10488384  21  10488384  21 dict of lepl.core.manager.GeneratorRef
#     1  10000   3 10480000  21  20968384  43 dict of 0x846390
#     2  61337  18  4753656  10  25722040  53 tuple
#     3  10505   3  3897560   8  29619600  61 dict (no owner)
#     4  40710  12  3256800   7  32876400  67 types.MethodType
#     5  29645   9  2265392   5  35141792  72 str
#     6  20019   6  1922880   4  37064672  76 unicode
#     7  20595   6  1812360   4  38877032  80 __builtin__.weakref
#     8  10897   3  1466120   3  40343152  83 list
#     9  59638  18  1431312   3  41774464  86 int
#<180 more rows. Type e.g. '_.more' to view.>
