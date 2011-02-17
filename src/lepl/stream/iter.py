
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

from lepl.support.lib import HashedValue, add_defaults
from lepl.stream.simple import OFFSET, LINENO, BaseHelper
from lepl.stream.core import s_delta, s_kargs, s_format, s_debug, s_next, \
    s_line, s_join, s_empty


class Cons(object):
    
    def __init__(self, iterable):
        self.head = next(iterable)
        self._iterable = iterable
        
    def tail(self):
        return Cons(self._iterable) 


class IterableHelper(BaseHelper):
    
    def __init__(self, factory, delta=None, max=None, global_kargs=None):
        super(IterableHelper, self).__init__(factory, delta=delta, max=max, 
                                             global_kargs=global_kargs)
        self._max_line_stream = None
        type_ = '<iterable>'
        add_defaults(self._global_kargs, {
            'global_type': type_,
            'filename': type_})
        self._kargs = dict(self._global_kargs)
        add_defaults(self._kargs, {'type': type_})
        
    def hash(self, state):
        (_, line_stream) = state
        offset = s_delta(line_stream)[OFFSET]
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
    
    def _checkpoint(self, line_stream):
        if self._max_line_stream is None or \
                s_delta(line_stream)[OFFSET] == int(self._max):
            self._max_line_stream = line_stream
    
    def next(self, state, count=1):
        (cons, line_stream) = state
        try:
            (value, next_line_stream) = s_next(line_stream, count=count)
            self._checkpoint(next_line_stream)
            return (value, ((cons, next_line_stream), self))
        except StopIteration:
            # the general approach here is to take what we can from the
            # current line, create the next, and take the rest from that.
            # of course, that may also not have enough, in which case it
            # will recurse.
            cons = cons.tail()
            def next_line(empty_line_stream):
                delta = s_delta(empty_line_stream)
                delta = (delta[OFFSET], delta[LINENO]+1, 1)
                return self._factory(cons.head, factory=self._factory,
                                     delta=delta, max=self._max, 
                                     global_kargs=self._global_kargs)
            if s_empty(line_stream):
                next_line_stream = next_line(line_stream)
                next_stream = ((cons, next_line_stream), self)
                return s_next(next_stream, count=count)
            else:
                (line, end_line_stream) = s_line(line_stream)
                next_line_stream = next_line(end_line_stream)
                next_stream = ((cons, next_line_stream), self)
                (extra, final_stream) = s_next(next_stream, count=count-len(line))
                (_, final_line_stream) = final_stream
                self._checkpoint(final_line_stream)
                value = line_stream.join(line, extra)
                return (value, final_stream)
    
    def join(self, state, *values):
        (_, line_stream) = state
        return s_join(line_stream, *values)
    
    def empty(self, state):
        try:
            self.next(state)
            return False
        except StopIteration:
            return True
    
    def line(self, state):
        (cons, line_stream) = state
        (value, next_line_stream) = s_line(line_stream)
        self._checkpoint(next_line_stream)
        return (value, ((cons, next_line_stream), self))
    
    def stream(self, state, value):
        (cons, line_stream) = state
        next_line_stream = self._factory(value, factory=self._factory,
                                         delta=s_delta(line_stream), max=self._max, 
                                         global_kargs=self._global_kargs)
        return ((cons, next_line_stream), self)
    
    def deepest(self):
        return ((None, self._max_line_stream), self)
    
    def delta(self, state):
        (_, line_stream) = state
        return s_delta(line_stream)
