
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

A stream is a tuple (state, helper), where `state` will vary from location to 
location, while `helper` is an "unchanging" instance of `StreamHelper`, 
defined below.

For simple streams state can be a simple integer and this approach avoids the
repeated creation of objects.  More complex streams may choose to not use
the state at all, simply creating a new helper at each point.
'''

from abc import ABCMeta

from lepl.support.lib import format


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
    '''
    
    def __repr__(self):
        '''Simplify for comparison in tests'''
        return '<helper>'
    
    def __eq__(self, other):
        return other is DUMMY_HELPER or super(StreamHelper, self).__eq__(other)
    
    def __hash__(self):
        return super(StreamHelper, self).__hash__()

    def hash(self, state):
        '''
        Generate an object that can be hashed (implements __hash__ and __eq__),
        and whose value attribute contains the stream (ie is the tuple 
        (state, helper)).  See `HashedValue`.
        '''
        raise NotImplementedError
    
    def kargs(self, state, prefix='', kargs=None):
        '''
        Generate a dictionary of values that describe the stream.  These
        may be extended by subclasses.  They are provided to 
        `syntax_error_kargs`, for example.
        
        `prefix` modifies the property names
        
        `kargs` allows values to be provided.  These are *not* overwritten,
        so if there is a name clash the provided value remains.
        
        Note: Calculating this can be expensive; use only for error messages,
        not debug messages (that may be discarded).
        
        The following names will be defined (at a minimum).
        
        For these value the "global" prefix indicates the underlying stream 
        when, for example, tokens are used (other values will be relative to 
        the token).  If tokens etc are not in use then global and non-global 
        values will agree.
        - data: a line representing the data, highlighting the current offset
        - global_data: as data, but for the entire sequence
        - text: as data, but without a "[...]" at the end
        - global_text: as text, but for the entire sequence
        - type: the type of the sequence
        - global_type: the type of the entire sequence
        - offset: a 0-based index into the sequence
        - global_offset: a 0-based index into the underlying sequence

        These values are always local:
        - rest: the data following the current point
        - repr: the current value, or <EOS>
        - str: the current value, or an empty string
        
        These values are always global:
        - filename: a filename, if available, or the type
        - lineno: a 1-based line number for the current offset
        - char: a 1-based character count within the line for the current offset
        - location: a summary of the current location
        '''
        raise NotImplementedError

    def format(self, state, template, prefix='', kargs=None):
        '''Format a message using the expensive kargs function.'''
        return format(template, **self.kargs(state, prefix=prefix, kargs=kargs))
    
    def debug(self, state):
        '''Generate an inexpensive debug message.'''
        raise NotImplementedError
    
    def next(self, state, count=1):
        '''
        Return (value, stream) where `value` is the next value (or 
        values if count > 1) from the stream and `stream` is advanced to the
        next character.  Note that `value` is always a sequence (so if the 
        stream is a list of integers, and `count`=1, then it will be a 
        unitary list, for example).
        
        Should raise StopIteration when no more data are available.
        '''
        raise StopIteration
    
    def join(self, *values):
        '''
        Join sequences of values into a single sequence.
        '''
        raise NotImplementedError
    
    def empty(self, state):
        '''
        Return true if no more data available.
        '''
        raise NotImplementedError
    
    def line(self, state):
        '''
        Return (values, stream) where `values` correspond to something
        like "the rest of the line" from the current point and `stream`
        is advanced to the point after the line ends.
        '''
        raise NotImplementedError
    
    def stream(self, state, value):
        '''
        Return a new stream that encapsulates the value given, starting at
        `state`.  IMPORTANT: the stream used is the one that corresponds to
        the start of the line.
          
        For example:
            (line, next_stream) = s_line(stream)
            token_stream = s_stream(stream, line) # uses stream, not next_stream
         
        This is used when processing Tokens, for example, or columns (where
        fragments in the correct column area are parsed separately).
        '''
        raise NotImplementedError
    
    def deepest(self):
        '''
        Return a stream that represents the deepest match.  The stream may be
        incomplete in some sense (it may not be possible to use it for
        parsing more data), but it will have usable format and kargs methods.
        '''
        raise NotImplementedError


# The following are helper functions that allow the methods above to be
# called on (state, helper) tuples

s_hash = lambda stream: stream[1].hash(stream[0])
'''Invoke helper.hash(state)'''

s_kargs = lambda stream, prefix='', kargs=None: stream[1].kargs(stream[0], prefix=prefix, kargs=kargs)
'''Invoke helper.kargs(state, prefix, kargs)'''

s_format = lambda stream, template, prefix='', kargs=None: stream[1].format(stream[0], template, prefix=prefix, kargs=kargs)
'''Invoke helper.format(state, template, prefix, kargs)'''

s_next = lambda stream, count=1: stream[1].next(stream[0], count=count)
'''Invoke helper.next(state, count)'''

s_join = lambda stream, *values: stream[1].join(*values)
'''Invoke helper.join(*values)'''

s_empty = lambda stream: stream[1].empty(stream[0])
'''Invoke helper.empty(state)'''

s_line = lambda stream: stream[1].line(stream[0])
'''Invoke helper.line(state)'''

s_stream = lambda stream, value: stream[1].stream(stream[0], value)
'''Invoke helper.stream(state, value)'''

s_debug = lambda stream: stream[1].debug()
'''Invoke helper.debug()'''
