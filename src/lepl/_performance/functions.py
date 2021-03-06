
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
Performance related tests, based on a request on the mailing list.

Currently shows that full memoisation isn't worth the overhead (in this
particular case).

Original input:
Namespace(alpha=0.10000000000000001, decim_phase=0, delta=1.0000000000000001e-05, epsilon=0, errors=100, esnodB=13.07, fftsize=1024, filter_type='none', freq=0, initial_error=0, logname='test_btr_equal_coded.py.nbecker6.3204d546abd8e4b8fbf5243c8e9fc184.err', loop_gain=0.0001, max_hours=12.0, max_iter=13, mod='16apsk', notch=False, order=7, print_time=30, rate='8/9', si=32, size=16200, sps=2.2727270000000002, symbol_rate=220000000.0, taps=25, tau=0, tolerance=0, wait_converge=2000, wait_mse=None, wait_stable=1000)\n

'''

from logging import basicConfig, DEBUG
from random import choice, random
from string import ascii_letters, ascii_lowercase

from lepl import *

# need to generate random input because memoisation trivially handles
# repeated calls with same input
lines = []
for i in range(1000):
    values = []
    for j in range(10):
        name = ''.join(choice(ascii_lowercase) for k in range(6))
        type_ = choice(range(3))
        if type_ == 0:
            value = choice(['False', 'True', 'None'])
        elif type_ == 1:
            value = "'" + ''.join(choice(ascii_letters) for k in range(10)) + "'"
        else:
            value = str(random() * 10)
        values.append(name + '=' + value)
    lines.append('Namespace(' + ', '.join(values) + ')')
text = '\n'.join(lines)
#print(text)

#basicConfig(level=DEBUG)

def combine(dicts):
    return dict((d['name'], d['value']) for d in dicts)

name  = Word(ascii_letters + '_') > 'name'
value = (String(quote="'") | Float() | 'False' | 'True' | 'None') > 'value'
arg   = (name & '=' & value) > make_dict
line  = Drop('Namespace(') & arg[1:,Drop(', ')] & Drop(')') > combine
parser = line[1:, '\n']

parser.config.no_full_first_match()
default_parser = parser.get_parse_string()

parser.config.clear()
clear_parser = parser.get_parse_string()

parser.config.default().auto_memoize(full=False).no_full_first_match()
parser_1 = parser.get_parse_string()

parser.config.default().auto_memoize(full=True).no_full_first_match()
parser_2 = parser.get_parse_string()

#print(default_parser.matcher, '\n')
#print(clear_parser.matcher, '\n')
#print(repr(parser_1.matcher), '\n')
#print(repr(parser_2.matcher), '\n')

def default(): assert default_parser(text)
def clear(): assert clear_parser(text)
def parser1(): assert parser_1(text)
def parser2(): assert parser_2(text)


def time():
    from timeit import Timer
    n = 1
    
    # 13.0672681332
    print(Timer("default()", "from __main__ import default").timeit(number=n))
    
    # 18.382144928
    print(Timer("clear()", "from __main__ import clear").timeit(number=n))
    
    # 12.6545679569
    print(Timer("parser1()", "from __main__ import parser1").timeit(number=n))
    
    # 31.0624670982
    print(Timer("parser2()", "from __main__ import parser2").timeit(number=n))



if __name__ == '__main__':
    time()
    #result = default_parser(text)
    #print(result)

    
    