
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
The token stream processing works on two levels.

At the source level the incoming data is split into chunks that match the 
token definitions.  The result is a list of the form (ids, contents, offset),
where ids are the possible token IDs, contents is the string (or whatever)
that matched the regex, and offset is the offset into the original data.

At the token level the contents are treated the head for a new stream.

The StreamHelper supplied during configuration should be one appropriate for
un-tokenized processing of the original data.  This is then adapted for
the two levels described above using the classes below. 
'''


class _HelperWrapper(object):
    '''
    Common support for the classes below.
    '''
    def __init__(self, helper):
        self._helper = helper
        
    def to_hash(self, stream, state=None):
        return self._helper.to_hash(stream, state=state)

    def to_kargs(self, head, offset, prefix='', kargs=None):
        return self._helper.to_kargs(head, offset, prefix=prefix, kargs=kargs)

    def format(self, template, head, offset, prefix=''):
        return self._helper.format(template, head, offset, prefix=prefix)
    
    def __repr__(self):
        return repr(self._helper)
    
    def __eq__(self, other):
        return self._helper == other
    
    def __hash__(self):
        return hash(self._helper)
        
        
    
class SourceLevelWrapper(_HelperWrapper):
    '''
    This saves the original data (head) to be used at the next level and 
    delegates all calls to the original helper.
    '''
    
    def __init__(self, head, helper):
        self.head = head
        super(SourceLevelWrapper, self).__init__(helper)
    
    def to_kargs(self, head, offset, prefix='', kargs=None):
        return self.helper.to_kargs(self.head, offset, prefix=prefix, kargs=kargs)

    def format(self, template, head, offset, prefix=''):
        return self.helper.format(template, self.head, offset, prefix=prefix)
    

class TokenLevelWrapper(_HelperWrapper):
    '''
    This saves the offset to the current token so that, together with the head
    stored in `SourceLevelWrapper` helper, it can construct the appropriate kargs.
    '''
    
    def __init__(self, delta, helper):
        self.delta = delta
        super(TokenLevelWrapper, self).__init__(helper)
    
    def to_kargs(self, head, offset, prefix='', kargs=None):
        return self.helper.to_kargs(self._helper.head, self.delta + offset, 
                                    prefix=prefix, kargs=kargs)

    def format(self, template, head, offset, prefix=''):
        return self.helper.format(template, self._helper.head, 
                                  self.delta + offset, prefix=prefix)
        
    def __eq__(self, other):
        try:
            return self.delta == other.delta and self._helper == other
        except AttributeError:
            return False
    
    def __hash__(self):
        return self.delta ^ hash(self._helper)
