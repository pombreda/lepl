
'''
Matchers form the basis of the library; they are used to define the grammar
and do the work of parsing the input.

A matcher is like a parser combinator - it takes a stream, matches content in
the stream, and returns a list of tokens and a new stream.  However, matchers
are also generators, so they can be "recalled" to return alternative matches.
This gives backtracking.

Matchers are implemented as both classes (these tend to be the basic building
blocks) and functions (these are typically "syntactic sugar").  I have used
the same syntax (capitalized names) for both to keep the API uniform.

For more background, please see the `manual <../manual/index.html>`_.
'''

from collections import deque
import string
from re import compile
from traceback import print_exc

from lepl.custom import NAMESPACE, Override
from lepl.node import Node, raise_error
from lepl.resources import managed
from lepl.stream import StreamMixin
from lepl.support import assert_type, BaseGeneratorDecorator
from lepl.trace import LogMixin


class BaseMatch(StreamMixin, LogMixin):
    '''
    A base class that provides support to all matchers; most 
    importantly it defines the operators used to combine elements in a 
    grammar specification.
    '''

    def __init__(self):
        super().__init__()
        
    def __add__(self, other):
        '''
        **self + other** - Join strings, merge lists.
        
        Combine adjacent matchers in sequence, merging the result with "+" 
        (so strings are joined, lists merged).
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('+', lambda a, b: Add(And(a, b)))(self, other)

    def __radd__(self, other):
        '''
        **other + self** - Join strings, merge lists.
        
        Combine adjacent matchers in sequence, merging the result with "+" 
        (so strings are joined, lists merged).
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('+', lambda a, b: Add(And(a, b)))(other, self)

    def __and__(self, other):
        '''
        **self & other** - Append results.
        
        Combine adjacent matchers in sequence.  This is equivalent to 
        `lepl.match.And`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('&', And)(self, other) 
        
    def __rand__(self, other):
        '''
        **other & self** - Append results.
        
        Combine adjacent matchers in sequence.  This is equivalent to 
        `lepl.match.And`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('&', And)(other, self) 
    
    def __truediv__(self, other):
        '''
        **self / other** - Append results, with optional separating space.
        
        Combine adjacent matchers in sequence, with an optional space between
        them.  The space is included in the results.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('/', 
                             lambda a, b: 
                             NAMESPACE.get('&', And)(a, Space()[0:,...], b)) \
                             (self, other)
        
    def __rtruediv__(self, other):
        '''
        **other / self** - Append results, with optional separating space.
        
        Combine adjacent matchers in sequence, with an optional space between
        them.  The space is included in the results.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('/', 
                             lambda a, b: 
                             NAMESPACE.get('&', And)(a, Space()[0:,...], b)) \
                             (other, self)
        
    def __floordiv__(self, other):
        '''
        **self // other** - Append results, with required separating space.
        
        Combine adjacent matchers in sequence, with a space between them.  
        The space is included in the results.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('//', 
                             lambda a, b: 
                             NAMESPACE.get('&', And)(a, Space()[1:,...], b)) \
                             (self, other)
        
    def __rfloordiv__(self, other):
        '''
        **other // self** - Append results, with required separating space.
        
        Combine adjacent matchers in sequence, with a space between them.  
        The space is included in the results.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('//', 
                             lambda a, b: 
                             NAMESPACE.get('&', And)(a, Space()[1:,...], b)) \
                             (other, self)
        
    def __or__(self, other):
        '''
        **self | other** - Try alternative matchers.
        
        This introduces backtracking.  Matches are tried from left to right
        and successful results returned (one on each "recall").  This is 
        equivalent to `lepl.match.Or`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('|', Or)(self, other) 
        
    def __ror__(self, other):
        '''
        **other | self** - Try alternative matchers.
        
        This introduces backtracking.  Matches are tried from left to right
        and successful results returned (one on each "recall").  This is 
        equivalent to `lepl.match.Or`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('|', Or)(other, self) 
        
    def __mod__(self, other):
        '''
        **self % other** - Take first match (committed choice).
        
        Matches are tried from left to right and the first successful result
        is returned.  This is equivalent to `lepl.match.First`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('%', First)(self, other) 
        
    def __rmod__(self, other):
        '''
        **other % self** - Take first match (committed choice).
        
        Matches are tried from left to right and the first successful result
        is returned.  This is equivalent to `lepl.match.First`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        return NAMESPACE.get('%', First)(other, self) 
        
    def __invert__(self):
        '''
        **~self** - Discard the result.

        This generates a matcher that behaves as the original, but returns
        an empty list. This is equivalent to `lepl.match.Drop`.
        
        Note that `lepl.match.Lookahead` overrides this method to have
        different semantics (negative lookahead).
        '''
        return NAMESPACE.get('~', Drop)(self) 
        
    def __getitem__(self, indices):
        '''
        **self[start:stop:direction, separator, ...]** - Repetition and lists.
        
        This is a complex statement that modifies the current matcher so
        that it matches several times.  A separator may be specified
        (eg for comma-separated lists) and the results may be combined with
        "+" (so repeated matching of characters would give a word).
        
        start:stop:direction
          This controls the number of matches made and the order in which
          different numbers of matches are returned.
          
          [start]
            Repeat exactly *start* times
            
          [start:stop]
            Repeat *start* to *stop* times (starting with as many matches
            as possible, and then decreasing as necessary).
            
          [start:stop:direction]
            Direction selects the algorithm for searching.  This is
            equivalent to a tree search because at each match we can
            either consume more of the stream (going deeper) or try
            an alternative matcher (by backtracking the sub-matcher)
            (going wider). 
            
            1
              A breadth first search is used, which guarantees that the
              number of matches returned will not decrease (ie will
              monotonically increase) on backtracking.  This tries all
              possible matches for the sub-matcher first (before repeating
              calls to consume more of the stream).
              
            0
              A depth first search is used, which tends to give longer
              matches before shorter ones.  This tries to repeats matches 
              with the sub-matcher, consuming as much of the stream as 
              possible, before backtracking to find alternative matchers.
              If the sub-matcher does not backtrack then this guarantees
              that the number of matches returned will not increase (ie will
              monotonically decrease) on backtracking.
              
            -1
              An exhaustive search is used, which finds all results (by 
              breadth first search) and orders them by length before returning 
              them ordered from longest to shortest.  This guarantees that
              the number of matches returned will not increase (ie will
              monotonically decrease) on backtracking.
            
          Values may be omitted; the defaults are: *start* = 0, *stop* = 
          infinity, *direction* = 0 (depth first search).

        separator
          If given, this must appear between repeated values.  Matched
          separators are returned as part of the result (unless, of course,
          they are implemented with a matcher that returns nothing).  If 
          *separator* is a string it is converted to a literal match.

        ...
          If ... (an ellipsis) is given then the results are joined together
          with "+".           

        Examples
        --------
        
        Any()[0:3,...] will match 3 or less characters, joining them
        together so that the result is a single string.
        
        Word()[:,','] will match a comma-separated list of words.
        
        value[:] or value[0:] or value[0::0] is a "greedy" match that,
        if value does not backtrack, is equivalent to the "*" in a regular
        expression.
        value[::1] is the "non-greedy" equivalent (preferring as short a 
        match as possible) and value[::-1] is greedy even when value does
        provide alternative matches on backtracking.
        '''
        start = 0
        stop = None
        step = 0
        separator = None
        add = False
        if not isinstance(indices, tuple):
            indices = [indices]
        for index in indices:
            if isinstance(index, int):
                start = index
                stop = index
                step = -1
            elif isinstance(index, slice):
                start = index.start if index.start != None else 0
                stop = index.stop if index.stop != None else None
                step = index.step if index.step != None else 0
            elif index == Ellipsis:
                add = True
            elif separator == None:
                separator = index
            else:
                raise TypeError(index)
        return NAMESPACE.get('[]', Repeat)(
            self, start, stop, step, separator, add)
        
    def __gt__(self, function):
        '''
        **self in function** - Process or label the results.
        
        Create a named pair or apply a function to the results.  This is
        equivalent to `lepl.match.Apply`.
        
        :Parameters:
        
          function
            This can be a string or a function.
            
            If a string is given each result is replaced by a 
            (name, value) pair, where name is the string and value is the
            result.
            
            If a function is given it is called with the results as an
            argument.  The return value is used as the new result.  This
            is equivalent to `lepl.match.Apply` with nolist=False.
        '''
        return NAMESPACE.get('>', Apply)(self, function) 
    
    def __rshift__(self, function):
        '''
        **self >> function** - Process or label the results (map).
        
        Create a named pair or apply a function to each result in turn.  
        This is equivalent to `lepl.match.Map`.  It is similar to 
        *self >= function*, except that the function is applied to each 
        result in turn.
        
        :Parameters:
        
          function
            This can be a string or a function.
            
            If a string is given each result is replaced by a 
            (name, value) pair, where name is the string and value is the
            result.
            
            If a function is given it is called with each result in turn.
            The return values are used as the new result.
        '''
        return NAMESPACE.get('>>', Map)(self, function) 
        
    def __mul__(self, function):
        '''
        **self * function** - Process the results (\*args).
        
        Apply a function to each result in turn.  
        This is equivalent to `lepl.match.Apply` with ``args=True``.  
        It is similar to *self > function*, except that the function is 
        applies to multiple arguments (using Python's ``*args`` behaviour).
        
        :Parameters:
        
          function
            A function that is called with the results as arguments.
            The return values are used as the new result.
        '''
        return NAMESPACE.get('*', 
                             lambda a, b: Apply(a, b, args=True)) \
                             (self, function) 
        
    def __pow__(self, function):
        '''
        **self \** function** - Process the results (\**kargs).
        
        Apply a function to keyword arguments
        This is equivalent to `lepl.match.KApply`.
        
        :Parameters:
        
          function
            A function that is called with the keyword arguments described below.
            The return value is used as the new result.

            Keyword arguments:
            
              stream_in
                The stream passed to the matcher.
    
              stream_out
                The stream returned from the matcher.
                
              core
                The core, if streams are being used, else ``None``.
            
              results
                A list of the results returned.
        '''
        return NAMESPACE.get('**', KApply)(self, function) 
    
    def __xor__(self, message):
        '''
        **self ^ message**
        
        Raise a SytaxError.
        
        :Parameters:
        
          message
            The message for the SyntaxError.
        '''
        return NAMESPACE.get('^', 
                             lambda a, b: KApply(a, raise_error(b))) \
                             (self, message) 
        
    
class _Repeat(BaseMatch):
    '''
    Modifies a matcher so that it repeats several times, including an optional
    separator and the ability to combine results with "+" (**[::]**).
    ''' 
    
    def __init__(self, matcher, start=0, stop=None, direction=0, separator=None):
        '''
        Construct the modified matcher.
        
        :Parameters:
        
          matcher
            The matcher to modify (a string is converted to a literal match).
        
          start, stop
            Together these control how many times the matcher will repeat.
          
            If step is positive, repeat *start*, *start+step*, ... times,
            with a maximum number of *stop* repetitions.
            
            If step is negative, repeat *stop*, *stop-step*, ... times
            with a minimum number of *start* repetitions.
            
          direction
            In the presence of global backtracking, repeated matching can
            be performed in a variety of ways.
            This parameter controls the sequence in which the matches are 
            generated.
            The algorithm is selected by an integer:
            
              1 (counts up)
                This selects a breadth first search of possible matches.
                The number of matches increases monotonically (ie. never gets
                smaller).
                
              0 (unpredictable, but tends to count down)
                This selects a depth first search of possible matches.
                In general, larger numbers of matches are found first, but
                it is possible for the number of matches to increase or
                decrease if the sub-matcher backtracks.
                
              -1 (counts down)
                This selects an exhaustive search whose results are then 
                ordered to guarantee that the number of matches decreases
                monotonically (ie never gets larger).
                
                **Warning**: This will recurse indefinitely (until the
                stack is exhausted) *without* returning any value if there 
                is no limit to the number of repetitions via *any possible* 
                combination of repeated matchers.
                
            The default is 0, which approximates the usual "greedy"
            behaviour of regular expressions, but is more predictable (and
            efficient) that the exhaustive search.
            
          separator
            If given, this must appear between repeated values.  Matched
            separators are returned as part of the result (unless, of course,
            they are implemented with a matcher that returns nothing).  If 
            *separator* is a string it is converted to a literal match.
        '''
        super().__init__()
        self.__first = coerce(matcher)
        if separator == None:
            self.__second = self.__first 
        else:
            self.__second = And(coerce(separator, Regexp), self.__first)
        if start == None: start = 0
        assert_type('The start index for Repeat or [...]', start, int)
        assert_type('The stop index for Repeat or [...]', stop, int, none_ok=True)
        assert_type('The index step (direction) for Repeat or [...]', direction, int)
        if start < 0:
            raise ValueError('Repeat or [...] cannot have a negative start.')
        if stop != None and stop < start:
            raise ValueError('Repeat or [...] must have a stop '
                             'value greater than or equal to the start.')
        if abs(direction) > 1:
            raise ValueError('Repeat or [...] must have a step (direction) '
                             'of -1, 0 or 1.')
        self._start = start
        self._stop = stop
        self._direction = direction
        tag = '{0}:{1}:{2}'.format(self._start, self._start, self._direction)
        if separator != None:
            tag += ','
            if isinstance(separator, str):
                tag += repr(separator)
            else:
                try:
                    tag += separator.describe()
                except:
                    tag += str(separator)
        self.tag(tag)
        
    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        if self._direction > 0:
            return self.__breadth_first(stream)
        elif self._direction == 0:
            return self.__depth_first(stream)
        else:
            return self.__exhaustive(stream)
        
    def __breadth_first(self, stream):
        '''
        Implement breadth first, non-greedy matching (zero step).
        '''
        for (_depth, results, stream) in self.__with_breadth(stream):
            yield (results, stream)
                    
    def __with_breadth(self, stream):
        '''
        Implement breadth first, non-greedy matching (zero step).
        '''
        queue = deque()
        if 0 == self._start: yield(0, [], stream)
        queue.append((0, [], stream))
        while queue:
            (count1, acc1, stream1) = queue.popleft()
            count2 = count1 + 1
            for (value, stream2) in self.__matcher(count1)(stream1):
                acc2 = acc1 + value
                if count2 >= self._start and \
                    (self._stop == None or count2 <= self._stop):
                    yield (count2, acc2, stream2)
                if self._stop == None or count2 < self._stop:
                    queue.append((count2, acc2, stream2))

    def __matcher(self, count):
        '''
        Provide the appropriate matcher for a given count.
        '''
        if 0 == count:
            return self.__first
        else:
            return self.__second
        
    def __exhaustive(self, stream):
        '''
        Implement the greedy, exhaustive search matching (negative step).

        The only advantage of this over depth first is that it guarantees
        longest first.
        '''
        all = {}
        for (depth, results, stream) in self.__with_breadth(stream):
            if depth not in all:
                all[depth] = []
            all[depth].append((results, stream))
        for depth in reversed(list(all.keys())):
            for (result, stream) in all[depth]:
                yield (result, stream)
                
    def __depth_first(self, stream):
        '''
        Implement the default, depth first matching (zero step).
        '''
        stack = []
        try:
            stack.append((0, [], stream, self.__matcher(0)(stream)))
            while stack:
                (count1, acc1, stream1, generator) = stack[-1]
                extended = False
                if self._stop == None or count1 < self._stop:
                    count2 = count1 + 1
                    try:
                        (value, stream2) = next(generator)
                        acc2 = acc1 + value
                        stack.append((count2, acc2, stream2, self.__matcher(count2)(stream2)))
                        extended = True
                    except StopIteration:
                        pass
                if not extended:
                    if count1 >= self._start and \
                            (self._stop == None or count1 <= self._stop):
                        yield (acc1, stream1)
                    stack.pop(-1)
        finally:
            for (count, acc, stream, generator) in stack:
                self._debug('Closing %s' % generator)
                generator.close()
                

def Repeat(matcher, start=0, stop=None, direction=0, separator=None, add=False):
    '''
    Extend `lepl.match._Repeat` with `lepl.match.Add` to match the
    functionality required by the [...] syntax in `lepl.match.BaseMatch`.
    '''
    return (Add if add else Identity)(
        _Repeat(matcher, start, stop, direction, separator)).tag('...')
                
                
class And(BaseMatch):
    '''
    Match one or more matchers in sequence (**&**).
    It can be used indirectly by placing ``&`` between matchers.
    '''
    
    def __init__(self, *matchers):
        '''
        Create a matcher for one or more sub-matchers in sequence.

        :Parameters:
        
          matchers
            The patterns which are matched, in turn.  String arguments will
            be coerced to literal matches.
        '''
        super().__init__()
        self.__matchers = [coerce(matcher) for matcher in matchers]

    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  Results from the different matchers are
        combined together as elements in a list.
        '''

        if self.__matchers:
            stack = [([], self.__matchers[0](stream), self.__matchers[1:])]
            try:
                while stack:
                    (result, generator, matchers) = stack.pop(-1)
                    try:
                        (value, stream) = next(generator)
                        stack.append((result, generator, matchers))
                        if matchers:
                            stack.append((result+value, matchers[0](stream), 
                                          matchers[1:]))
                        else:
                            yield (result+value, stream)
                    except StopIteration:
                        pass
            finally:
                for (result, generator, matchers) in stack:
                    generator.close()


class Or(BaseMatch):
    '''
    Match one of the given matchers (**|**).
    It can be used indirectly by placing ``|`` between matchers.
    
    **Note:** This is equivalent to depth first search.  Breadth 
    first search is not supported (partly because the way the parser is
    built using Python's operators doesn't build the flat tree that
    it would require to be useful; partly because I don't yet see
    how it helps).  See `lepl.match.First`.
    '''
    
    def __init__(self, *matchers):
        '''
        Create a matcher for matching one of the given sub-matchers.
        
        :Parameters:
        
          matchers
            They are tried from left to right until one succeeds; backtracking
            will try more from the same matcher and, once that is exhausted,
            continue to the right.  String arguments will be coerced to 
            literal matches.
        '''
        super().__init__()
        self.__matchers = [coerce(matcher) for matcher in matchers]

    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will correspond to one of the
        sub-matchers (starting from the left).
        '''

        for match in self.__matchers:
            for result in match(stream):
                yield result


class First(BaseMatch):
    '''
    Match the first successful matcher only (**%**).
    It can be used indirectly by placing ``%`` between matchers.
    Note that backtracking for the first-selected matcher will still occur.
    '''
    
    def __init__(self, *matchers):
        '''
        Create a matcher for matching one of the given sub-matchers.
        
        :Parameters:
        
          matchers
            They are tried from left to right until one succeeds; backtracking
            will try more from the same matcher and, once that is exhausted,
            continue to the right.  String arguments will be coerced to 
            literal matches.
        '''
        super().__init__()
        self.__matchers = [coerce(matcher) for matcher in matchers]

    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will correspond to one of the
        sub-matchers (starting from the left).
        '''
        matched = False
        for match in self.__matchers:
            for result in match(stream):
                matched = True
                yield result
            if matched: break
            

class Any(BaseMatch):
    '''
    Match a single token in the stream.  
    A set of valid tokens can be supplied.
    '''
    
    def __init__(self, restrict=None):
        '''
        Create a matcher for a single character.
        
        :Parameters:
        
          restrict (optional)
            A list of tokens (or a string of suitable characters).  
            If omitted any single token is accepted.  
            
            **Note:** This argument is *not* a sub-matcher.
        '''
        super().__init__()
        self.tag(repr(restrict))
        self.__restrict = restrict
    
    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will be a single matching 
        character.
        '''
        if stream and (not self.__restrict or stream[0] in self.__restrict):
            yield ([stream[0]], stream[1:])
            
            
class Literal(BaseMatch):
    '''
    Match a series of tokens in the stream (**''**).
    '''
    
    def __init__(self, text):
        '''
        Typically the argument is a string but a list might be appropriate 
        with some streams.
        '''
        super().__init__()
        self.tag(repr(text))
        self.__text = text
    
    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).

        Need to be careful here to use only the restricted functionality
        provided by the stream interface.
        '''
        try:
            if self.__text == stream[0:len(self.__text)]:
                yield ([self.__text], stream[len(self.__text):])
        except IndexError:
            pass
        
        
class Empty(BaseMatch):
    '''
    Match any stream, consumes no input, and returns nothing.
    '''
    
    def __init__(self, name=None):
        super().__init__()
        if name:
            self.tag(name)
    
    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  Match any character and progress to 
        the next.
        '''
        yield ([], stream)

            
class Lookahead(BaseMatch):
    '''
    Tests to see if the embedded matcher *could* match, but does not do the
    matching.  On success an empty list (ie no result) and the original
    stream are returned.
    
    When negated (preceded by ~) the behaviour is reversed - success occurs
    only if the embedded matcher would fail to match.
    '''
    
    def __init__(self, matcher, negated=False):
        '''
        On success, no input is consumed.
        If negated, this will succeed if the matcher fails.  If the matcher is
        a string it is coerced to a literal match.
        '''
        super().__init__()
        self.__matcher = coerce(matcher)
        self.__negated = negated
        if negated:
            self.tag('~')
    
    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        # Note that there is no backtracking here - the 'for' is not repeated.
        if self.__negated:
            for result in self.__matcher(stream):
                return
            yield ([], stream)
        else:
            for result in self.__matcher(stream):
                yield ([], stream)
                return
            
    def __invert__(self):
        '''
        Invert the semantics (this overrides the usual meaning for ~).
        '''
        return Lookahead(self.__matcher, negated=not self.__negated)
            

class Apply(BaseMatch):
    '''
    Apply an arbitrary function to the results of the matcher (**>=**, ***=**).
    
    The function should expect a list and can return any value (it should
    return a list if ``raw=True``).
     
    It can be used indirectly by placing ``>=`` (or ``*=`` to set ``args=True``)
    to the right of the matcher.    
    '''

    def __init__(self, matcher, function, raw=False, args=False):
        '''
        The function will be applied to all the arguments.  If a string is
        given named pairs will be created.
        
        **Note:** The creation of named pairs (when a string argument is
        used) behaves more like a mapping than a single function invocation.
        If several values are present, several pairs will be created.
        
        **Note:** There is an asymmetry in the default values of *raw*
        and *args*.  If the identity function is used with the default settings
        then a list of results is passed as a single argument (``args=False``).
        That is then returned (by the identity) as a list, which is wrapped
        in an additional list (``raw=False``), giving an extra level of
        grouping.  This is necessary because Python's ``list()`` is an
        identity for lists, but we want it to add an extra level of grouping
        so that nested S-expressions are easy to generate.  
        
        :Parameters:
        
          matcher
            The matcher whose results will be modified.
            
          function
            The modification to apply.
            
          raw
            If false, no list will be added around the final result (default
            is False because results should always be returned in a list).
            
          args
            If true, the results are passed to the function as separate
            arguments (Python's '*args' behaviour) (default is False ---
            the results are passed inside a list).
        '''
        super().__init__()
        self.__matcher = coerce(matcher)
        if isinstance(function, str):
            self.__function = lambda results: list(map(lambda x:(function, x), results))
        elif raw:
            self.__function = function
        else:
            self.__function = lambda results: [function(results)]
        self.__args = args
        tags = []
        if isinstance(function, str): tags.append(repr(function))
        if raw: tags.append('raw')
        if args: tags.append('*args')
        if tags: self.tag(','.join(tags))

    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        for (results, stream) in self.__matcher(stream):
            if self.__args:
                yield (self.__function(*results), stream)
            else:
                yield (self.__function(results), stream)
            
            
class KApply(BaseMatch):
    '''
    Apply an arbitrary function to named arguments (******).
    The function should typically expect and return a list.
    It can be used indirectly by placing ``**=`` to the right of the matcher.    
    '''

    def __init__(self, matcher, function, raw=False):
        '''
        The function will be applied the following keyword arguments:
        
          stream_in
            The stream passed to the matcher.

          stream_out
            The stream returned from the matcher.
            
          core
            The core, if streams are being used, else ``None``.
        
          results
            A list of the results returned.
            
        :Parameters:
        
          matcher
            The matcher whose results will be modified.
            
          function
            The modification to apply.
            
          raw
            If false (the default), the final return value from the function 
            will be placed in a list and returned in a pair together with the 
            new stream returned from the matcher (ie the function returns a 
            single new result).
            
            If true, the final return value from the function is used directly
            and so should match the ``([results], stream)`` type expected by
            other matchers.   
        '''
        super().__init__()
        self.__matcher = coerce(matcher)
        self.__function = function
        self.__raw = raw
        
    @managed
    def __call__(self, stream_in):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        kargs = {}
        kargs['stream_in'] = stream_in
        try:
            kargs['core'] = stream_in.core
        except:
            kargs['core'] = None
        for (results, stream_out) in self.__matcher(stream_in):
            kargs['stream_out'] = stream_out
            kargs['results'] = results
            if self.__raw:
                yield self.__function(**kargs)
            else:
                yield ([self.__function(**kargs)], stream_out)
            
            
class Regexp(BaseMatch):
    '''
    Match a regular expression.  If groups are defined, they are returned
    as results.  Otherwise, the entire expression is returned.
    '''
    
    def __init__(self, pattern):
        '''
        If the pattern contains groups, they are returned as separate results,
        otherwise the whole match is returned.
        
        :Parameters:
        
          pattern
            The regular expression to match. 
        '''
        super().__init__()
        self.tag(repr(pattern))
        self.__pattern = compile(pattern)
        
    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            match = self.__pattern.match(stream.text())
        except:
            match = self.__pattern.match(stream)
        if match:
            eaten = len(match.group())
            if match.groups():
                yield (list(match.groups()), stream[eaten:])
            else:
                yield ([match.group()], stream[eaten:])
            
            
class Delayed(BaseMatch):
    '''
    A placeholder that allows forward references (**+=**).  Before use a 
    matcher must be assigned via '+='.
    '''
    
    def __init__(self):
        '''
        Introduce the matcher.  It can be defined later with '+='
        '''
        super().__init__()
        self.__matcher = None
    
    @managed
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''

        if self.__matcher:
            return self.__matcher(stream)
        else:
            raise ValueError('Delayed matcher still unbound.')
        
    def __iadd__(self, matcher):
        if self.__matcher:
            raise ValueError('Delayed matcher already bound.')
        else:
            self.__matcher = coerce(matcher)
            return self
         

class Commit(BaseMatch):
    '''
    Commit to the current state - deletes all backtracking information.
    This only works if the match... methods are used and min_queue is greater
    than zero.
    '''
    
    @managed
    def __call__(self, stream):
        '''
        Delete backtracking state and return an empty match.
        '''
        try:
            stream.core.gc.erase()
            yield([], stream)
        except AttributeError:
            print_exc()
            raise ValueError('Commit requires stream source.')
    
    
class _TraceDecorator(BaseGeneratorDecorator):
    '''
    Support class for `lepl.match.Trace`.
    '''
    
    def __init__(self, generator, stream, name=None):
        super().__init__(generator)
        self.__stream = stream
        self.__on = Empty('+' + (name if name else ''))
        self.__off = Empty('-' + (name if name else ''))
    
    def _before(self):
        '''
        Called before each match.
        '''
        try:
            self.__stream.core.bb.switch(True)
        except:
            raise ValueError('Trace requires stream source.')
        next(self.__on(self.__stream))
        
    def _after(self):
        '''
        Called after each match.
        '''
        next(self.__off(self.__stream))
        try:
            self.__stream.core.bb.switch(False)
        except:
            raise ValueError('Trace requires stream source.')


class Trace(BaseMatch):
    '''
    Enable trace logging for the sub-matcher.
    '''
    
    def __init__(self, matcher, name=None):
        super().__init__()
        self.__matcher = matcher
        self.__name = name
    
    @managed
    def __call__(self, stream):
        '''
        '''
        return _TraceDecorator(self.__matcher(stream), stream, self.__name)


# the following are functions rather than classes, but we use the class
# syntax to give a uniform interface.
 
def AnyBut(exclude=None):
    '''
    Match any character except those specified.
    
    The argument should be a list of tokens (or a string of suitable 
    characters) to exclude.  If omitted all tokens are accepted.
    '''
    return ~Lookahead(coerce(exclude, Any)) + Any().tag('AnyBut')
            

def Optional(matcher):
    '''
    Match zero or one instances of a matcher (**[0:1]**).
    '''
    return coerce(matcher)[0:1]


def Star(matcher):
    '''
    Match zero or more instances of a matcher (**[0:]**)
    '''
    return coerce(matcher)[:]


ZeroOrMore = Star
'''
Match zero or more instances of a matcher (**[0:]**)
'''


def Plus(matcher):
    '''
    Match one or more instances of a matcher (**[1:]**)
    ''' 
    return coerce(matcher)[1:]


OneOrMore = Plus
'''
Match one or more instances of a matcher (**[1:]**)
''' 


def Map(matcher, function):
    '''
    Apply an arbitrary function to each of the tokens in the result of the 
    matcher (**>>=**).  If the function is a name, named pairs are created 
    instead.  It can be used indirectly by placing ``>>=`` to the right of the 
    matcher.    
    '''
    # list() necessary so we can use '+' on result
    if isinstance(function, str):
        return Apply(matcher, lambda l: list(map(lambda x: (function, x), l)), raw=True)
    else:
        return Apply(matcher, lambda l: list(map(function, l)), raw=True)


def Add(matcher):
    '''
    Join tokens in the result using the "+" operator (**+**).
    This joins strings and merges lists.  
    It can be used indirectly by placing ``+`` between matchers.
    '''
    def add(results):
        if results:
            result = results[0]
            for extra in results[1:]:
                try:
                    result = result + extra
                except TypeError:
                    raise TypeError('An attempt was made to add two results '
                                    'that do not have consistent types: '
                                    '{0!r} + {1!r}'.format(result, extra))
            result = [result]
        else:
            result = []
        return result
    return Apply(matcher, add, raw=True).tag('Add')


def Drop(matcher):
    '''Do the match, but return nothing (**~**).  The ~ prefix is equivalent.'''
    return Apply(matcher, lambda l: [], raw=True).tag('Drop')


def Substitute(matcher, value):
    '''Replace each return value with that given.'''
    return Map(matcher, lambda x: value).tag('Substitute')


def Name(matcher, name):
    '''
    Name the result of matching (**> name**)
    
    This replaces each value in the match with a tuple whose first value is 
    the given name and whose second value is the matched token.  The Node 
    class recognises this form and associates such values with named attributes.
    '''
    return Map(matcher, name).tag("Name('{0}')" % name)


def Eof():
    '''Match the end of a stream.  Returns nothing.'''
    return ~Lookahead(Any().tag('Eof')).tag('Eof')


Eos = Eof
'''Match the end of a stream.  Returns nothing.'''


def Identity(matcher):
    '''Functions identically to the matcher given as an argument.'''
    return coerce(matcher)


def Newline():
    '''Match newline (Unix) or carriage return newline (Windows)'''
    return Literal('\n') | Literal('\r\n')


def Space(space=' \t'):
    '''Match a single space (by default space or tab).'''
    return Any(space)


def Whitespace(space=string.whitespace):
    '''
    Match a single space (by default from string.whitespace,
    which includes newlines).
    '''
    return Any(space)


def Digit():
    '''Match any single digit.'''
    return Any(string.digits)


def Letter():
    '''Match any ASCII letter (A-Z, a-z).'''
    return Any(string.ascii_letters)


def Upper():
    '''Match any ASCII uppercase letter (A-Z).'''
    return Any(string.ascii_uppercase)

    
def Lower():
    '''Match any ASCII lowercase letter (A-Z).'''
    return Any(string.ascii_lowercase)


def Printable():
    '''Match any printable character (string.printable).'''
    return Any(string.printable)


def Punctuation():
    '''Match any punctuation character (string.punctuation).'''
    return Any(string.punctuation)


def UnsignedInteger():
    '''Match a  simple sequence of digits.'''
    return Digit()[1:,...]


def SignedInteger():
    '''Match a sequence of digits with an optional initial sign.'''
    return Any('+-')[0:1] + UnsignedInteger()

    
Integer = SignedInteger


def UnsignedFloat(decimal='.'):
    '''Match a sequence of digits that may include a decimal point.'''
    return (UnsignedInteger() + Optional(Any(decimal))) \
        | (UnsignedInteger()[0:1] + Any(decimal) + UnsignedInteger())

    
def SignedFloat(decimal='.'):
    '''Match a signed sequence of digits that may include a decimal point.'''
    return Any('+-')[0:1] + UnsignedFloat(decimal)
    
    
def SignedEFloat(decimal='.', exponent='eE'):
    '''
    Match a `lepl.match.SignedFloat` followed by an optional exponent 
    (e+02 etc).
    '''
    return SignedFloat + (Any(exponent) + SignedInteger())[0:1]

    
Float = SignedEFloat


def coerce(arg, function=Literal):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    return function(arg) if isinstance(arg, str) else arg


def Word(chars=AnyBut(Whitespace()), body=None):
     '''
     Match a sequence of non-space characters, joining them together. 
     
     chars and body, if given as strings, define possible characters to use
     for the first and rest of the characters in the word, respectively.
     If body is not given, then chars is used for the entire word.
     They can also specify matchers, which typically should match only a
     single character.
     
     So Word(Upper(), Lower()) would match names that being with an upper
     case letter, for example, while Word(AnyBut(Space())) (the default)
     matches any sequence of non-space characters. 
     '''
     chars = coerce(chars, Any)
     body = chars if body == None else coerce(body, Any)
     return chars + body[0:,...]
 

class Separator(Override):
    
    def __init__(self, separator):
        separator = coerce(separator, Regexp)
        and_ = lambda a, b: And(a, separator, b)
        def repeat(m, st=0, sp=None, d=0, s=None, a=False):
            if s == None: s = separator
            return Repeat(m, st, sp, d, s, a)
        super().__init__(and_=and_, repeat=repeat)
        