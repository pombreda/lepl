
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
Create and evaluate parsers.

Once a consistent set of matchers is constructed (that describes a grammar)
they must be evaluated against some input.  The code here supports that 
evaluation (via `trampoline()`) and allows the graph of matchers to be 
rewritten beforehand.
'''


from collections import deque
from logging import getLogger
from traceback import print_exc, format_exc
from types import MethodType, GeneratorType

from lepl.monitor import MultipleMonitors
from lepl.stream import Stream
    
    
def tagged(call):
    '''
    Decorator for generators to add extra attributes.
    '''
    def tagged_call(matcher, stream):
        return GeneratorWrapper(call(matcher, stream), matcher, stream)
    return tagged_call


class GeneratorWrapper(object):
    '''
    Associate basic info about call that created the generator with the 
    generator itself.  This lets us manage resources and provide logging.
    It is also used by `trampoline()` to recognise generators that must 
    be evaluated (rather than being treated as normal values).
    '''

    def __init__(self, generator, matcher, stream):
        self.matcher = matcher
        self.stream = stream
        self.describe = None
        self.__generator = generator
    
    def __next__(self):
        return next(self.__generator)
            
    # for 2.6
    def next(self):
        return self.__next__()
    
    def send(self, value):
        return self.__generator.send(value)
    
    def throw(self, value):
        return self.__generator.throw(value)
                
    def __iter__(self):
        return self
                
    def close(self):
        self.__generator.close()
        
    def __repr__(self):
        '''
        Lazily evaluated for speed - saves 1/3 of time spent in constructor
        '''
        if not self.describe:
            self.describe = '{0}({1})'.format(self.matcher.describe, self.stream)
        return self.describe
        

class Configuration(object):
    '''
    Encapsulate various parameters that describe how the matchers are
    rewritten and evaluated.
    '''
    
    def __init__(self, rewriters=None, monitors=None):
        '''
        `rewriters` Are functions that take and return a matcher tree.  They
        can add memoisation, restructure the tree, etc.  They are applied left
        to right.
        
        `monitors` Subclasses of `MonitorInterface` that will be
        invoked by `trampoline()`.  Multiple values are combined into a single 
        monitor.
        '''
        self.rewriters = [] if rewriters is None else rewriters 
        if not monitors:
            self.monitor = None
        elif len(monitors) == 1:
            self.monitor = monitors[0]
        else:
            self.monitor = MultipleMonitors(monitors)
            
        
def trampoline(main, monitor=None):
    '''
    The main parser loop.  Evaluates matchers as coroutines.
    
    A dedicated version for when monitor not present increased the speed of
    the nat_lang performance test by only around 1% (close to noise). 
    
    Replacing stack append/pop with a manually allocated non-decreasing array
    and index made no significant difference (at around 1% level)
    '''
    stack = deque()
    append = stack.append
    pop = stack.pop
    try:
        value = main
        exception = False
        epoch = 0
        log = getLogger('lepl.parser.trampoline')
        last_exc = None
        while True:
            epoch += 1
            try:
                if monitor: monitor.next_iteration(epoch, value, exception, stack)
                if type(value) is GeneratorWrapper:
                    if monitor: monitor.push(value)
                    append(value)
                    if monitor: monitor.before_next(value)
                    value = next(value)
                    if monitor: monitor.after_next(value)
                else:
                    popped = pop()
                    if monitor: monitor.pop(popped)
                    if stack:
                        if exception:
                            exception = False
                            if monitor: monitor.before_throw(stack[-1], value)
                            value = stack[-1].throw(value)
                            if monitor: monitor.after_throw(value)
                        else:
                            if monitor: monitor.before_send(stack[-1], value)
                            value = stack[-1].send(value)
                            if monitor: monitor.after_send(value)
                    else:
                        if exception:
                            if monitor: monitor.raise_(value)
                            raise value
                        else:
                            if monitor: monitor.yield_(value)
                            yield value
                        value = main
            except Exception as e:
                if exception: # raising to caller
                    raise
                else:
                    value = e
                    exception = True
                    if monitor: monitor.exception(value)
                    if type(value) is not StopIteration and value != last_exc:
                        last_exc = value
                        log.warn(format_exc())
                        for generator in stack:
                            log.warn('Stack: ' + generator.matcher.describe)
    finally:
        while monitor and stack:
            monitor.pop(pop())
                    
                
def prepare(matcher, stream, conf):
    '''
    Rewrite the matcher and prepare the input for a parser.
    '''
    for rewriter in conf.rewriters:
        matcher = rewriter(matcher)
    parser = lambda arg: trampoline(matcher(stream(arg)), monitor=conf.monitor)
    parser.matcher = matcher
    return parser


def make_parser(matcher, stream, conf):
    '''
    Make a parser.  This takes a matcher node, a stream constructor, and a 
    configuration, and return a function that takes an input and returns a
    *single* parse.
    '''
    matcher = prepare(matcher, stream, conf)
    def single(arg):
        try:
            return next(matcher(arg))[0]
        except StopIteration:
            return None
    single.matcher = matcher.matcher
    return single

    
def make_matcher(matcher, stream, conf):
    '''
    Similar to `make_parser`, but constructs a function that returns a 
    generator that provides a sequence of matches.
    '''
    return prepare(matcher, stream, conf)

    
def file_parser(matcher, conf):
    '''
    Construct a parser for file objects that returns a single match and
    uses a `Stream()` internally.
    '''
    return make_parser(matcher, Stream.from_file, conf)

def list_parser(matcher, conf):
    '''
    Construct a parser for lists that returns a single match and uses a 
    `Stream()` internally.
    '''
    return make_parser(matcher, Stream.from_list, conf)

def path_parser(matcher, conf):
    '''
    Construct a parser for a file that returns a single match and uses a 
    `Stream()` internally.
    '''
    return make_parser(matcher, Stream.from_path, conf)

def string_parser(matcher, conf):
    '''
    Construct a parser for strings that returns a single match and uses a 
    `Stream()` internally.
    '''
    return make_parser(matcher, Stream.from_string, conf)

def null_parser(matcher, conf):
    '''
    Construct a parser for strings and lists returns a single match
    (this does not use streams).
    '''
    return make_parser(matcher, Stream.null, conf)


def file_matcher(matcher, conf):
    '''
    Construct a parser that returns a sequence of matches for file objects 
    and uses a `Stream()` internally.
    '''
    return make_matcher(matcher, Stream.from_file, conf)

def list_matcher(matcher, conf):
    '''
    Construct a parser that returns a sequence of matches for lists 
    and uses a `Stream()` internally.
    '''
    return make_matcher(matcher, Stream.from_list, conf)

def path_matcher(matcher, conf):
    '''
    Construct a parser that returns a sequence of matches for a file
    and uses a `Stream()` internally.
    '''
    return make_matcher(matcher, Stream.from_path, conf)

def string_matcher(matcher, conf):
    '''
    Construct a parser that returns a sequence of matches for strings 
    and uses a `Stream()` internally.
    '''
    return make_matcher(matcher, Stream.from_string, conf)

def null_matcher(matcher, conf):
    '''
    Construct a parser that returns a sequence of matches for strings
    and lists (this does not use streams).
    '''
    return make_matcher(matcher, Stream.null, conf)

