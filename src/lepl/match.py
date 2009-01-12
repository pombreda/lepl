
'''
Matches take a stream of input and return a list of a list of values.

The "list of values" is typically a list of words or AST nodes or similar.
The extra list, "outside" that, is different possible versions.  In most cases
only the first item from the second, outer list, is used.  So a very simple 
use of a matcher might be:
  MyMatcher(stream)[0]
where the [0] immediately takes the first value from that outer list.

Internally, the outer list is important to allow backtracking - this lets
matchers explore alternative combinations until one "fits" the stream.
'''

import string

from lepl.node import Node
from lepl.resources import managed
from lepl.stream import StreamMixin
from lepl.support import assert_type
from lepl.trace import LogMixin


class BaseMatch(StreamMixin, LogMixin):
    '''
    This provides support and special syntax that is common across all
    matchers.  For example, it provides logging and makes the "&" operator
    a shortcut for the "And" matcher.
    '''

    def __init__(self):
        super().__init__()
        
    def __add__(self, other):
        '''
        self + other
        
        Combine adjacent matchers in sequence, merging the result with "+" 
        (so strings are joined, lists merged).
        '''
        return Add(And(self, other))

    def __radd__(self, other):
        '''
        other + self
        
        Combine adjacent matchers in sequence, merging the result with "+" 
        (so strings are joined, lists merged).
        '''
        return Add(And(other, self))

    def __and__(self, other):
        '''
        self & other
        
        Combine adjacent matchers in sequence.
        '''
        return And(self, other)
        
    def __rand__(self, other):
        '''
        other & self
        
        Combine adjacent matchers in sequence.
        '''
        return And(other, self)
    
    def __truediv__(self, other):
        '''
        self / other
        
        Combine adjacent matchers in sequence, with an optional space between
        them.  The space is included in the results.
        '''
        return And(self, Space()[0:,...], other)
        
    def __rtruediv__(self, other):
        '''
        other / self
        
        Combine adjacent matchers in sequence, with an optional space between
        them.  The space is included in the results.
        '''
        return And(other, Space()[0:,...], self)
        
    def __moddiv__(self, other):
        '''
        self // other
        
        Combine adjacent matchers in sequence, with a space between them.  
        The space is included in the results.
        '''
        return And(self, Space()[1:,...], other)
        
    def __rmoddiv__(self, other):
        '''
        other // self
        
        Combine adjacent matchers in sequence, with a space between them.  
        The space is included in the results.
        '''
        return And(other, Space()[1:,...], self)
        
    def __or__(self, other):
        '''
        self | other
        
        Try from alternative matchers.
        '''
        return Or(self, other)
        
    def __ror__(self, other):
        '''
        other | self
        
        Try from alternative matchers.
        '''
        return Or(other, self)
        
    def __invert__(self):
        '''
        ~self
        
        Apply Not to the current matcher.
        '''
        return Not(self)
        
    def __getitem__(self, indices):
        '''
        self[start:stop:step, separator, ...]
        
        Allows the main class to be modified via the array index / slice syntax:
        [n] - Repeat exactly n times
        [n:m] - Repeat n to m times, starting with n and incrementing
        [n:m:s] - Repeat n, n+s, ... times, with an upper bound of m
        Defaults are: n=0, m=infinity, s=-1
        We use a negative third index (greedy matching, depth first search)
        because it behaves better with large patterns and limited backtracking
        (the generators are stored directly and can be closed to free resources;
        with non-greedy, breadth first search generators are successively 
        expanded and the results accumulated in memory).
        
        A match argument can be given, which is used as the separator.
        For example, [0:3,Drop(Space())] will match lists of length 0 to 3
        whose entries are separated by a space (omitted from the result).
        
        An ellipsis (...) can also be given, in which case the results are 
        joined together with '+' (as Add()).
        '''
        start = 0
        stop = None
        step = -1
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
                step = index.step if index.step != None else -1
            elif index == Ellipsis:
                add = True
            elif separator == None:
                separator = coerce(index)
            else:
                raise TypeError(index)
        return (Add if add else Identity)(
                    Repeat(self, start, stop, step, separator))
    
    def __gt__(self, function):
        '''
        self > function
        
        Apply the function to the results returned (unless function is a 
        string, in which case the results are returned as the second part
        of a tuple, whose first part is the string given).  If the function
        is a Node constructor then we add the list.
        '''
        if isinstance(function, str):
            return Name(self, function)
        elif isinstance(function, type) and issubclass(function, Node):
             return Apply(self, lambda l: [function(l)])
        else:
            return Apply(self, function(l))
    
    def __rshift__(self, function):
        '''
        self >> function
        
        Apply the function to each member of the list of results returned
        (unless function is a string, in which case the results are returned 
        as the second part of a tuple, whose first part is the string given).
        '''
        if isinstance(function, str):
            return Name(self, function)
        else:
            return Map(self, function)
    
    
class Repeat(BaseMatch):
    '''
    Repeats the pattern supplied to the constructor.
    ''' 
    
    def __init__(self, pattern, start=0, stop=None, step=1, separator=None):
        '''
        A value of None for stop implies no upper bound.
        '''
        super().__init__()
        self.__first = coerce(pattern)
        self.__second = self.__first if separator == None else And(separator, pattern)
        if start == None: start = 0
        assert_type('The start index for Repeat or [...]', start, int)
        assert_type('The stop index for Repeat or [...]', stop, int, none_ok=True)
        assert_type('The index step for Repeat or [...]', step, int)
        if start < 0:
            raise ValueError('Repeat or [...] cannot have a negative start.')
        if stop != None and stop < start:
            raise ValueError('Repeat or [...] must have a stop '
                             'value greater than or equal to the start.')
        if stop == None and step < -1:
            raise ValueError('Repeat or [...] cannot have an open upper '
                             'bound with a decreasing step other than -1.')
        if step == 0:
            raise ValueError('Repeat or [...] must have a non-zero step.')
        self._start = start
        self._stop = stop
        self._step = step
        
    @managed
    def __call__(self, stream):
        if self._step > 0:
            return self.__call_up(stream)
        else:
            return self.__call_down(stream)
        
    def __call_up(self, stream):
        '''
        Note that in the presence of backtracking, non-greedy match is 
        slightly odd - it will return all possible short lists (including
        backtracking embedded matchers) before returning longer lists.
        
        We generate all possibilities in order of increasing numbers of
        matches, so for each call to the underlying pattern we immediately
        examine all possible values (postponing another call as long as
        possible).  Since any of those values could be expanded on later
        we save them in a stack.
        
        Discarding stack duplicates may be a gain in odd circumstances?
        '''
        stack = []
        if 0 == self._start: yield ([], stream)
        stack.append((0, [], stream))
        while stack:
            # smallest counts first
            (count1, acc1, stream1) = stack.pop(0)
            count2 = count1 + 1
            for (value, stream2) in self.__pattern(count1)(stream1):
                acc2 = acc1 + value
                if count2 >= self._start and \
                    (self._stop == None or count2 <= self._stop) and \
                    (count2 - self._start) % self._step == 0:
                    yield (acc2, stream2)
                if self._stop == None or count2 + self._step <= self._stop:
                    stack.append((count2, acc2, stream2))
                    
    def __pattern(self, count):
        if 0 == count:
            return self.__first
        else:
            return self.__second

    def __call_down(self, stream):
        '''
        We attempt (see note below) to generate all possibilities in order of 
        decreasing numbers of matches, so we build on calls to the underlying
        pattern by calling again as soon as we have one value.  Later values 
        (ie the generator that supplies later values) are saved on the stack.
        
        Despite that, we still accumulate many (all non-stop) values "on 
        the way".  These are stored for later use.
        
        Note - It is possible (I think) that backtracking may return a larger 
        match than the first match returned (for example, if the match being 
        repeated is itself greedy and, on backtracking, matches a smaller 
        portion of the input).  To guarantee longest first we would need to
        generate all results and then sort by length; that is too inefficient.
        '''
        stack = []
        try:
            stack.append((0, [], self.__pattern(0)(stream)))
            known = {}
            if 0 == self._start:
                known[0] = [([], stream)]
            while stack:
                (count1, acc1, generator) = stack[-1]
                try:
                    (value, stream2) = next(generator)
                    count2 = count1 + 1
                    acc2 = acc1 + value
                    if count2 == self._stop:
                        yield (acc2, stream2)
                    elif count2 >= self._start and \
                        (self._stop == None or \
                            (count2 <= self._stop and \
                            (self._step == -1 or
                             (self._stop - count2) % self._step == 0))):
                        if count2 not in known: known[count2] = []
                        known[count2].append((acc2, stream2))
                    stack.append((count2, acc2, self.__pattern(count2)(stream2)))
                except StopIteration:
                    stack.pop(-1)
            counts = list(known.keys())
            counts.sort(reverse=True)
            for count in counts:
                for (acc, stream) in known[count]:
                    yield (acc, stream)
        finally:
            for (count, acc, generator) in stack:
                self._debug('Closing %s' % generator)
                generator.close()
                
                
class And(BaseMatch):
    '''
    Matches one or more matchers in sequence.
    It can be used indirectly by using '&' between matchers.
    '''
    
    def __init__(self, *matchers):
        '''
        The arguments are the matchers which are matched in turn.
        '''
        super().__init__()
        self.__matchers = [coerce(matcher) for matcher in matchers]

    @managed
    def __call__(self, stream):
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
    Matches one of the given matchers.
    It can be used indirectly by using '|' between matchers.
    '''
    
    def __init__(self, *matchers):
        '''
        The arguments are the matchers, one of which is matched.
        They are tried from left to right until one succeeds; backtracking
        will try more from the same matcher and, once that is exhausted,
        continue to the right.
        '''
        super().__init__()
        self.__matchers = [coerce(matcher) for matcher in matchers]

    @managed
    def __call__(self, stream):
        for match in self.__matchers:
            for result in match(stream):
                yield result


class Any(BaseMatch):
    '''
    Matches any single token in the stream.  Optionally a restricted set of
    valid tokens can be supplied.
    '''
    
    def __init__(self, restrict=None):
        '''
        The argument should be a list of tokens (or a string of suitable 
        characters).  If omitted any single token is accepted.
        '''
        super().__init__()
        self.__restrict = restrict
    
    @managed
    def __call__(self, stream):
        '''
        Match any character and progress to the next.
        '''
        if stream and (not self.__restrict or stream[0] in self.__restrict):
            yield ([stream[0]], stream[1:])
            
            
class Literal(BaseMatch):
    '''
    Matches a series of tokens in the stream.
    '''
    
    def __init__(self, text):
        '''
        Typically the argument is a string but a list might be appropriate 
        with some streams.
        '''
        super().__init__()
        self.__text = text
    
    @managed
    def __call__(self, stream):
        '''
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
    Matches any stream, consumes no input, and returns nothing.
    '''
    
    @managed
    def __call__(self, stream):
        '''
        Match any character and progress to the next.
        '''
        yield ([], stream)

            
class Not(BaseMatch):
    '''
    This returns an empty list if the stream does not match the given matcher.
    If the stream does match, no result is returned (and the parsing will
    backtrack to explore alternative options).
    It can be used indirectly by using '!' before a matcher.
    '''
    
    def __init__(self, matcher):
        '''
        The argument acts as a "stop" - if it matches, this will fail.
        '''
        super().__init__()
        self.__matcher = coerce(matcher)
    
    @managed
    def __call__(self, stream):
        for result in self.__matcher(stream):
            raise StopIteration()
        yield ([], stream)
        

class Apply(BaseMatch):
    '''
    Apply an arbitrary function to the results of the matcher.
    The function should typically expect and return a list.
    It can be used indirectly by using '>=' to the right of the matcher.    
    '''
    
    def __init__(self, matcher, function):
        super().__init__()
        self.__matcher = coerce(matcher)
        self.__function = function
        
    @managed
    def __call__(self, stream):
        for (results, stream) in self.__matcher(stream):
            yield (self.__function(results), stream)
            
            
class Delayed(BaseMatch):
    '''
    A placeholder that allows forward references.  Before use a matcher
    must be assigned via "+="
    '''
    
    def __init__(self):
        super().__init__()
        self.__matcher = None
        
    def __call__(self, stream):
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
         

 # the following are functions rather than classes, but we use the class
 # syntax to give a uniform interface.
 
def Optional(matcher):
    '''
    
    '''
    return coerce(matcher)[0:1]


def Star(matcher):
    '''
    
    '''
    return coerce(matcher)[:]

ZeroOrMore = Star


def Plus(matcher):
    '''
    
    ''' 
    return coerce(matcher)[1:]

OneOrMore = Plus


def Map(matcher, function):
    '''
    Apply an arbitrary function to each of the tokens in the result of the 
    matcher.
    It can be used indirectly by using '>>=' to the right of the matcher.    
    '''
    return Apply(matcher, lambda l: list(map(function, l)))


def Add(matcher):
    '''
    Join tokens in the result using the "+" operator.
    This joins strings and merges lists.  
    It can be used indirectly by using '+' between matchers.
    '''
    def add(results):
        result = []
        if results:
            result = results[0]
            for extra in results[1:]:
                result = result + extra
            result = [result]
        return result
    return Apply(matcher, add)


def Drop(matcher):
    '''Do the match, but return nothing.'''
    return Apply(matcher, lambda l: [])


def Substitute(matcher, value):
    '''Replace each return value with that given.'''
    return Map(matcher, lambda x: value)


def Name(matcher, name):
    '''
    Name the result of matching.  This replaces each value in the match with
    a tuple whose first value is the given name and whose second value is
    the matched token.  The Node class recognises this form and associates
    such values with named attributes.
    '''
    return Map(matcher, lambda x: (name, x))


def Eof():
    '''Matches the end of a stream.  Returns nothing.'''
    return Not(Any())

Eos = Eof


def Identity(matcher):
    '''Functions identically to the matcher given as an argument.'''
    return coerce(matcher)


def Space(space=string.whitespace):
    '''Matches a single space (by default from string.whitespace).'''
    return Any(space)


def Digit():
    '''Matches any single digit.'''
    return Any(string.digits)


def Letter():
    '''Matches any ASCII letter (A-Z, a-z).'''
    return Any(string.ascii_letters)


def Upper():
    '''Matches any ASCII uppercase letter (A-Z).'''
    return Any(string.ascii_uppercase)

    
def Lower():
    '''Matches any ASCII lowercase letter (A-Z).'''
    return Any(string.ascii_lowercase)


def Printable():
    '''Matches any printable character (string.printable).'''
    return Any(string.printable)


def Punctuation():
    '''Matches any punctuation character (string.punctuation).'''
    return Any(string.punctuation)


def UnsignedInteger():
    '''A simple sequence of digits.'''
    return Digit()[1:,...]

def SignedInteger():
    '''A sequence of digits with an optional initial sign.'''
    return Any('+-')[0:1] + UnsignedInteger()
    
Integer = SignedInteger


def UnsignedFloat(decimal='.'):
    '''A sequence of digits that may include a decimal point.'''
    return (UnsignedInteger() + Optional(Any(decimal))) \
        | (UnsignedInteger()[0:1] + Any(decimal) + UnsignedInteger())
    
def SignedFloat(decimal='.'):
    '''A signed sequence of digits that may include a decimal point.'''
    return Any('+-')[0:1] + UnsignedFloat(decimal)
    
def SignedEFloat(decimal='.', exponent='eE'):
    '''A SignedFloat followed by an optional exponent (e+02 etc).'''
    return SignedFloat + (Any(exponent) + SignedInteger())[0:1]
    
Float = SignedEFloat


def coerce(arg, function=Literal):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    return function(arg) if isinstance(arg, str) else arg


def Word(chars=~Space(), body=None):
     '''
     chars and body, if given as strings, define possible characters to use
     for the first and rest of the characters in the word, respectively.
     If body is not given, then chars is used for the entire word.
     They can also specify matchers, which typically should match only a
     single character.
     So Word(Upper(), Lower()) would match names that being with an upper
     case letter, for example, while Word(~Space()) matches any sequence
     of non-space characters. 
     '''
     chars = coerce(chars, Any)
     body = chars if body == None else coerce(body, Any)
     return chars + body[0:,...]
 
