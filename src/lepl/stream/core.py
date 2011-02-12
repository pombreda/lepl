
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
- head must support __getitem__ operations (including -ve indices!)
- head must support len()
- offset is an integer
- helper is an instance of StreamHelper, defined below
- head[offset] is the current "character" to be parsed
'''

from io import IOBase

from lepl.support.lib import basestring, str, format


class HashedStream(object):
    '''
    Used to store a reference to the stream.  This assumes that the helper
    and offset together uniquely identify the stream and location.
    '''
    
    __slots__ = ['stream']
    
    def __init__(self, stream):
        self.stream = stream
        
    def __hash__(self):
        (_, offset, helper) = self.stream
        return offset ^ hash(helper)
    
    def __eq__(self, other):
        (_, offset1, helper1) = self.stream
        (_, offset2, helper2) = other.stream
        return offset1 == offset2 and helper1 == helper2
    

class StreamHelper(object):
    
    def to_hash(self, stream):
        '''
        Generate an object that can be hashed (implements __hash__ and __eq__),
        (_, offset, helper) = self.stream
        that reflects the current state of the stream, and that evaluates
        to give the stream.
        '''
        return HashedStream(stream)
    
    def to_str(self, head, offset):
        if offset < 3:
            base = (str(head[0:2]) + '...') if len(head) > 3 else str(head)
            return format('{0}[{1:d}:]', base, offset)
        elif offset > len(head)-2:
            return format('{0!r}...{1!r}[{2:d}:]', head[0:1], head[-3:], offset)
        else:
            return format('{0!r}...{1!r}...[{2:d}:]', head[0:1], head[offset:offset+2], offset)
    
    def to_location(self, head, offset):
        return format('index {0:d}, {1!r}', offset, head[offset])
    
    def __repr__(self):
        return '<helper>'
    

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
    
    def from_items(self, items, sub_list=True):
        '''
        Provide a stream for the contents of an iterator over items.
        
        The `sub_list` causes each each item to be wrapped in a list.  This 
        may seem unusual but is typically what is needed, because it makes the
        items resemble strings.  In particular, it allows single values to
        be joined with `+`.
        
        To understand further, compare "123" and [1,2,3].  The components of
        the former are "1", "2" and "3', which can be joined with `+` as
        expected.  However, the components of the latter are 1, 2, and 3 which
        will "join" to give "6" instead of "123".  This is avoided if we
        wrap in lists: [[1],[2],[3]] has components [1], [2], [3] which join
        to give [1,2,3] as likely expected.  
        '''
        if sub_list:
            items = ([item] for item in items)
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
