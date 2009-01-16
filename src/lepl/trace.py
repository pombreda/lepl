
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
        
    def describe_args(self, *args):
        self.__describe = '{0}({1})'.format(self.__class__.__name__, 
                                            ','.join(map(self.__nice_str, args)))
        
    def __nice_str(self, value):
        return repr(value) if isinstance(value, str) else str(value)
        
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
            fifo = CircularFifo(self.__memory)
            if self.latest:
                for report in self.latest:
                    fifo.append(report)
            self.latest = fifo
        
    @staticmethod        
    def formatter(matcher, result, epoch):
        return '{0:5d}  {1}   {2}'.format(epoch, matcher, 
                                          'fail' if result == None else result)

    @staticmethod
    def preformatter(matcher, stream):
        return '{0:<20s} {1:4d}:{2:{3}s}'.format(
                    matcher.describe(), stream.distance(), stream, 
                    stream.core.description_length + 5)

    def register(self, matcher, result=None, stream=None):
        '''
        This is called whenever a match succeeds or fails.
        '''
        if self.__memory > 0:
            record = self.formatter(matcher, result, self.__epoch())
            self.latest.append(record)
            if stream and stream.distance() >= self.__longest_depth:
                self.__longest_depth = stream.distance()
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
        return '\n'.join(self.latest)
    
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
            'Epoch  Matcher                 Stream          Result' \
            .format(self.__memory, '\n'.join(before),
                    self.__memory_fail, '\n'.join(failure),
                    self.__memory_tail, '\n'.join(after))
    
    def print_latest(self):
        print(self.format_latest())
    
    def print_longest(self):
        print(self.format_longest())
    
