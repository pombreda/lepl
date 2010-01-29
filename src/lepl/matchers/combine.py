
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Matchers that combine sub-matchers (And, Or etc).
'''

# pylint: disable-msg=C0103,W0212
# (consistent interfaces)
# pylint: disable-msg=E1101
# (_args create attributes)
# pylint: disable-msg=R0901, R0904, W0142
# lepl conventions

from collections import deque

from lepl.core.parser import tagged
from lepl.matchers.core import Literal
from lepl.matchers.support import OperatorMatcher, coerce_
from lepl.matchers.transform import Transformable
from lepl.support.lib import lmap, format


class _BaseSearch(OperatorMatcher):
    '''
    Support for search (repetition) classes.
    '''
    
    def __init__(self, first, start, stop, rest=None):
        '''
        Subclasses repeat a match between 'start' and 'stop' times, inclusive.
        
        The first match is made with 'first'.  Subsequent matches are made
        with 'rest' (if undefined, 'first' is used).
        '''
        super(_BaseSearch, self).__init__()
        self._arg(first=coerce_(first))
        self._arg(start=start)
        self._arg(stop=stop)
        self._karg(rest=coerce_(first if rest is None else rest))
        
    @staticmethod
    def _cleanup(queue):
        '''
        Utility called by subclasses.
        '''
        for (_count, _acc, _stream, generator) in queue:
            generator.close()
        
        
class DepthFirst(_BaseSearch):
    '''
    (Post order) Depth first repetition (typically used via `Repeat`).
    '''

    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        stack = deque()
        try:
            stack.append((0, [], stream, self.first._match(stream)))
            while stack:
                (count1, acc1, stream1, generator) = stack[-1]
                extended = False
                if self.stop is None or count1 < self.stop:
                    count2 = count1 + 1
                    try:
                        (value, stream2) = yield generator
                        acc2 = acc1 + value
                        stack.append((count2, acc2, stream2, 
                                      self.rest._match(stream2)))
                        extended = True
                    except StopIteration:
                        pass
                if not extended:
                    if count1 >= self.start and \
                            (self.stop is None or count1 <= self.stop):
                        yield (acc1, stream1)
                    stack.pop()
        finally:
            self._cleanup(stack)
        
        
class BreadthFirst(_BaseSearch):
    '''
    (Level order) Breadth first repetition (typically used via `Repeat`).
    '''
    
    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        queue = deque()
        try:
            queue.append((0, [], stream, self.first._match(stream)))
            while queue:
                (count1, acc1, stream1, generator) = queue.popleft()
                if count1 >= self.start and \
                        (self.stop is None or count1 <= self.stop):
                    yield (acc1, stream1)
                count2 = count1 + 1
                try:
                    while True:
                        (value, stream2) = yield generator
                        acc2 = acc1 + value
                        if self.stop is None or count2 <= self.stop:
                            queue.append((count2, acc2, stream2, 
                                          self.rest._match(stream2)))
                except StopIteration:
                    pass
        finally:
            self._cleanup(queue)
            

class OrderByResultCount(OperatorMatcher):
    '''
    Modify a matcher to return results in length order.
    '''
    
    def __init__(self, matcher, ascending=True):
        super(OrderByResultCount, self).__init__()
        self._arg(matcher=coerce_(matcher, Literal))
        self._karg(ascending=ascending)
        
    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        generator = self.matcher._match(stream)
        results = []
        try:
            while True:
                # syntax error if this on one line?!
                result = yield generator
                results.append(result)
        except StopIteration:
            pass
        for result in sorted(results,
                             key=lambda x: len(x[0]), reverse=self.ascending):
            yield result

                
class _BaseCombiner(Transformable):
    '''
    Support for `And` and `Or`.
    '''
    
    def __init__(self, *matchers):
        super(_BaseCombiner, self).__init__()
        self._args(matchers=lmap(coerce_, matchers))
        
    def compose(self, transform):
        '''
        Generate a new instance with the composed function from the Transform.
        '''
        copy = type(self)(*self.matchers)
        copy.function = self.function.compose(transform.function)
        return copy
    
    def __str__(self):
        return format('{0}({1})', self.__class__.__name__,
                      ', '.join(map(lambda x: x._name, self.matchers)))


class And(_BaseCombiner):
    '''
    Match one or more matchers in sequence (**&**).
    It can be used indirectly by placing ``&`` between matchers.
    '''
    
    @tagged
    def _match(self, stream_in):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  Results from the different matchers are
        combined together as elements in a list.
        '''
        if self.matchers:
            stack = deque([([], 
                            self.matchers[0]._match(stream_in), 
                            self.matchers[1:])])
            append = stack.append
            pop = stack.pop
            try:
                while stack:
                    (result, generator, matchers) = pop()
                    try:
                        (value, stream_out) = yield generator
                        append((result, generator, matchers))
                        if matchers:
                            append((result+value, 
                                    matchers[0]._match(stream_out), 
                                    matchers[1:]))
                        else:
                            yield self.function(result+value, stream_in, 
                                                stream_out)
                    except StopIteration:
                        pass
            finally:
                for (result, generator, matchers) in stack:
                    generator.close()


class Or(_BaseCombiner):
    '''
    Match one of the given matchers (**|**).
    It can be used indirectly by placing ``|`` between matchers.
    
    Matchers are tried from left to right until one succeeds; backtracking
    will try more from the same matcher and, once that is exhausted,
    continue to the right.  String arguments will be coerced to 
    literal matches.
    '''
    
    @tagged
    def _match(self, stream_in):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will correspond to one of the
        sub-matchers (starting from the left).
        '''
        for matcher in self.matchers:
            generator = matcher._match(stream_in)
            try:
                while True:
                    (results, stream_out) = (yield generator)
                    yield self.function(results, stream_in, stream_out)
            except StopIteration:
                pass


class First(_BaseCombiner):
    '''
    Match the first successful matcher only (**%**).
    It can be used indirectly by placing ``%`` between matchers.
    Note that backtracking for the first-selected matcher will still occur.

    Matchers are tried from left to right until one succeeds; backtracking
    will try more from the same matcher (only).  String arguments will be 
    coerced to literal matches.
    '''
    
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will correspond to one of the
        sub-matchers (starting from the left).
        '''
        matched = False
        for matcher in self.matchers:
            generator = matcher._match(stream)
            try:
                while True:
                    yield (yield generator)
                    matched = True
            except StopIteration:
                pass
            if matched:
                break
            

