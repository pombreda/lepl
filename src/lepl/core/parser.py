
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
Create and evaluate parsers.

Once a consistent set of matchers is constructed (that describes a grammar)
they must be evaluated against some input.  The code here supports that 
evaluation (via `trampoline()`) and allows the graph of matchers to be 
rewritten beforehand.
'''


from collections import deque
from logging import getLogger
from traceback import format_exc

from lepl.core.monitor import prepare_monitors
from lepl.support.lib import format

    
def tagged(method):
    '''
    Decorator for generators to add extra attributes.
    '''
    def tagged_method(matcher, stream):
        '''
        Wrap the result.
        '''
        return GeneratorWrapper(method(matcher, stream), matcher, stream)
    return tagged_method


def tagged_function(matcher, function):
    '''
    Decorator for generators to add extra attributes.
    '''
    def tagged_function(stream):
        '''
        Wrap the result.
        '''
        return GeneratorWrapper(function(matcher, stream), matcher, stream)
    return tagged_function


class GeneratorWrapper(object):
    '''
    Associate basic info about call that created the generator with the 
    generator itself.  This lets us manage resources and provide logging.
    It is also used by `trampoline()` to recognise generators that must 
    be evaluated (rather than being treated as normal values).
    '''
    
    __slots__ = ['generator', 'matcher', 'stream', 
                 '_GeneratorWrapper__cached_repr', '__weakref__']

    def __init__(self, generator, matcher, stream):
        self.generator = generator
        self.matcher = matcher
        self.stream = stream
        self.__cached_repr = None
        
    def __repr__(self):
        '''
        Lazily evaluated for speed - saves 1/3 of time spent in constructor
        '''
        if not self.__cached_repr:
            self.__cached_repr = format('{0}({1!r})', self.matcher, self.stream)
        return self.__cached_repr
    
    def __str__(self):
        return self.__repr__()
        

def trampoline(main, m_stack=None, m_value=None):
    '''
    The main parser loop.  Evaluates matchers as coroutines.
    
    A dedicated version for when monitor not present increased the speed of
    the nat_lang performance test by only around 1% (close to noise). 
    
    Replacing stack append/pop with a manually allocated non-decreasing array
    and index made no significant difference (at around 1% level)
    '''
    stack = deque()
    push = stack.append
    pop = stack.pop
    try:
        value = main
        exception_being_raised = False
        epoch = 0
        log = getLogger('lepl.parser.trampoline')
        last_exc = None
        while True:
            epoch += 1
            try:
                if m_value:
                    m_value.next_iteration(epoch, value, 
                                           exception_being_raised, stack)
                # is the value a coroutine that should be added to our stack
                # and evaluated?
                if type(value) is GeneratorWrapper:
                    if m_stack:
                        m_stack.push(value)
                    # add to the stack
                    push(value)
                    if m_value:
                        m_value.before_next(value)
                    # and evaluate
                    value = next(value.generator)
                    if m_value:
                        m_value.after_next(value)
                # if we don't have a coroutine then we have a result that
                # must be passed up the stack.
                else:
                    # drop top of the stack (which returned the value)
                    popped = pop()
                    if m_stack:
                        m_stack.pop(popped)
                    # if we still have coroutines left, pass the value in
                    if stack:
                        # handle exceptions that are being raised
                        if exception_being_raised:
                            exception_being_raised = False
                            if m_value:
                                m_value.before_throw(stack[-1], value)
                            # raise it inside the coroutine
                            value = stack[-1].generator.throw(value)
                            if m_value:
                                m_value.after_throw(value)
                        # handle ordinary values
                        else:
                            if m_value:
                                m_value.before_send(stack[-1], value)
                            # inject it into the coroutine
                            value = stack[-1].generator.send(value)
                            if m_value:
                                m_value.after_send(value)
                    # otherwise, the stack is completely unwound so return
                    # to main caller 
                    else:
                        if exception_being_raised:
                            if m_value:
                                m_value.raise_(value)
                            raise value
                        else:
                            if m_value:
                                m_value.yield_(value)
                            yield value
                        # this allows us to restart with a new evaluation
                        # (backtracking) if called again.
                        value = main
            except StopIteration as exception:
                # this occurs when we need to exit the main loop
                if exception_being_raised:
                    raise
                # otherwise, we will propagate this value
                value = exception
                exception_being_raised = True
                if m_value:
                    m_value.exception(value)
            except Exception:
                # do some logging etc before re-raising
                log.error(format('Exception at epoch {0}: {1!s}',
                                 epoch, value))
                if stack:
                    log.debug(format('Top of stack: {0}', stack[-1]))
                    log.warn(format_exc())
                    for generator in stack:
                        log.debug(format('Stack: {0}', generator))
                raise
    finally:
        # record the remaining stack
        while m_stack and stack:
            m_stack.pop(pop())
                    
                
def make_raw_parser(matcher, stream_factory, config):
    '''
    Make a parser.  Rewrite the matcher and prepare the input for a parser.
    This constructs a function that returns a generator that provides a 
    sequence of matches (ie (results, stream) pairs).
    '''
    for rewriter in config.rewriters:
        matcher = rewriter(matcher)
    (m_stack, m_value) = prepare_monitors(config.monitors)
    # pylint bug here? (E0601)
    # pylint: disable-msg=W0212, E0601
    # (_match is meant to be hidden)
    # pylint: disable-msg=W0142
    parser = lambda arg, **kargs: \
        trampoline(matcher._match(stream_factory(arg, **kargs)), 
                   m_stack=m_stack, m_value=m_value)
    parser.matcher = matcher
    return parser


def make_multiple(raw):
    '''
    Convert a raw parser to return a generator of results.
    '''
    def multiple(arg, **kargs):
        '''
        Adapt a raw parser to behave as expected for the matcher interface.
        '''
        return map(lambda x: x[0], raw(arg, **kargs))
    multiple.matcher = raw.matcher
    return multiple


def make_single(raw):
    '''
    Convert a raw parser to return a single result or None.
    '''
    def single(arg, **kargs):
        '''
        Adapt a raw parser to behave as expected for the parser interface.
        '''
        try:
            return next(raw(arg, **kargs))[0]
        except StopIteration:
            return None
    single.matcher = raw.matcher
    return single
