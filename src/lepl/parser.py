
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

from lepl.monitor import prepare_monitors
from lepl.support import format

    
def tagged(call):
    '''
    Decorator for generators to add extra attributes.
    '''
    def tagged_call(matcher, stream):
        '''
        Wrap the result.
        '''
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
            
    def next(self):
        '''
        For Python 2.6
        '''
        return self.__next__()
    
    def send(self, value):
        '''
        Pass a value back "into" the generator (standard Python method).
        '''
        return self.__generator.send(value)
    
    def throw(self, value):
        '''
        Raise an exception in the generator (standard Python method).
        '''
#        We don't use exceptions, apart from StopIteration, so they are 
#        always "errors".  if we try passing them in they get re-thrown and 
#        lose the stack trace (i don't understand fully).  
#        Anyway, it seems to give more useful errors just to throw here 
#        (alternatively, we could alter the trampoline to throw immediately, 
#        but i'd rather keep that more general).
#        if isinstance(value, StopIteration):
#            return self.__generator.throw(value)
#        else:
#            raise value
        return self.__generator.throw(value)
                
    def __iter__(self):
        return self
                
    def close(self):
        '''
        Close the generator (used in with contexts; standard Pythin method).
        '''
        self.__generator.close()
        
    def __repr__(self):
        '''
        Lazily evaluated for speed - saves 1/3 of time spent in constructor
        '''
        if not self.describe:
            self.describe = format('{0}({1!r})', 
                                   self.matcher.describe, self.stream)
        return self.describe
        

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
                    value = next(value)
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
                            value = stack[-1].throw(value)
                            if m_value:
                                m_value.after_throw(value)
                        # handle ordinary values
                        else:
                            if m_value:
                                m_value.before_send(stack[-1], value)
                            # inject it into the coroutine
                            value = stack[-1].send(value)
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
            # pylint: disable-msg=W0703
            # (we really do want to catch everything)
            except Exception as exception:
                # an exception occurred while we were handling an exception
                # - that's not expected, so we bail to the main caller
                if exception_being_raised: # raising to caller
                    raise
                # an exception was raised by a coroutine.  internally,
                # LEPL only uses StopIteration, so we warn about anything
                # else (this might want to change if third party matchers
                # use exceptions in a more constructive way?)  
                else:
                    value = exception
                    exception_being_raised = True
                    if m_value:
                        m_value.exception(value)
                    if type(value) is not StopIteration and value != last_exc:
                        last_exc = value
                        log.error(format('Exception at epoch {0}: {1!s}',
                                         epoch, value))
                        if stack:
                            log.debug(format('Top of stack: {0}', stack[-1]))
                        log.warn(format_exc())
                        for generator in stack:
                            log.debug('Stack: ' + generator.matcher.describe)
    finally:
        # record the remaining stack
        while m_stack and stack:
            m_stack.pop(pop())
                    
                
def make_matcher(matcher, stream, config, kargs):
    '''
    Make a matcher.  Rewrite the matcher and prepare the input for a parser.
    This constructs a function that returns a generator that provides a 
    sequence of matches.
    '''
    rewriters = [] if config.rewriters is None else config.rewriters
    for rewriter in rewriters:
        matcher = rewriter(matcher)
    (m_stack, m_value) = prepare_monitors(config.monitors)
    # pylint bug here? (E0601)
    # pylint: disable-msg=W0212, E0601
    # (_match is meant to be hidden)
    # pylint: disable-msg=W0142
    parser = lambda arg: trampoline(matcher._match(stream(arg, **kargs)), 
                                    m_stack=m_stack, m_value=m_value)
    parser.matcher = matcher
    return parser


def make_parser(matcher, stream, config, kargs):
    '''
    Make a parser.  This takes a matcher node, a stream constructor, and a 
    configuration, and return a function that takes an input and returns a
    *single* parse.
    '''
    matcher = make_matcher(matcher, stream, config, kargs)
    def single(arg):
        '''
        Adapt a matcher to behave as expected for the parser interface.
        '''
        try:
            return next(matcher(arg))[0]
        except StopIteration:
            return None
    single.matcher = matcher.matcher
    return single

