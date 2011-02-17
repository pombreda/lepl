
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


from collections import Iterable

from lepl.stream.simple import SequenceHelper, StringHelper, ListHelper
from lepl.support.lib import basestring, format, add_defaults


class StreamFactory(object):
    '''
    Given a value (typically a sequence), generate a stream.
    '''
    
    def from_string(self, text, **kargs):
        '''
        Provide a stream for the contents of the string.
        '''
        add_defaults(kargs, {'factory': self})
        return (0, StringHelper(text, **kargs))

    def from_list(self, list_, **kargs):
        '''
        Provide a list for the contents of the string.
        '''
        add_defaults(kargs, {'factory': self})
        return (0, ListHelper(list_, **kargs))

    def from_sequence(self, sequence, **kargs):
        '''
        Return a generic stream.
        '''
        add_defaults(kargs, {'factory': self})
        return (0, SequenceHelper(sequence, **kargs))

    def from_iterable(self, iterable, helper=None):
        pass
        # TODO
        
        
    
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
    
    def __call__(self, sequence, **kargs):
        '''
        Auto-detect type and wrap appropriately.
        '''
        if isinstance(sequence, basestring):
            return self.from_string(sequence, **kargs)
        elif isinstance(sequence, list):
            return self.from_list(sequence, **kargs)
        elif hasattr(sequence, '__getitem__') and hasattr(sequence, '__len__'):
            return self.from_sequence(sequence, **kargs)
        elif isinstance(sequence, Iterable):
            return self.from_iterable(sequence, **kargs)
        else:
            raise TypeError(format('Cannot generate a stream for type {0}',
                                   type(sequence)))

DEFAULT_STREAM_FACTORY = StreamFactory()
