
'''
Add standard Python logging to a class.
'''

from itertools import count
from logging import getLogger
from traceback import print_exc

from lepl.support import CircularFifo


class LogMixin():
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._log = getLogger(self.__module__ + '.' + self.__class__.__name__)
        self._debug = self._log.debug
        self._info = self._log.info
        self._warn = self._log.warn
        self._error = self._log.error
        self.__describe = self.__class__.__name__
        
    def tag(self, *args):
        self.__describe = '{0}({1})'.format(self.__class__.__name__, 
                                            ','.join(map(str, args)))
        return self
        
    def describe(self):
        '''
        This should return a (fairly compact) description of the match.
        '''
        return self.__describe
    

def traced(f):
    def next(self):
        try:
            (result, stream) = f(self)
            self.register(self, result, stream)
        except:
            self.register(self)
            raise
        return (result, stream)
    return next


class BlackBox(LogMixin):
    '''
    Record the longest and the most recent matches. 
    '''
    
    def __init__(self, core, memory=4):
        super().__init__()
        try:
            self.__epoch = core.gc.epoch
        except:
            self.__epoch = lambda: -1
        self.memory = memory
        
    @property
    def memory(self):
        return (self.__memory, self.__memory_fail, self.__memory_tail)
    
    @memory.setter
    def memory(self, memory):
        self.latest = [] 
        self.longest = ['Trace not enabled (set memory option on Core)']
        self.__trace = 0
        self.__longest_depth = 0
        self.__longest_fail = 0
        self.__longest_tail = 0
        try:
            (self.__memory, self.__memory_fail, self.__memory_tail) = memory
        except:
            self.__memory = memory
            self.__memory_fail = 3
            self.__memory_tail = 3
        if not self.__memory or self.__memory < 0:
            self._debug('No recording of best and latest matches.')
        else:
            self._debug('Recording {0} matches (including {1} failures and '
                        '{2} following matches)'
                        .format(self.__memory, self.__memory_fail, 
                                self.__memory_tail))
            limited = CircularFifo(self.__memory)
            if self.latest:
                for report in self.latest:
                    limited.append(report)
            self.latest = limited
        
    @staticmethod        
    def formatter(matcher, result, epoch):
        return '{0:5d}  {1}   {2}'.format(epoch, matcher, 
                                          'fail' if result == None else result)

    @staticmethod
    def preformatter(matcher, stream):
        return '{0:<30s} {1[0]:3d}.{1[1]:<3d} ({2:05d}) {3:{4}s}'.format(
                    matcher.describe(), stream.location(), stream.depth(),
                    stream, stream.core.description_length + 5)
        
    def switch(self, trace):
        '''
        Called to turn immediate tracing on/off.
        
        Implement with a counter rather than on/off to allow nesting.
        '''
        if trace:
            self.__trace += 1
        else:
            self.__trace -= 1

    def register(self, matcher, result=None, stream=None):
        '''
        This is called whenever a match succeeds or fails.
        '''
        if self.__memory > 0 or self.__trace:
            record = self.formatter(matcher, result, self.__epoch())
            if self.__trace:
                self._info(record)
            if self.__memory > 0:
                self.latest.append(record)
                if stream and stream.depth() >= self.__longest_depth:
                    self.__longest_depth = stream.depth()
                    self.__longest_fail = self.__memory_fail
                    self.__longest_tail = self.__memory_tail
                    self.longest = list(self.latest)
                elif not stream and self.__longest_fail:
                    self.__longest_fail -= 1
                    self.longest.append(record)
                elif stream and self.__longest_tail:
                    self.__longest_tail -= 1
                    self.longest.append(record)
                
    def format_latest(self):
        return '{0}\nEpoch  Matcher                 Stream          Result' \
            .format('\n'.join(self.latest))
    
    def format_longest(self):
        before = []
        failure = []
        after = []
        for (index, line) in zip(count(0), self.longest):
            if index < self.__memory:
                before.append(line)
            elif line.endswith('fail'):
                failure.append(line)
            else:
                after.append(line)
        return 'Up to {0} matches before and including longest match:\n{1}\n' \
            'Up to {2} failures following longest match:\n{3}\n' \
            'Up to {4} successful matches following longest match:\n{5}\n' \
            'Epoch  Matcher                       Line.Chr (Chars) Stream' \
            '        Result' \
            .format(self.__memory, '\n'.join(before),
                    self.__memory_fail, '\n'.join(failure),
                    self.__memory_tail, '\n'.join(after))
    
    def print_latest(self):
        print(self.format_latest())
    
    def print_longest(self):
        print(self.format_longest())
    
