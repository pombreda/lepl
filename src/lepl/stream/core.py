
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
Default implementations of the stream classes. 

A stream is a tuple (head, offset, helper) with the following requirements:
- head must support basic __slice__ operations
- head must support len()
- offset is an integer
- helper is an instance of StreamHelper, defined below
- head[offset] is the current "character" to be parsed
'''

from io import IOBase

from lepl.support.lib import basestring


class HashedThunk(object):
    '''
    Used to store a reference to the stream.  This assumes that the helper
    and offset together uniquely identify the stream and location.
    '''
    
    __slots__ = ['_head', '_offset', '_helper']
    
    def __init__(self, head, offset, helper):
        self._head = head
        self._offset = offset
        self._helper = helper
        
    def __hash__(self):
        return self._offset ^ hash(self._helper)
    
    def __eq__(self, other):
        return other._head == self._head and other._helper == self._helper
    
    def __call__(self):
        return (self._head, self._offset, self._helper)
    

class StreamHelper(object):
    
    def hashed_thunk(self, head, offset):
        '''
        Generate an object that can be hashed (implements __hash__ and __eq__),
        that reflects the current state of the stream, and that evaluates
        to give the stream.
        '''
        return HashedThunk(self, head, offset)
    

class StreamFactory(object):
    '''
    Given an input (usually head), generate a stream.
    '''
    
    def __call__(self, head, **kargs):
        '''
        The kargs are passed from the "parse" method.
        '''
        return (head, 0, StreamHelper())
    
    def from_file(self, file_):
        '''
        Provide a stream for the contents of the file.
        '''
        return self.from_lines(file_.readlines())
            
    def from_path(self, path):
        '''
        Provide a stream for the contents of the file at the given path.
        '''
        with open(path) as file_:
            stream = self.from_file(file_)
        return stream
    
    def from_string(self, text):
        '''
        Provide a stream for the contents of the string.
        '''
        return self(text)

    def from_lines(self, lines, join='\n'.join):
        '''
        Provide a stream for the contents of an iterator over lines.
        '''
        return self.auto(join(lines))
    
    def from_items(self, items):
        '''
        Provide a stream for the contents of an iterator over items
        (ie characters).
        '''
        return self.auto(list(items))
    
    def from_null(self, head):
        '''
        Return the underlying data with no modification.
        '''
        return self(head)

    def auto(self, head, **kargs):
        '''
        Auto-detect type and wrap appropriately.
        '''
        if isinstance(head, basestring):
            return self.from_string(head, **kargs)
        elif isinstance(head, IOBase):
            # this will use file name attribute if available, then treat as
            # a source of lines
            return self.from_file(head, **kargs)
        else:
            return self.from_null(head, **kargs)

DEFAULT_STREAM_FACTORY = StreamFactory()
