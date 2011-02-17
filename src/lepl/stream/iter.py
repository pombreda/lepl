
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
A stream for iterable sources.  Each value in the iteration is considered as 
a line (which makes sense for files, for example, which iterate over lines).

The source is wrapped in a `Cons` object.  This has an attribute `head`
which contains the current line and a method `tail()` which returns another
`Cons` instance, or raise a `StopIteration`.

The stream has the form `(state, helper)`, where `helper` is an 
`IterableHelper` instance, as described below.

The `state` value in the stream described above has the form
`(cons, line_stream)` where `cons` is a `Cons` instance and line_stream
is a stream generated from `cons.head` (so has the structure (state', helper')
where state' and helper' depend on the type of the line and the stream factory
used).

Evaluation of stream methods then typically has the form:
- call to IterableHelper
- unpacking of state
- delegation to line_stream
- possible exception handling 

This has the  advantages of being generic in the type returned by the
iterator, of being customizable (by specifying a new factory), and re-using
existing code where possible (in the use of the sub-helper).  It should even
be possible to have iterables of iterables...
'''

from lepl.support.lib import HashedValue
from lepl.stream.simple import OFFSET, LINENO
from lepl.stream.core import s_offset, StreamHelper, s_kargs, s_format, \
    s_debug, s_next, s_line


class Cons(object):
    
    def __init__(self, iterable):
        self.head = next(iterable)
        self._iterable = iterable
        
    def tail(self):
        return Cons(self.iterable) 


class IterableHelper(StreamHelper):
    
    def hash(self, state):
        (_, line_stream) = state
        offset = s_offset(line_stream)
        return HashedValue(offset, (state, self), self._sequence)
    
    def kargs(self, state, prefix='', kargs=None):
        (_, line_stream) = state
        return s_kargs(line_stream, prefix=prefix, kargs=kargs)

    def format(self, state, template, prefix='', kargs=None):
        (_, line_stream) = state
        return s_format(line_stream, template, prefix=prefix, kargs=kargs)
    
    def debug(self, state):
        (_, line_stream) = state
        return s_debug(line_stream)
    
    def next(self, state, count=1):
        (cons, line_stream) = state
        try:
            return s_next(line_stream, count=count)
        except StopIteration:
            # the general approach here is to take what we can from the
            # current line, create the next, and take the rest from that.
            # of course, that may also not have enough, in which case it
            # will recurse.
            (line, end_line_stream) = s_line(line_stream)
            # create next stream
            cons = cons.tail()
            delta = end_line_stream._delta
            delta = (delta[OFFSET], delta[LINENO]+1, 1)
            next_line_stream = self._factory(cons.head, factory=self._factory,
                                             delta=delta, max=self._max, 
                                             global_kargs=self._global_kargs)
            next_stream = ((cons, next_line_stream), self)
            (extra, final_stream) = s_next(next_stream, count=count-len(line))
            value = line_stream.join(line, extra)
            return (value, final_stream)
    
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
    
    def offset(self, state):
        '''
        Return the 0-based offset of the current point, relative to the 
        entire stream. 
        '''
        raise NotImplementedError

    
    def _fmt(self, sequence, offset, maxlen=60, left='', right='', index=True):
        '''Format a possibly long subsection of data.'''
        if not sequence:
            if index:
                return format('{0!r}[{1:d}]', sequence, offset)
            else:
                return format('{0!r}', sequence)
        if offset >= 0 and offset < len(sequence):
            centre = offset
        elif offset > 0:
            centre = len(sequence) - 1
        else:
            centre = 0
        begin, end = centre, centre+1
        longest = None
        while True:
            if begin > 0:
                if end < len(sequence):
                    template = '{0!s}...{1!s}...{2!s}'
                else:
                    template = '{0!s}...{1!s}{2!s}'
            else:
                if end < len(sequence):
                    template = '{0!s}{1!s}...{2!s}'
                else:
                    template = '{0!s}{1!s}{2!s}'
            body = repr(sequence[begin:end])[len(left):]
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
            if begin < 0 and end > len(sequence):
                return longest
            begin = max(begin, 0)
            end = min(end, len(sequence))
                
    def _location(self, kargs, prefix):
        '''Location (separate method so subclasses can replace).'''
        return format('offset {' + prefix + 'global_offset}, value {' + prefix + 'repr}',
                      **kargs)
    
    def _typename(self, instance):
        if isinstance(instance, list) and instance:
            return format('<list{0}>', self._typename(instance[0]))
        else:
            try:
                return format('<{0}>', instance.__class__.__name__)
            except:
                return '<unknown>'
    
    def kargs(self, state, prefix='', kargs=None):
        '''
        Generate a dictionary of values that describe the stream.  These
        may be extended by subclasses.  They are provided to 
        `syntax_error_kargs`, for example.
        
        Note: Calculating this can be expensive; use only for error messages,
        not debug messages (that may be discarded).
        
        Implementation note: Because some values are 
        '''
        offset = state + self._delta[OFFSET]
        if kargs is None: kargs = {}
        add_defaults(kargs, self._kargs, prefix=prefix)
        within = offset > -1 and offset < len(self._sequence)
        data = self._fmt(self._sequence, state)
        text = self._fmt(self._sequence, state, index=False)
        # some values below may be already present in self._global_kargs
        defaults = {'data': data,
                    'global_data': data,
                    'text': text,
                    'global_text': text,
                    'offset': state,
                    'global_offset': offset,
                    'rest': self._fmt(self._sequence[offset:], 0, index=False),
                    'repr': repr(self._sequence[offset]) if within else '<EOS>',
                    'str': str(self._sequence[offset]) if within else '',
                    'lineno': 1,
                    'char': offset+1}
        add_defaults(kargs, defaults, prefix=prefix)
        add_defaults(kargs, {prefix + 'location': self._location(kargs, prefix)})
        return kargs
    
    def next(self, state, count=1):
        new_state = state+count
        if new_state <= len(self._sequence):
            self._max(self._delta[OFFSET] + new_state)
            return (self._sequence[state:new_state], (new_state, self))
        else:
            raise StopIteration
    
    def join(self, *values):
        assert values, 'Cannot join zero general sequences'
        result = values[0]
        for value in values[1:]:
            result += value
        return result
    
    def empty(self, state):
        return state >= len(self._sequence)
    
    def line(self, state):
        '''Returns the rest of the data.'''
        new_state = len(self._sequence)
        if state < new_state:
            self._max(self._delta[OFFSET] + new_state)
            return (self._sequence[state:new_state], (new_state, self))
        else:
            raise StopIteration
    
    def stream(self, state, value):
        return self._factory(value, factory=self._factory,
                             delta=(state+self._delta[0],) + self._delta[1:],
                             max=self._max, global_kargs=self._global_kargs)
        
    def deepest(self):
        return (int(self._max) - self._delta[OFFSET], self)
    
    def debug(self, state):
        try:
            return format('{0:d}:{1:r}', state, self._sequence[state])
        except IndexError:
            return format('{0:d}:<EOS>', state)
