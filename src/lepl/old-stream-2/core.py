
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

from abc import ABCMeta
from io import IOBase

from lepl.support.lib import basestring, str, format


class HashedStream(object):
    '''
    Used to store a reference to the stream.  This assumes that the helper
    and offset together uniquely identify the stream and location.
    '''
    
    __slots__ = ['stream', 'state']
    
    def __init__(self, stream, state):
        self.stream = stream
        self.state = state
        
    def __hash__(self):
        (_, offset, helper) = self.stream
        return offset ^ hash(helper) ^ hash(self.state)
    
    def __eq__(self, other):
        (_, offset1, helper1) = self.stream
        (_, offset2, helper2) = other.stream
        return offset1 == offset2 and helper1 == helper2 and other.state == self.state


#class _SimpleStream(metaclass=ABCMeta):
# Python 2.6
# pylint: disable-msg=W0105, C0103
_StreamHelper = ABCMeta('_StreamHelper', (object, ), {})
'''ABC used to identify streams.'''

DUMMY_HELPER = object()
'''Allows tests to specify an arbitrary helper in results.'''
    

class StreamHelper(_StreamHelper):
    '''
    The interface that all helpers should implement.
    
    A helper contains state related to the source and provides stream-related
    services that use that information (eg. formatting).  Is it part of a
    stream tuple (head, offset, helper).
    
    This "ugly" design was chosen for Lepl 5; previously the stream was a 
    complex object that "wrapped" the underlying stream.  The advantages of the
    new approach are that:
    - In simple cases, a single helper and head instance are used, only the
      offset changes.  This is more efficient.
    - In simple cases we avoid the complex wrapper object, which was hard to
      extend and bug-prone.
    - There is a cleaner separation of responsibilities between the stream
      and the source.
    - In-memory streams are more efficient.
    The disadvantages are:
    - Very large streams will require extra, complex code.
    - Matchers need to "unpack" streams
    '''
    
    def to_hash(self, stream, state=None):
        '''
        Generate an object that can be hashed (implements __hash__ and __eq__),
        (_, offset, helper) = self.stream
        that reflects the current state of the stream, and that evaluates
        to give the stream.
        '''
        return HashedStream(stream, state)
    
    def to_kargs(self, head, offset, prefix='', kargs=None):
        '''
        Generate a dictionary of values that describe the stream.  These
        may be extended by subclasses.  They are provided to 
        `syntax_error_kargs`, for example.
        
        `prefix` modifies the property names
        
        `kargs` allows values to be provided.  These are *not* overwritten,
        so if there is a name clash the provided value remains.
        
        Note: Calculating this can be expensive; use only for error messages,
        not debug messages (that may be discarded).
        '''
        raise NotImplementedError()

    def format(self, template, head, offset, prefix=''):
        return format(template, **self.to_kargs(head, offset, prefix))
    
    def __repr__(self):
        '''Simplify for comparison in tests'''
        return '<helper>'
    
    def __eq__(self, other):
        return other is DUMMY_HELPER or super(StreamHelper, self).__eq__(other)
    
    def __hash__(self):
        return super(StreamHelper, self).__hash__()


class SimpleHelper(StreamHelper):
    
    def to_hash(self, stream, state=None):
        '''
        Generate an object that can be hashed (implements __hash__ and __eq__),
        (_, offset, helper) = self.stream
        that reflects the current state of the stream, and that evaluates
        to give the stream.
        '''
        return HashedStream(stream, state)
    
    def _fmt(self, head, offset, maxlen=60, left='', right='', index=True):
        '''Format a possibly long subsection of data.'''
        if not head:
            if index:
                return format('{0!r}[{1:d}]', head, offset)
            else:
                return format('{0!r}', head)
        if offset >= 0 and offset < len(head):
            centre = offset
        elif offset > 0:
            centre = len(head) - 1
        else:
            centre = 0
        begin, end = centre, centre+1
        longest = None
        while True:
            if begin > 0:
                if end < len(head):
                    template = '{0!s}...{1!s}...{2!s}'
                else:
                    template = '{0!s}...{1!s}{2!s}'
            else:
                if end < len(head):
                    template = '{0!s}{1!s}...{2!s}'
                else:
                    template = '{0!s}{1!s}{2!s}'
            body = repr(head[begin:end])[len(left):]
            if len(right):
                body = body[:-len(right)]
            text = format(template, left, body, right, offset)
            if index:
                text = format('{0!s}[{1:d}:]', text, offset)
            if longest is None or len(text) <= maxlen:
                longest = text
            if len(text) > maxlen:
                return longest
            begin -= 1
            end += 1
            if begin < 0 and end > len(head):
                return longest
            begin = max(begin, 0)
            end = min(end, len(head))
                
    def _location(self, head, offset, kargs, prefix):
        '''Location (separate method so subclasses can replace).'''
        return format('offset {' + prefix + 'offset}, value {' + prefix + 'repr}',
                      **kargs)
    
    def _unwrap(self, head):
        from lepl.stream.maxdepth import Facade
        if isinstance(head, Facade):
            head = head.head
        return head
    
    def _update(self, kargs, defaults):
        for (name, value) in defaults.items():
            if name not in kargs:
                kargs[name] = value
                
    def _typename(self, instance):
        if isinstance(instance, list) and instance:
            return format('<list{0}>', self._typename(instance[0]))
        else:
            try:
                return format('<{0}>', instance.__class__.__name__)
            except:
                return '<unknown>'
    
    def to_kargs(self, head, offset, prefix='', kargs=None):
        '''
        Generate a dictionary of values that describe the stream.  These
        may be extended by subclasses.  They are provided to 
        `syntax_error_kargs`, for example.
        
        Note: Calculating this can be expensive; use only for error messages,
        not debug messages (that may be discarded).
        
        Implementation note: Because some values are 
        '''
        if kargs is None: kargs = {}
        head = self._unwrap(head)
        type_ = self._typename(head)
        within = offset > -1 and offset < len(head)
        defaults = {# the entire dataset, highlighting the data at the offset
                    prefix + 'data': self._fmt(head, offset),
                    # as `data` but without the indexing
                    prefix + 'text': self._fmt(head, offset, index=False),
                    # data from the offset onwards
                    prefix + 'rest': self._fmt(head[offset:], 0, index=False),
                    # a filename (set by the filename specific subclass) or type
                    prefix + 'filename': type_,
                    # current line number (1-based)
                    prefix + 'lineno': 1,
                    # character offset in line (1-based)
                    prefix + 'char': offset+1,
                    # offset from start (0-based)
                    prefix + 'offset': offset,
                    # repr of current value
                    prefix + 'repr': repr(head[offset]) if within else '<EOS>',
                    # str of current value
                    prefix + 'str': str(head[offset]) if within else '',
                    # type of stream
                    prefix + 'type': type_}
        self._update(kargs, defaults)
        self._update(kargs, {prefix + 'location': 
                             self._location(head, offset, kargs, prefix)})
        return kargs
        
    
class StringHelper(SimpleHelper):
    '''
    String-specific formatting
    '''
    
    def _data(self, head, offset):
        return super(StringHelper, self)._fmt(head, offset, left="'", right="'")
        
    def _location(self, head, offset, kargs, prefix):
        return format('line {' + prefix + 'lineno:d}, character {' + prefix + 'char:d}', **kargs)
        
    def to_kargs(self, head, offset, prefix='', kargs=None):
        if kargs is None: kargs = {}
        head = self._unwrap(head)
        lineno = 1
        for line in head.split('\n'):
            delta = len(line) + 1
            if offset > delta:
                offset -= delta
                lineno += 1
            else:
                break
        self._update(kargs, {prefix + 'filename': '<string>',
                             prefix + 'line': line,
                             prefix + 'rest': repr(line[offset:]),
                             prefix + 'lineno': lineno,
                             prefix + 'char': offset+1})
        return super(StringHelper, self).to_kargs(
                    head, offset, prefix=prefix, kargs=kargs)
            

class StreamFactory(object):
    '''
    Given an input (usually head), generate a stream.
    '''
    
    def __call__(self, head, helper=None):
        '''
        The kargs are passed from the "parse" method.
        '''
        if helper is None:
            helper = SimpleHelper()
        return (head, 0, helper)
    
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
    
    def from_string(self, text, helper=None):
        '''
        Provide a stream for the contents of the string.
        '''
        if helper is None:
            helper = StringHelper()
        return self(text, helper=helper)

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
