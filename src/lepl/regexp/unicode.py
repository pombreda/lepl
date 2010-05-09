
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
A regexp implementation for unicode strings.
'''

from sys import maxunicode

from lepl.regexp.str import StrAlphabet, ILLEGAL
from lepl.support.lib import chr

class UnicodeAlphabet(StrAlphabet):
    '''
    An alphabet for unicode strings.
    '''
    
    __cached_instance = None
    
    # pylint: disable-msg=E1002
    # (pylint bug?  this chains back to a new style abc)
    def __init__(self):
        from lepl.matchers.core import Any
        from lepl.matchers.derived import Drop
        max_ = chr(maxunicode)
        def n_hex(char, n):
            return Drop(Any(char)) + Any('0123456789abcdefABCDEF')[n,...] >> \
                        (lambda x: chr(int(x, 16)))
        simple = Any(ILLEGAL)
        escaped = simple | n_hex('x', 2) | n_hex('u', 4) | n_hex('U', 8)
        super(UnicodeAlphabet, self).__init__(chr(0), max_, escaped=escaped)
        
    def before(self, char):
        '''
        Must return the character before char in the alphabet.  Never called 
        with min (assuming input data are in range).
        ''' 
        return chr(ord(char)-1)
    
    def after(self, char): 
        '''
        Must return the character after c in the alphabet.  Never called with
        max (assuming input data are in range).
        ''' 
        return chr(ord(char)+1)
    
    @classmethod
    def instance(cls):
        '''
        Get an instance of this alphabet (avoids creating new objects).
        '''
        if cls.__cached_instance is None:
            cls.__cached_instance = UnicodeAlphabet()
        return cls.__cached_instance

    def __repr__(self):
        return '<Unicode>'
    