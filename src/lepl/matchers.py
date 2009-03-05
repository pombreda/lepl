
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
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
Matchers form the basis of the library; they are used to define the grammar
and do the work of parsing the input.

A matcher is like a parser combinator - it takes a stream, matches content in
the stream, and returns a list of tokens and a new stream.  However, matchers
are also generators, so they can be "recalled" to return alternative matches.
This gives backtracking.

Matchers are implemented as both classes (these tend to be the basic building
blocks) and functions (these are typically "syntactic sugar").  I have used
the same syntax (capitalized names) for both to keep the API uniform.

For more background, please see the `manual <../index.html>`_.
'''

from collections import deque
import string
from re import compile
from sys import version
from traceback import print_exc

from lepl.graph \
    import ArgAsAttributeMixin, PostorderWalkerMixin, ConstructorStr, GraphStr
from lepl.manager import GeneratorManager
from lepl.node import Node, raise_error
from lepl.operators \
    import OperatorMixin, Matcher, GREEDY, NON_GREEDY, BREADTH_FIRST, DEPTH_FIRST
from lepl.parser import Configuration, make_parser, make_matcher, tagged, flatten
from lepl.stream import Stream
from lepl.trace import TraceResults
from lepl.support import assert_type, lmap, compose, LogMixin


class BaseMatcher(ArgAsAttributeMixin, PostorderWalkerMixin, OperatorMixin, 
                    LogMixin, Matcher):
    '''
    A base class that provides support to all matchers.
    '''

    def __init__(self):
        super(BaseMatcher, self).__init__()

    def __str__(self):
        visitor = ConstructorStr()
        return visitor.postprocess(self.postorder(visitor))
    
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
    def tree(self):
        '''
        An ASCII tree for display.
        '''
        visitor = GraphStr()
        return visitor.postprocess(self.postorder(visitor))
    
    def file_parser(self, config=None):
        '''
        Construct a parser for file objects that uses a `lepl.stream.Stream()` 
        internally and returns a single result.
        '''
        return make_parser(self, Stream.from_file, 
                           config if config else self.default_config())
    
    def list_parser(self, config=None):
        '''
        Construct a parser for lists that uses a `lepl.stream.Stream()` 
        internally and returns a single result.
        '''
        return make_parser(self, Stream.from_list, 
                           config if config else self.default_config())
    
    def path_parser(self, config=None):
        '''
        Construct a parser for a file that uses a `lepl.stream.Stream()` 
        internally and returns a single result.
        '''
        return make_parser(self, Stream.from_path, 
                           config if config else self.default_config())
    
    def string_parser(self, config=None):
        '''
        Construct a parser for strings that uses a `lepl.stream.Stream()` 
        internally and returns a single result.
        '''
        return make_parser(self, Stream.from_string, 
                           config if config else self.default_config())
    
    def null_parser(self, config=None):
        '''
        Construct a parser for strings and lists that returns a single result
        (this does not use streams).
        '''
        return make_parser(self, Stream.null, 
                           config if config else self.default_config())
    
    def parse_file(self, file, config=None):
        '''
        Parse the contents of a file, returning a single match and using a
        `lepl.stream.Stream()` internally.
        '''
        return self.file_parser(config)(file)
        
    def parse_list(self, list_, config=None):
        '''
        Parse the contents of a list, returning a single match and using a
        `lepl.stream.Stream()` internally.
        '''
        return self.list_parser(config)(list_)
        
    def parse_path(self, path, config=None):
        '''
        Parse the contents of a file, returning a single match and using a
        `lepl.stream.Stream()` internally.
        '''
        return self.path_parser(config)(path)
        
    def parse_string(self, string, config=None):
        '''
        Parse the contents of a string, returning a single match and using a
        `lepl.stream.Stream()` internally.
        '''
        return self.string_parser(config)(string)
    
    def parse(self, stream, config=None):
        '''
        Parse the contents of a string or list, returning a single match (this
        does not use streams).
        '''
        return self.null_parser(config)(stream)
    
    
    def file_matcher(self, config=None):
        '''
        Construct a parser for file objects that returns a sequence of matches
        and uses a `lepl.stream.Stream()` internally.
        '''
        return make_matcher(self, Stream.from_file, 
                            config if config else self.default_config())
    
    def list_matcher(self, config=None):
        '''
        Construct a parser for lists that returns a sequence of matches
        and uses a `lepl.stream.Stream()` internally.
        '''
        return make_matcher(self, Stream.from_list, 
                            config if config else self.default_config())
    
    def path_matcher(self, config=None):
        '''
        Construct a parser for a file that returns a sequence of matches
        and uses a `lepl.stream.Stream()` internally.
        '''
        return make_matcher(self, Stream.from_path, 
                            config if config else self.default_config())
    
    def string_matcher(self, config=None):
        '''
        Construct a parser for strings that returns a sequence of matches
        and uses a `lepl.stream.Stream()` internally.
        '''
        return make_matcher(self, Stream.from_string, 
                            config if config else self.default_config())

    def null_matcher(self, config=None):
        '''
        Construct a parser for strings and lists list objects that returns a s
        equence of matches (this does not use streams).
        '''
        return make_matcher(self, Stream.null, 
                            config if config else self.default_config())

    def match_file(self, file, config=None):
        '''
        Parse the contents of a file, returning a sequence of matches and using a
        `lepl.stream.Stream()` internally.
        '''
        return self.file_matcher(config)(file)
        
    def match_list(self, list_, config=None):
        '''
        Parse a list, returning a sequence of matches and using a
        `lepl.stream.Stream()` internally.
        '''
        return self.list_matcher(config)(list_)
        
    def match_path(self, path, config=None):
        '''
        Parse a file, returning a sequence of matches and using a
        `lepl.stream.Stream()` internally.
        '''
        return self.path_matcher(config)(path)
        
    def match_string(self, string, config=None):
        '''
        Parse a string, returning a sequence of matches and using a
        `lepl.stream.Stream()` internally.
        '''
        return self.string_matcher(config)(string)

    def match(self, stream, config=None):
        '''
        Parse a string or list, returning a sequence of matches 
        (this does not use streams).
        '''
        return self.null_matcher(config)(stream)

    
    def default_config(self):
        '''
        Generate a default configuration instance.  Currently this flattens
        nested `lepl.matchers.And()` and `lepl.matchers.Or()` instances;
        supports tracing (which is initially disabled, but can be enabled
        using the `lepl.matchers.Trace()` matcher); and tracks but does
        not limit generators (which can be flushed using the 
        `lepl.matchers.Commit()` matcher).
        '''
        return Configuration(
            rewriters=[flatten({And: '*matchers', Or: '*matchers'})],
            monitors=[TraceResults(False), GeneratorManager(0)])
#        return Configuration()
    

class _BaseSearch(BaseMatcher):
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
        self._arg(first=coerce(first))
        self._arg(start=start)
        self._arg(stop=stop)
        self._karg(rest=coerce(first if rest is None else rest))
        
    def _cleanup(self, queue):
        for (count, acc, stream, generator) in queue:
            generator.close()
        
        
class DepthFirst(_BaseSearch):
    '''
    (Post order) Depth first repetition (typically used via ``lepl.Repeat``).
    '''

    @tagged
    def __call__(self, stream):
        stack = []
        try:
            stack.append((0, [], stream, self.first(stream)))
            while stack:
                (count1, acc1, stream1, generator) = stack[-1]
                extended = False
                if self.stop is None or count1 < self.stop:
                    count2 = count1 + 1
                    try:
                        (value, stream2) = yield generator
                        acc2 = acc1 + value
                        stack.append((count2, acc2, stream2, self.rest(stream2)))
                        extended = True
                    except StopIteration:
                        pass
                if not extended:
                    if count1 >= self.start and \
                            (self.stop is None or count1 <= self.stop):
                        yield (acc1, stream1)
                    stack.pop(-1)
        finally:
            self._cleanup(stack)
        
        
class BreadthFirst(_BaseSearch):
    '''
    (Level order) Breadth first repetition (typically used via ``lepl.Repeat``).
    '''
    
    @tagged
    def __call__(self, stream):
        queue = deque()
        try:
            queue.append((0, [], stream, self.first(stream)))
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
                            queue.append((count2, acc2, stream2, self.rest(stream2)))
                except StopIteration:
                    pass
        finally:
            self._cleanup(queue)
            

class OrderByResultCount(BaseMatcher):
    '''
    Modify a matcher to return results in length order.
    '''
    
    def __init__(self, matcher, ascending=True):
        super(OrderByResultCount, self).__init__()
        self._arg(matcher=coerce(matcher, Literal))
        self._karg(ascending=ascending)
        
    @tagged
    def __call__(self, stream):
        generator = self.matcher(stream)
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

                
class _BaseCombiner(BaseMatcher):
    '''
    Support for `And` and `Or`.
    '''
    
    def __init__(self, *matchers):
        super(_BaseCombiner, self).__init__()
        self._args(matchers=lmap(coerce, matchers))


class And(_BaseCombiner):
    '''
    Match one or more matchers in sequence (**&**).
    It can be used indirectly by placing ``&`` between matchers.
    '''
    
    @tagged
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  Results from the different matchers are
        combined together as elements in a list.
        '''

        if self.matchers:
            stack = [([], self.matchers[0](stream), self.matchers[1:])]
            try:
                while stack:
                    (result, generator, matchers) = stack.pop(-1)
                    try:
                        (value, stream) = yield generator
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
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will correspond to one of the
        sub-matchers (starting from the left).
        '''
        for matcher in self.matchers:
            generator = matcher(stream)
            try:
                while True:
                    yield (yield generator)
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
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will correspond to one of the
        sub-matchers (starting from the left).
        '''
        matched = False
        for match in self.matchers:
            generator = match(stream)
            try:
                while True:
                    yield (yield generator)
                    matched = True
            except StopIteration:
                pass
            if matched: break
            

class Any(BaseMatcher):
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
        super(Any, self).__init__()
        self._karg(restrict=restrict)
        self.tag(repr(restrict))
    
    @tagged
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will be a single matching 
        character.
        '''
        if stream and (not self.restrict or stream[0] in self.restrict):
            yield ([stream[0]], stream[1:])
            
            
class Literal(BaseMatcher):
    '''
    Match a series of tokens in the stream (**''**).
    '''
    
    def __init__(self, text):
        '''
        Typically the argument is a string but a list might be appropriate 
        with some streams.
        '''
        super(Literal, self).__init__()
        self._arg(text=text)
        self.tag(repr(text))
    
    @tagged
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).

        Need to be careful here to use only the restricted functionality
        provided by the stream interface.
        '''
        try:
            if self.text == stream[0:len(self.text)]:
                yield ([self.text], stream[len(self.text):])
        except IndexError:
            pass
        
        
def coerce(arg, function=Literal):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    return function(arg) if isinstance(arg, str) else arg


class Empty(BaseMatcher):
    '''
    Match any stream, consumes no input, and returns nothing.
    '''
    
    def __init__(self, name=None):
        super(Empty, self).__init__()
        self._karg(name=name)
        if name:
            self.tag(name)
    
    @tagged
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  Match any character and progress to 
        the next.
        '''
        yield ([], stream)

            
class Lookahead(BaseMatcher):
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
        super(Lookahead, self).__init__()
        self._arg(matcher=coerce(matcher))
        self._karg(negated=negated)
        if negated:
            self.tag('~')
    
    @tagged
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            yield self.matcher(stream) # an evaluation, not a return
            success = True
        except StopIteration:
            success = False
        if success is self.negated:
            return
        else:
            yield ([], stream)
            
    def __invert__(self):
        '''
        Invert the semantics (this overrides the usual meaning for ~).
        '''
        return Lookahead(self.matcher, negated=not self.negated)
            

class Apply(BaseMatcher):
    '''
    Apply an arbitrary function to the results of the matcher (**>**, **\***).
    
    The function should expect a list and can return any value (it should
    return a list if ``raw=True``).
     
    It can be used indirectly by placing ``>`` (or ``*`` to set ``args=True``)
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
        super(Apply, self).__init__()
        self._arg(matcher=coerce(matcher))
        if isinstance(function, str):
            self._arg(function=lambda results: list(map(lambda x:(function, x), results)))
        elif raw:
            self._arg(function=function)
        else:
            self._arg(function=lambda results: [function(results)])
        # this may seem odd, but we have already "applied" raw=False above
        self._karg(raw=True)
        self._karg(args=args)
        tags = []
        if isinstance(function, str): tags.append(repr(function))
        if args: tags.append('*args')
        if tags: self.tag(','.join(tags))

    @tagged
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            generator = self.matcher(stream)
            while True:
                (results, stream) = yield generator
                if self.args:
                    yield (self.function(*results), stream)
                else:
                    yield (self.function(results), stream)
        except StopIteration:
            pass
            
            
class KApply(BaseMatcher):
    '''
    Apply an arbitrary function to named arguments (**\****).
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
        super(KApply, self).__init__()
        self._arg(matcher=coerce(matcher))
        self._arg(function=function)
        self._karg(raw=raw)
        
    @tagged
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
        try:
            generator = self.matcher(stream_in)
            while True:
                (results, stream_out) = yield generator
                kargs['stream_out'] = stream_out
                kargs['results'] = results
                if self.raw:
                    yield self.function(**kargs)
                else:
                    yield ([self.function(**kargs)], stream_out)
        except StopIteration:
            pass
            
            
class Regexp(BaseMatcher):
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
        super(Regexp, self).__init__()
        self._arg(pattern=pattern)
        self.tag(repr(pattern))
        self.__pattern = compile(pattern)
        
    @tagged
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            match = self.__pattern.match(stream.text())
        except: # no text method
            match = self.__pattern.match(stream)
        if match:
            eaten = len(match.group())
            if match.groups():
                yield (list(match.groups()), stream[eaten:])
            else:
                yield ([match.group()], stream[eaten:])
            
            
class Delayed(BaseMatcher):
    '''
    A placeholder that allows forward references (**+=**).  Before use a 
    matcher must be assigned via '+='.
    '''
    
    def __init__(self, matcher=None):
        '''
        Introduce the matcher.  It can be defined later with '+='
        '''
        super(Delayed, self).__init__()
        self._karg(matcher=matcher)
    
    def __call__(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        if self.matcher:
            return self.matcher(stream)
        else:
            raise ValueError('Delayed matcher still unbound.')
        
    def __iadd__(self, matcher):
        if self.matcher:
            raise ValueError('Delayed matcher already bound.')
        else:
            self.matcher = coerce(matcher)
            return self
         

class Commit(BaseMatcher):
    '''
    Commit to the current state - deletes all backtracking information.
    This only works if the core is present (eg when parse_string is called)
    and the min_queue option is greater than zero.
    '''
    
    def __init__(self):
        super(Commit, self).__init__()
        self.monitor_class = GeneratorManager
    
    @tagged
    def __call__(self, stream):
        if False:
            yield
    
    def on_push(self, monitor):
        pass
    
    def on_pop(self, monitor):
        monitor.commit()
    
    
class Trace(BaseMatcher):
    '''
    Enable trace logging for the sub-matcher.
    '''
    
    def __init__(self, matcher, trace=True):
        super(Trace, self).__init__()
        self._arg(matcher=matcher)
        self._karg(trace=trace)
        self.monitor_class = TraceResults

    @tagged
    def __call__(self, stream):
        try:
            generator = self.matcher(stream)
            while True:
                yield (yield generator)
        except StopIteration:
            pass
        
    def on_push(self, monitor):
        monitor.switch(1 if self.trace else -1)
        
    def on_pop(self, monitor):
        monitor.switch(-1 if self.trace else 1)
        
    
# The following are functions rather than classes, but we use the class
# syntax to give a uniform interface.

# The functions are not strictly matchers, in that they do not yield
# results directly.  Instead they provide useful ways of assembling other
# matchers to do useful tasks.  Because of this they do not appear in the
# final matcher tree for any particular grammar.

 
def Repeat(matcher, start=0, stop=None, algorithm=DEPTH_FIRST, 
            separator=None, add=False):
    '''
    '''
    first = coerce(matcher)
    if separator is None:
        rest = first
    else:
        rest = And(coerce(separator, Regexp), first)
    if start is None: start = 0
    assert_type('The start index for Repeat or [...]', start, int)
    assert_type('The stop index for Repeat or [...]', stop, int, none_ok=True)
    assert_type('The algorithm/increment for Repeat or [...]', algorithm, str)
    if start < 0:
        raise ValueError('Repeat or [...] cannot have a negative start.')
    if stop is not None and stop < start:
        raise ValueError('Repeat or [...] must have a stop '
                         'value greater than or equal to the start.')
    if 'dbgn'.find(algorithm) == -1:
        raise ValueError('Repeat or [...] must have a step (algorithm) '
                         'of d, b, g or n.')
    add = Add if add else Identity
    return {DEPTH_FIRST:
                add(DepthFirst(first, start, stop, rest)),
            BREADTH_FIRST: 
                add(BreadthFirst(first, start, stop, rest)),
            GREEDY:        
                add(OrderByResultCount(BreadthFirst(first, start, stop, rest))),
            NON_GREEDY:
                add(OrderByResultCount(BreadthFirst(first, start, stop, rest),
                                       False))
            }[algorithm]
            
        
def AnyBut(exclude=None):
    '''
    Match any character except those specified (or, if a matcher is used as
    the exclude, if the matcher fails).
    
    The argument should be a list of tokens (or a string of suitable 
    characters) to exclude, or a matcher.  If omitted all tokens are accepted.
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
    matcher (**>>**).  If the function is a name, named pairs are created 
    instead.  It can be used indirectly by placing ``>>`` to the right of the 
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
    Match a `lepl.matchers.SignedFloat` followed by an optional exponent 
    (e+02 etc).
    '''
    return SignedFloat + (Any(exponent) + SignedInteger())[0:1]

    
Float = SignedEFloat


def Word(chars=AnyBut(Whitespace()), body=None):
     '''
     Match a sequence of non-space characters, joining them together. 
     
     chars and body, if given as strings, define possible characters to use
     for the first and rest of the characters in the word, respectively.
     If body is not given, then chars is used for the entire word.
     They can also specify matchers, which typically should match only a
     single character.
     
     So ``Word(Upper(), Lower())`` would match names that being with an upper
     case letter, for example, while ``Word(AnyBut(Space()))`` (the default)
     matches any sequence of non-space characters. 
     '''
     chars = coerce(chars, Any)
     body = chars if body is None else coerce(body, Any)
     return chars + body[0:,...]
 
 
def DropEmpty(matcher):
    '''
    Drop results if they are empty (ie if they are ``False`` in Python).
    
    This will drop empty strings and lists.  It will also drop
    `lepl.node.Node` instances if they are empty (since the length is then
    zero).
    '''
    def drop(results):
        return [result for result in results if result]
    return Apply(matcher, drop, raw=True)


def Literals(*matchers):
    '''
    A series of literals, joined with ``lepl.Or``.
    '''
    # I considered implementing this by extending Literal() itself, but
    # that would have meant putting "Or-like" functionality in Literal,
    # and I felt it better to keep the base matchers reasonably orthogonal.
    return Or(*lmap(Literal, matchers))
 