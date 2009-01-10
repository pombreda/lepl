
'''
We can control resource consumption by closing generators - the problem is
which generators to close?

At first it seems that the answer is going to be connected to tree traversal,
but after some thought it's not so clear - exactly what tree is being traversed,
and how that identifies what generators should be closed, is not completely
clear (to me at least).

A better approach seems to be to discard those that have not been used "for a
long time".  A variation on this - keep a maximum number of the youngest 
generators - is practical.  But care is needed to both in identifying what is 
used, and when it starts being unused, and in implementing that efficiently.

All generators are stored in a priority queue using weak references.  The 
"real" priority is given by the "last used date" (a value read from a counter 
in core each time a value is returned), but the priority in the queue is
frozen when inserted.  So on removing from the queue the priority must be
checked to ensure it has not changed (and, if so, it must be updated with the
real value and replaced).
'''

from heapq import heappushpop, heappop, heappush
from weakref import ref

from lepl.trace import LogMixin
from lepl.stream import Stream


class GeneratorWrapper():
    '''
    This provides basic support for the GC process, but uses normal 
    references and exists within the main body of the code.  It is added
    to generators via a decorator when first returned from a match object.
    
    It assumes that the match includes the logMixin, but is resilient to
    simple list streams (in which case no GC will occur).
    '''
    
    def __init__(self, generator, match, stream):
        self.__generator = generator
        self.__description = '%s@%s' % (self.__owner.describe(), stream)
        self.__managed = isinstance(stream, Stream)
        if self.__managed:
            self.__core = stream.core
            self.__registered = False
            self.age = 0
            self.active = False
    
    def __next__(self):
        try:
            self.active = True
            return next(self.__generator)
        finally:
            self.epoch = self.__core.gc.current_epoch()
            self.active = False
            if self.__managed and not self.__registered:
                self.__core.gc.register(self)
                
    def close(self):
        self.__generator.close()
        
    def __str__(self):
        return self.__description


class GeneratorRef():
    '''
    This contains the weak reference to the GeneratorWrapper and is stored
    in the GC priority queue.
    '''
    
    def __init__(self, wrapper):
        self.__wrapper = ref(wrapper)
        self.exists = True
        self.epoch = wrapper.epoch
        self.active = wrapper.active
        self.stale = False
        
    def __cmp__(self, other):
        assert isinstance(other, GeneratorRef)
        return cmp(self.epoch, other.epoch)
    
    def update(self):
        wrapper = self.__wrapper()
        if wrapper:
            self.exists = True
            self.stable = self.epoch == wrapper.epoch
            self.epoch = wrapper.epoch
            self.active = wrapper.active
        else:
            self.exists = False
            self.stale = True
            self.active = False
    
    def close(self):
        generator = self.__wrapper()
        if generator:
            generator.close()


class GeneratorControl(LogMixin):
    '''
    This manages the priority queue, etc.
    '''
    
    def __init__(self, max_size):
        '''
        The maximum size is only a recommendation - we do not discard active
        generators so there is an effective minimum size which takes priority.
        '''
        super().__init__()
        self.__max_size = max_size
        self.__epoch = 0
        self.__queue = []
        self.__overdue = False
        
    def current_epoch(self):
        '''
        This is called every time a generator returns a value.  It increments
        the current epoch and also triggers garbage collection when there are
        outstanding generators.
        '''
        self.__epoch += 1
        if self.__overdue: self.__check()
        return self.__epoch
    
    def register(self, wrapper):
        '''
        This is called every time a generator is created (when the generator
        returns its first value).
        '''
        self.__check(wrapper)
        
    def __check(self, wrapper=None):
        '''
        If we delete a generator when one is added then we keep a constant 
        number; if we fail to delete one when the queue is full then we set 
        "overdue" and do an additional delete each time a generator is called.
        
        Note - no proof that this covers the total amortized cost - stack
        may grow anyway.
        ''' 
        if self.__max_size > 0:
            self.__overdue = False
            # if we've entered via overdue, bootstrap
            if wrapper == None and len(self.__queue) > self.__max_size:
                self._debug('Bootstrapping check with {0} ({0.epoch})'
                            .format(wrapper))
                wrapper = heappop(self.__queue)
            else:
                self._debug('Registering {0} ({0.epoch})'.format(wrapper))
            # if we have space, simply save with no expiry
            if len(self.__queue) < self.__max_size:
                self._debug('Free space, so add {0}'.format(wrapper))
                heappush(self.__queue, wrapper)
            else:
                # otherwise, try to delete the oldest
                candidate = heappop(self.__queue)
                self._debug('Exchanged {0} for {1}'.format(wrapper, candidate))
                candidate.update()
                # if we cannot delete, return and flag overdue
                if candidate.exists and \
                    (candidate.active or not candidate.stable):
                    self._debug('{0} not suitable for deletion '
                                '(active: {0.active}, stable:{0.stable})'
                                .format(candidate))
                    # if active, update epoch to current value so that we do not
                    # re-extract (it will be updated again on returning a
                    # value)
                    if candidate.active:
                        candidate.epoch = self.__epoch
                        self._debug('Updated {0} epoch ({0.epoch})'
                                    .format(candidate))
                    # return
                    self._debug('Returning {0}; overdue'.format(candidate))
                    heappush(self.__queue, candidate)
                    self.__overdue = True
                else:
                    self._debug('Close and discard {0}'.format(candidate))
                    # free resources, discard
                    candidate.close()
