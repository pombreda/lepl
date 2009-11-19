
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


# for some reason (parsing of yields?) pyulint cannot process this file
# (can get partial analysis from command line)

# pylint: disable-msg=C0103,W0212
# (consistent interfaces)
# pylint: disable-msg=E1101
# (_args create attributes)
# pylint: disable-msg=R0901, R0904, W0142
# lepl conventions

from abc import ABCMeta
from collections import deque
from re import compile as compile_

from lepl.config import Configuration
from lepl.graph import ArgAsAttributeMixin, PostorderWalkerMixin, \
    ConstructorStr, GraphStr
from lepl.manager import _GeneratorManager
from lepl.node import Node
from lepl.operators import OperatorMixin, OPERATORS, DefaultNamespace, Matcher
from lepl.parser import make_parser, make_matcher, tagged
from lepl.trace import _TraceResults
from lepl.support import lmap, LogMixin, format, basestring, str


# pylint: disable-msg=W0105
# Python 2.6
#class ApplyRaw(metaclass=ABCMeta):
ApplyRaw = ABCMeta('ApplyRaw', (object, ), {})
'''
ABC used to control `Apply`, so that the result is not wrapped in a list.  
'''


# Python 2.6
#class ApplyArgs(metaclass=ABCMeta):
ApplyArgs = ABCMeta('ApplyArgs', (object, ), {})
'''
ABC used to control `Apply`, os that the results list is supplied as "*args".  
'''

ApplyArgs.register(Node)



class BaseMatcher(ArgAsAttributeMixin, PostorderWalkerMixin, 
                    LogMixin, Matcher):
    '''
    A base class that provides support to all matchers.
    '''
    pass
    
    
class OperatorMatcher(OperatorMixin, BaseMatcher):
    '''
    A base class that provides support to all matchers with operators.
    '''
    
    __default_config = None

    def __init__(self, name=OPERATORS, namespace=DefaultNamespace):
        super(OperatorMatcher, self).__init__(name=name, namespace=namespace)

    def __str__(self):
        visitor = ConstructorStr()
        return self.postorder(visitor, Matcher)
    
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
    def tree(self):
        '''
        An ASCII tree for display.
        '''
        visitor = GraphStr()
        return self.postorder(visitor)
    
    def file_parser(self, config=None, **kargs):
        '''
        Construct a parser for file objects that uses a stream 
        internally and returns a single result.
        '''
        config = Configuration.default(config)
        return make_parser(self, config.stream.from_file, config, kargs)
    
    def items_parser(self, config=None, **kargs):
        '''
        Construct a parser for a sequence of times (an item is something
        that would be matched by `Any`) that uses a stream internally and 
        returns a single result.
        '''
        config = Configuration.default(config)
        return make_parser(self, config.stream.from_items, config, kargs) 
    
    def path_parser(self, config=None, **kargs):
        '''
        Construct a parser for a file that uses a stream 
        internally and returns a single result.
        '''
        config = Configuration.default(config)
        return make_parser(self, config.stream.from_path, config, kargs) 
    
    def string_parser(self, config=None, **kargs):
        '''
        Construct a parser for strings that uses a stream 
        internally and returns a single result.
        '''
        config = Configuration.default(config)
        return make_parser(self, config.stream.from_string, config, kargs) 
    
    def null_parser(self, config=None, **kargs):
        '''
        Construct a parser for strings and lists that returns a single result
        (this does not use streams).
        '''
        config = Configuration.default(config)
        return make_parser(self, config.stream.null, config, kargs) 
    
    
    def parse_file(self, file_, config=None, **kargs):
        '''
        Parse the contents of a file, returning a single match and using a
        stream internally.
        '''
        return self.file_parser(config, **kargs)(file_)
        
    def parse_items(self, list_, config=None, **kargs):
        '''
        Parse the contents of a sequence of items (an item is something
        that would be matched by `Any`), returning a single match and using a
        stream internally.
        '''
        return self.items_parser(config, **kargs)(list_)
        
    def parse_path(self, path, config=None, **kargs):
        '''
        Parse the contents of a file, returning a single match and using a
        stream internally.
        '''
        return self.path_parser(config, **kargs)(path)
        
    def parse_string(self, string, config=None, **kargs):
        '''
        Parse the contents of a string, returning a single match and using a
        stream internally.
        '''
        return self.string_parser(config, **kargs)(string)
    
    def parse(self, stream, config=None, **kargs):
        '''
        Parse the contents of a string or list, returning a single match (this
        does not use streams).
        '''
        return self.null_parser(config, **kargs)(stream)
    
    
    def file_matcher(self, config=None, **kargs):
        '''
        Construct a parser for file objects that returns a sequence of matches
        and uses a stream internally.
        '''
        config = Configuration.default(config)
        return make_matcher(self, config.stream.from_file, config, kargs) 
    
    def items_matcher(self, config=None, **kargs):
        '''
        Construct a parser for a sequence of items (an item is something that
        would be matched by `Any`) that returns a sequence of matches
        and uses a stream internally.
        '''
        config = Configuration.default(config)
        return make_matcher(self, config.stream.from_items, config, kargs) 
    
    def path_matcher(self, config=None, **kargs):
        '''
        Construct a parser for a file that returns a sequence of matches
        and uses a stream internally.
        '''
        config = Configuration.default(config)
        return make_matcher(self, config.stream.from_path, config, kargs) 
    
    def string_matcher(self, config=None, **kargs):
        '''
        Construct a parser for strings that returns a sequence of matches
        and uses a stream internally.
        '''
        config = Configuration.default(config)
        return make_matcher(self, config.stream.from_string, config, kargs) 

    def null_matcher(self, config=None, **kargs):
        '''
        Construct a parser for strings and lists list objects that returns a s
        equence of matches (this does not use streams).
        '''
        config = Configuration.default(config)
        return make_matcher(self, config.stream.null, config, kargs) 

    def match_file(self, file_, config=None, **kargs):
        '''
        Parse the contents of a file, returning a sequence of matches and using 
        a stream internally.
        '''
        return self.file_matcher(config, **kargs)(file_)
        
    def match_items(self, list_, config=None, **kargs):
        '''
        Parse a sequence of items (an item is something that would be matched
        by `Any`), returning a sequence of matches and using a
        stream internally.
        '''
        return self.items_matcher(config, **kargs)(list_)
        
    def match_path(self, path, config=None, **kargs):
        '''
        Parse a file, returning a sequence of matches and using a
        stream internally.
        '''
        return self.path_matcher(config, **kargs)(path)
        
    def match_string(self, string, config=None, **kargs):
        '''
        Parse a string, returning a sequence of matches and using a
        stream internally.
        '''
        return self.string_matcher(config, **kargs)(string)

    def match(self, stream, config=None, **kargs):
        '''
        Parse a string or list, returning a sequence of matches 
        (this does not use streams).
        '''
        return self.null_matcher(config, **kargs)(stream)
    

class Transformation(object):
    '''
    A transformation is a wrapper for a series of functions that are applied
    to a result. 
    
    A function takes three arguments (results, stream_in, stream_out)
    and returns the tuple (results, stream_out).
    '''
    
    def __init__(self, functions=None):
        '''
        We accept wither a list of a functions or a single value.
        '''
        functions = [] if functions is None else functions
        if not isinstance(functions, list):
            functions = [functions]
        self.functions = functions
        
    def compose(self, transformation):
        '''
        Apply transformation to the results of this function.
        '''
        functions = list(self.functions)
        functions.extend(transformation.functions)
        if functions == self.functions:
            return self
        else:
            return Transformation(functions)

    def precompose(self, transformation):
        '''
        Insert the transformation before the existing functions.
        '''
        functions = list(transformation.functions)
        functions.extend(self.functions)
        if functions == self.functions:
            return self
        else:
            return Transformation(functions)

    def __call__(self, results, stream_in, stream_out):
        for function in self.functions:
            (results, stream_out) = function(results, stream_in, stream_out)
        return (results, stream_out)
        
    def __str__(self):
        return str(self.functions)
        
    def __repr__(self):
        return format('Transformation({0!r})', self.functions)
    
    def __bool__(self):
        return bool(self.functions)
    
    # Python 2.6
    def __nonzero__(self):
        return self.__bool__()
    
    def __iter__(self):
        '''
        Co-operate with graph routines.
        '''
        return iter([])
        

class Transformable(OperatorMatcher):
    '''
    All subclasses invoke the function attribute on
    (results, stream_in, stream_out) when returning their final value.
    This allows `Transform` instances to be merged directly.
    '''

    def __init__(self, function=Transformation()):
        super(Transformable, self).__init__()
        if not isinstance(function, Transformation):
            function = Transformation(function)
        self.function = function

    def compose(self, transform):
        '''
        Combine with a transform, returning a new instance.
        
        We must return a new instance because the same Transformable may 
        occur more than once in a graph and we don't want to include the
        Transform in other cases.
        '''
        raise NotImplementedError()


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
            

class Any(OperatorMatcher):
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
        self.__warned = False
    
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  The result will be a single matching 
        character.
        '''
        ok = bool(stream)
        if ok and self.restrict:
            try:
                ok = stream[0] in self.restrict
            except TypeError:
                # it would be nice to make this an error, but for line aware
                # parsing (and any other heterogenous input) it's legal
                if not self.__warned:
                    self._debug(format('Cannot restrict {0} with {1!r}',
                                       stream[0], self.restrict))
                    self.__warned = True
        if ok:
            yield ([stream[0]], stream[1:])
            
            
class Literal(Transformable):
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
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).

        Need to be careful here to use only the restricted functionality
        provided by the stream interface.
        '''
        try:
            if self.text == stream[0:len(self.text)]:
                yield self.function([self.text], stream, 
                                    stream[len(self.text):])
        except IndexError:
            pass
        
    def compose(self, transform):
        '''
        Generate a new instance with the composed function from the Transform.
        '''
        copy = Literal(self.text)
        copy.function = self.function.compose(transform.function)
        return copy
        
        
def coerce_(arg, function=Literal):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    return function(arg) if isinstance(arg, basestring) else arg


class Empty(OperatorMatcher):
    '''
    Match any stream, consumes no input, and returns nothing.
    '''
    
    def __init__(self, name=None):
        super(Empty, self).__init__()
        self._karg(name=name)
        if name:
            self.tag(name)
    
    # pylint: disable-msg=R0201
    # keep things consistent for future subclasses
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  Match any character and progress to 
        the next.
        '''
        yield ([], stream)
        
        
class Lookahead(OperatorMatcher):
    '''
    Tests to see if the embedded matcher *could* match, but does not do the
    matching.  On success an empty list (ie no result) and the original
    stream are returned.
    
    When negated (preceded by ~) the behaviour is reversed - success occurs
    only if the embedded matcher would fail to match.
    
    This is a consumer because it's correct functioning depends directly on
    the stream's contents.
    '''
    
    def __init__(self, matcher, negated=False):
        '''
        On success, no input is consumed.
        If negated, this will succeed if the matcher fails.  If the matcher is
        a string it is coerced to a literal match.
        '''
        super(Lookahead, self).__init__()
        self._arg(matcher=coerce_(matcher))
        self._karg(negated=negated)
        if negated:
            self.tag('~')
    
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            yield self.matcher._match(stream) # an evaluation, not a return
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
            

class Transform(Transformable):
    '''
    Apply a function to (result, stream_in, stream_out)

    Typically used via `Apply` and `KApply`.
    '''

    def __init__(self, matcher, function):
        super(Transform, self).__init__(function)
        self._arg(matcher=coerce_(matcher))
        # it's ok that this overwrites the same thing from Transformable
        # (Transformable cannot have an argument because it is subclass to
        # matcher without explicit functions)
        if not isinstance(function, Transformation):
            function = Transformation(function)
        self._arg(function=function)

    @tagged
    def _match(self, stream_in):
        '''
        Do the matching (return a generator that provides successive
        (result, stream) tuples).
        '''
        try:
            generator = self.matcher._match(stream_in)
            while True:
                (results, stream_out) = yield generator
                yield self.function(results, stream_in, stream_out)
        except StopIteration:
            pass
        
    def compose(self, transform):
        '''
        Create a new Transform that includes the extra processing. 
        '''
        return Transform(self.matcher, 
                         self.function.compose(transform.function))


class Regexp(OperatorMatcher):
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
        self.__pattern = compile_(pattern)
        
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            match = self.__pattern.match(stream.text)
        except AttributeError: # no text method
            match = self.__pattern.match(stream)
        if match:
            eaten = len(match.group())
            if match.groups():
                yield (list(match.groups()), stream[eaten:])
            else:
                yield ([match.group()], stream[eaten:])
            
            
class Delayed(OperatorMatcher):
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
    
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        if self.matcher:
            return self.matcher._match(stream)
        else:
            raise ValueError('Delayed matcher still unbound.')
        
    # pylint: disable-msg=E0203, W0201
    # _karg defined this in constructor
    def __iadd__(self, matcher):
        if self.matcher:
            raise ValueError('Delayed matcher already bound.')
        else:
            self.matcher = coerce_(matcher)
            return self
        

class Commit(OperatorMatcher):
    '''
    Commit to the current state - deletes all backtracking information.
    This only works if the `GeneratorManager` monitor is present
    (see `Configuration`) and the min_queue option is greater than zero.
    '''
    
    def __init__(self):
        super(Commit, self).__init__()
        self.monitor_class = _GeneratorManager
    
    # pylint: disable-msg=R0201
    # consistent for subclasses
    @tagged
    def _match(self, _stream):
        '''
        Attempt to match the stream.
        '''
        if False:
            yield
    
    def on_push(self, monitor):
        '''
        Do nothing on entering matcher.
        '''
        pass
    
    def on_pop(self, monitor):
        '''
        On leaving, commit.
        '''
        monitor.commit()
    
    
class Trace(OperatorMatcher):
    '''
    Enable trace logging for the sub-matcher.
    '''
    
    def __init__(self, matcher, trace=True):
        super(Trace, self).__init__()
        self._arg(matcher=matcher)
        self._karg(trace=trace)
        self.monitor_class = _TraceResults

    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        try:
            generator = self.matcher._match(stream)
            while True:
                yield (yield generator)
        except StopIteration:
            pass
        
    def on_push(self, monitor):
        '''
        On entering, switch monitor on.
        '''
        monitor.switch(1 if self.trace else -1)
        
    def on_pop(self, monitor):
        '''
        On leaving, switch monitor off.
        '''
        monitor.switch(-1 if self.trace else 1)
        
    
class Eof(OperatorMatcher):
    '''
    Match the end of a stream.  Returns nothing.
    '''

    def __init__(self):
        super(Eof, self).__init__()

    # pylint: disable-msg=R0201
    # consistent for subclasses
    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        if not stream:
            yield ([], stream)
            
            
class Consumer(OperatorMatcher):
    '''
    Only accept the match if it consumes data from the input
    '''

    def __init__(self, matcher, consume=True):
        '''
        If consume is False, accept when no data is consumed.  
        '''
        super(Consumer, self).__init__()
        self._arg(matcher=coerce_(matcher))
        self._karg(consume=consume)
    
    @tagged
    def _match(self, stream_in):
        '''
        Do the match and test whether the stream has progressed.
        '''
        try:
            generator = self.matcher._match(stream_in)
            while True:
                (result, stream_out) = yield generator
                if self.consume == (stream_in != stream_out):
                    yield (result, stream_out)
        except StopIteration:
            pass
        
        
class _Columns(OperatorMatcher):
    '''
    Match data in a set of columns.
    
    This is a fairly complex matcher.  It allows matchers to be associated 
    with a range of indices (measured from the current point in the stream)
    and only succeeds if all matchers succeed.  The results are returned in
    a list, in the same order as the matchers are specified.
    
    A range if indices is given as a tuple (start, stop) which works like an
    array index.  So (0, 4) selects the first four characters (like [0:4]).
    Alternatively, a number of characters can be given, in which case they
    start where the previous column finished (or at zero for the first).
    
    The matcher for each column will see the (selected) input data as a 
    separate stream.  If a matcher should consume the entire column then
    it should check for `Eos`.
    
    Finally, the skip parameter allows control of how much input is consumed.  If 
    it is unset the remaining stream starts after the final column matched. 
    
    Note that with backtracking this matcher can be quite expensive, because
    each different combination of results is returned.
    '''
 
    def __init__(self, skip, indices, *matchers):
        super(_Columns, self).__init__()
        self._arg(skip=skip)
        self._arg(indices=indices)
        self._args(matchers=matchers)
        
    @tagged
    def _match(self, stream_in):
        '''
        Build the generator from standard components and then evaluate it.
        '''
        try:
            matcher = self.__build_matcher(stream_in)
            generator = matcher._match(stream_in)
            try:
                while True:
                    yield (yield generator)
            except StopIteration:
                pass
        # if there is insufficient data for the columns, skip
        except IndexError:
            pass
        
    def __build_matcher(self, stream_in):
        '''
        Build a matcher that, when it is evaluated, will return the 
        matcher results for the columns.  We base this on `And`, but need
        to force the correct streams.
        '''
        from lepl.functions import Drop
        def force_out(replacement):
            '''
            Generate a transformer function that replaces the stream_out.
            '''
            return lambda results, _stream_in, _stream_out: \
                                                    (results, replacement)
        # left and right are the indices for the column
        # matchers is the list of matchers that will be joined by And
        # previous is the "column before", which must be modified so that
        # it returns the correct stream_out for the next matcher
        right, matchers, previous = 0, [], Empty()
        columns = list(zip(self.indices, self.matchers))
        if self.skip: 
            # this takes the entire stream_in and applies it to skip
            columns.append(((0, None), Drop(self.skip)))
        else:
            # this takes everything to the right of the previous column
            columns.append((None, Empty()))
        for (col, matcher) in columns:
            try:
                (left, right) = col
            except TypeError:
                left = right
                right = None if col is None else right + col
            matchers.append(Transform(previous, 
                                      force_out(stream_in[left:right])))
            previous = matcher
        matchers.append(previous)
        return And(*matchers)
    


# Python 2.6 doesn't support named arg after *args
#def Columns(*columns, skip=None):
_SKIP = 'skip'
def Columns(*columns, **kargs):
    '''
    Provide a cleaner syntax to `_Columns` (we can't do this directly
    because the clone function isn't smart enough to unpack complex
    arguments). 
    '''
    from lepl.functions import SkipTo, Newline, Eos
    if _SKIP in kargs:
        skip = kargs[_SKIP]
        del kargs[_SKIP]
    else:
        skip = SkipTo(First(Newline(), Eos()))
    if kargs:
        raise SyntaxError(format('Columns only accepts a single keyword: {0}',
                                 _SKIP))
    indices = []
    matchers = []
    for (col, matcher) in columns:
        indices.append(col)
        matchers.append(matcher)
    return _Columns(skip, indices, *matchers)


