
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
Tools for logging and tracing.
'''

from itertools import count
from traceback import print_exc

from lepl.monitor import ExposedMonitor
from lepl.support import CircularFifo, BaseGeneratorWrapper


class TraceResults(ExposedMonitor):
    
    def __init__(self, enabled=False):
        super(TraceResults, self).__init__()
        self.generator = None
        self.depth = -1
        self.action = None
        self.enabled = 1 if enabled else 0
    
    def next_iteration(self, epoch, value, exception, stack):
        self.epoch = epoch
        self.depth = len(stack)
    
    def before_next(self, generator):
        if self.enabled > 0:
            self.generator = generator
            self.action = 'next({0})'.format(generator.describe)
    
    def after_next(self, value):
        if self.enabled > 0:
            self.result(value, self.fmt_result(value))
    
    def before_throw(self, generator, value):
        if self.enabled > 0:
            self.generator = generator
            if type(value) is StopIteration:
                self.action = ' stop -> {0}({1!s})'.format(generator.matcher.describe, generator.stream)
            else:
                self.action = '{2!r} -> {0}({1!s})'.format(generator.matcher.describe, generator.stream, value)
    
    def after_throw(self, value):
        if self.enabled > 0:
            self.result(value, self.fmt_result(value))
    
    def before_send(self, generator, value):
        if self.enabled > 0:
            self.generator = generator
            self.action = '{1!r} -> {0}'.format(generator.matcher.describe, value)
    
    def after_send(self, value):
        if self.enabled > 0:
            self.result(value, self.fmt_result(value))
    
    def exception(self, value):
        if self.enabled > 0:
            if type(value) is StopIteration:
                self.done(self.fmt_done())
            else:
                self.error(value, self.fmt_result(value))
        
    def fmt_result(self, value):
        return '{0:05d} {1:11s} {2} ({3:04d}) {4:03d} {5:>60s} -> {6!r}' \
                .format(self.epoch, 
                        self.generator.stream,
                        self.fmt_location(self.generator.stream),
                        self.generator.stream.depth(),
                        self.depth,
                        self.action,
                        value)
        
    def fmt_done(self):
        return '{0:05d} {1:11s} {2} ({3:04d}) {4:03d} {5:>60s} -> stop' \
                .format(self.epoch, 
                        self.generator.stream,
                        self.fmt_location(self.generator.stream),
                        self.generator.stream.depth(),
                        self.depth,
                        self.action)
                
    def fmt_location(self, stream):
        (line, char) = stream.location()
        if line < 0:
            return '  eof  '
        else:
            return '{0:3d}.{1:<3d}'.format(line, char)

    def yield_(self, value):
        if self.enabled > 0:
            self._info(self.fmt_final_result(value))
        
    def raise_(self, value):
        if self.enabled > 0:
            if type(value) is StopIteration:
                self._info(self.fmt_final_result('raise {0!r}'.format(value)))
            else:
                self._warn(self.fmt_final_result('raise {0!r}'.format(value)))
        
    def fmt_final_result(self, value):
        return '{0:05d}                            {1:03d} {2} {3}' \
                .format(self.epoch,
                        self.depth,
                        ' ' * 63,
                        value)

    def result(self, value, text):
        (self._info if type(value) is tuple else self._debug)(text)    

    def error(self, value, text):
        self._warn(text)    

    def done(self, text):
        self._debug(text)
        
    def switch(self, increment):
        self.enabled += increment
    

class RecordDeepest(TraceResults):
    
    def __init__(self, n_before=6, n_results_after=2, n_done_after=2):
        super(RecordDeepest, self).__init__()
        self.n_before = n_before
        self.n_results_after = n_results_after
        self.n_done_after = n_done_after
        self._limited = CircularFifo(n_before)
        self._before = []
        self._results_after = []
        self._done_after = []
        self._deepest = 0
        
    def result(self, value, text):
        if type(value) is tuple:
            self.record(True, text)

    def error(self, value, text):
        self.record(True, text)

    def done(self, text):
        self.record(False, text)

    def record(self, is_result, text):
        stream = self.generator.stream
        if stream.depth() >= self._deepest:
            self._deepest = stream.depth()
            self._countdown_result = self.n_results_after
            self._countdown_done = self.n_done_after
            self._before = list(self._limited)
            self._results_after = []
            self._done_after = []
        elif is_result and self._countdown_result:
            self._countdown_result -= 1
            self._results_after.append(text)
        elif not is_result and self._countdown_done:
            self._countdown_done -= 1
            self._done_after.append(text)
        self._limited.append(text)
        
    def yield_(self, value):
        self._deepest = 0
        self._limited.clear()
        self.display()
        
    def raise_(self, value):
        self._deepest = 0
        self._limited.clear()
        self.display()
        
    def display(self):
        self._info(self.format())
        
    def format(self):
        return '\nUp to {0} matches before and including longest match:\n{1}\n' \
            'Up to {2} failures following longest match:\n{3}\n' \
            'Up to {4} successful matches following longest match:\n{5}\n' \
            .format(self.n_before, '\n'.join(self._before),
                    self.n_done_after, '\n'.join(self._done_after),
                    self.n_results_after, '\n'.join(self._results_after))
        


#def traced(f):
#    '''
#    Decorator for traced generators.
#    
#    In the current system this is applied to the generator wrapper that is
#    added by the `lepl.resources.managed` decorator.
#    '''
#    def next(self):
#        try:
#            response = f(self)
#            if type(response) is tuple:
#                (result, stream) = response
#                self.register(self, result, stream)
#            return response
#        except Exception as e:
#            self.register(self)
#            raise
#    return next
#
#
#class BlackBox(LogMixin):
#    '''
#    Record the longest and the most recent matches. 
#    '''
#    
#    def __init__(self, core, trace_len=4):
#        '''
#        ``memory` is either a single value or a triplet.  If a triplet, it
#        represents the number of matchers before, fails after, and matches 
#        after the longest match.  If a single value, it is the number of 
#        matchers before (the other two values are set to 3).
#        '''
#        super(BlackBox, self).__init__()
#        try:
#            self.__epoch = core.gc.epoch
#        except:
#            self.__epoch = lambda: -1
#        self.trace_len = trace_len
#        
#    @property
#    def trace_len(self):
#        return (self.__memory, self.__memory_fail, self.__memory_tail)
#    
#    @trace_len.setter
#    def trace_len(self, trace_len):
#        self.latest = [] 
#        self.longest = ['Trace not enabled (set trace_len option on Core)']
#        self.__trace = 0
#        self.__longest_depth = 0
#        self.__longest_fail = 0
#        self.__longest_tail = 0
#        try:
#            (self.__memory, self.__memory_fail, self.__memory_tail) = trace_len
#        except:
#            self.__memory = trace_len
#            self.__memory_fail = 3
#            self.__memory_tail = 3
#        if not self.__memory or self.__memory < 0:
#            self._debug('No recording of best and latest matches.')
#        else:
#            self._debug('Recording {0} matches (plus {1} failures and '
#                        '{2} following matches)'
#                        .format(self.__memory, self.__memory_fail, 
#                                self.__memory_tail))
#            limited = CircularFifo(self.__memory)
#            if self.latest:
#                for report in self.latest:
#                    limited.append(report)
#            self.latest = limited
#        
#    @staticmethod        
#    def formatter(matcher, result, epoch):
#        return '{0:5d}  {1}   {2}'.format(epoch, matcher, 
#                                          'fail' if result is None else result)
#
#    @staticmethod
#    def preformatter(matcher, stream):
#        return '{0:<30s} {1[0]:3d}.{1[1]:<3d} ({2:05d}) {3:11s}'.format(
#                    matcher.describe(), stream.location(), stream.depth(),
#                    stream)
#        
#    def switch(self, trace):
#        '''
#        Called to turn immediate tracing on/off.
#        
#        Implement with a counter rather than on/off to allow nesting.
#        '''
#        if trace:
#            self.__trace += 1
#        else:
#            self.__trace -= 1
#
#    def register(self, matcher, result=None, stream=None):
#        '''
#        This is called whenever a match succeeds or fails.
#        '''
#        if self.__memory > 0 or self.__trace:
#            record = self.formatter(matcher, result, self.__epoch())
#            if self.__trace:
#                self._info(record)
#            if self.__memory > 0:
#                self.latest.append(record)
#                if stream and stream.depth() >= self.__longest_depth:
#                    self.__longest_depth = stream.depth()
#                    self.__longest_fail = self.__memory_fail
#                    self.__longest_tail = self.__memory_tail
#                    self.longest = list(self.latest)
#                elif not stream and self.__longest_fail:
#                    self.__longest_fail -= 1
#                    self.longest.append(record)
#                elif stream and self.__longest_tail:
#                    self.__longest_tail -= 1
#                    self.longest.append(record)
#                
#    def format_latest(self):
#        return '{0}\nEpoch  Matcher                 Stream          Result' \
#            .format('\n'.join(self.latest))
#    
#    def format_longest(self):
#        before = []
#        failure = []
#        after = []
#        for (index, line) in zip(count(0), self.longest):
#            if index < self.__memory:
#                before.append(line)
#            elif line.endswith('fail'):
#                failure.append(line)
#            else:
#                after.append(line)
#        return 'Up to {0} matches before and including longest match:\n{1}\n' \
#            'Up to {2} failures following longest match:\n{3}\n' \
#            'Up to {4} successful matches following longest match:\n{5}\n' \
#            'Epoch  Matcher                       Line.Chr (Chars) Stream' \
#            '        Result' \
#            .format(self.__memory, '\n'.join(before),
#                    self.__memory_fail, '\n'.join(failure),
#                    self.__memory_tail, '\n'.join(after))
#    
#    def print_latest(self):
#        print(self.format_latest())
#    
#    def print_longest(self):
#        print(self.format_longest())
#    
