
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

from lepl.repeat import RepeatMixin
from lepl.resources import managed
from lepl.stream import StreamMixin
from lepl.trace import LogMixin


class BaseMatch(RepeatMixin, StreamMixin, LogMixin):
    '''
    This provides support and special syntax that is common across all
    matchers.  For example, it provides logging and makes the "&" operator
    a shortcut for the "And" matcher.
    '''

    def __init__(self):
        super().__init__()
        
    def __add__(self, other):
        '''
        Combine adjacent matchers in sequence, merging the result with "+" 
        (so strings are joined, lists merged).
        '''
        if isinstance(other, BaseMatch):
            return Add(And(self, other))
        else:
            raise ValueError('+ can only be applied to to matchers')

    def __and__(self, other):
        '''
        Combine adjacent matchers in sequence.
        '''
        if isinstance(other, BaseMatch):
            return And(self, other)
        else:
            raise ValueError('& can only be applied to to matchers')
        
    def __or__(self, other):
        '''
        Try from alternative matchers.
        '''
        if isinstance(other, BaseMatch):
            return Or(self, other)
        else:
            raise ValueError('| can only be applied to to matchers')
        
    def __invert__(self):
        '''
        Apply Not to the current matcher.
        '''
        return Not(self)
        

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
        self.__restrict = restrict
    
    @managed
    def __call__(self, stream):
        '''
        Match any character and progress to the next.
        '''
        if stream and (not self.__restrict or stream[0] in self.__restrict):
            yield ([stream[0]], stream[1:])
            
            
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
        self.__matcher = matcher
    
    @managed
    def __call__(self, stream):
        for result in self.__matcher(stream):
            raise StopIteration()
        yield ([], stream)
        

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
        self.__matchers = matchers

    @managed
    def __call__(self, stream):
        if len(self.__matchers) > 0:
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
        self.__matchers = matchers

    @managed
    def __call__(self, stream):
        for match in self.__matchers:
            for result in match(stream):
                yield result
        

class Apply(BaseMatch):
    '''
    Apply an arbitrary function to the results of the matcher.
    The function should typically expect a list.
    It can be used indirectly by using '>=' to the right of the matcher.    
    '''
    
    def __init__(self, matcher, function):
        self.__matcher = matcher
        
    @managed
    def __call__(self, stream):
        for (results, stream) in self.__matcher(stream):
            yield (function(results), stream)


 # the following are functions rather than classes, but we use the class
 # syntax to give a uniform interface.
 
def Word(chars, body=None, space=None):
     '''
     
     '''
     chars = Any(chars)
     body = chars if body == None else Any(body)
     space = Space() if space == None else Any(space)
     return chars + body[:] + space
 

def Optional(matcher):
    '''
    
    '''
    return matcher[0:1]


def Star(matcher):
    '''
    
    '''
    return matcher[:]

ZeroOrMore = Star


def Plus(matcher):
    '''
    
    ''' 
    return matcher[1:]

OneOrMore = Plus


def Map(matcher, function):
    '''
    Apply an arbitrary function to each of the tokens in the result of the 
    matcher.
    It can be used indirectly by using '>>=' to the right of the matcher.    
    '''
    return Apply(matcher, lambda l: map(function, l))


def Add(matcher):
    '''
    Join tokens in the result using the "+" operator.
    This joins strings and merges lists.  
    It can be used indirectly by using '+' between matchers.
    '''
    def add(results):
        if results:
            result = results[0]
            for extra in results[1:]:
                result = result + extra
            yield ([result], stream)
        else:
            yield ([], stream)
    return Apply(matcher, add)


def Drop(matcher):
    '''

    '''
    return Apply(matcher, lambda l: [])


def Substitute(matcher, value):
    '''
    
    '''
    return Map(matcher, lambda x: value)


def Name(matcher, name):
    '''
    
    '''
    return Map(matcher, lambda x: (name, x))

