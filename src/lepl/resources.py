
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


def managed(f):
    '''
    Decorator for managed generators (ie all generators returned by
    matchers)
    '''
    def call(self, stream):
        return GeneratorWrapper(f(self, stream), self, stream)
    return call


class GeneratorWrapper(LogMixin):
    '''
    This provides basic support for the GC process, but uses normal 
    references and exists within the main body of the code.  It is added
    to generators via a decorator when first returned from a match object.
    
    It assumes that the match includes the logMixin, but is resilient to
    simple list streams (in which case no GC will occur).
    '''
    
    def __init__(self, generator, match, stream):
        super().__init__()
        self.__generator = generator
        self.__description = '%s@%s' % (match.describe(), stream)
        # we do this, rather than testing for stream's type, to simplify
        # the dependency between modules
        try:
            self.__core = stream.core
            self.__registered = False
            self.epoch = 0
            self.active = False
            self.__managed = True
        except:
            self.__managed = False
        self._debug('Created {0}, managed: {1}'.format(self, self.__managed))
    
    def __next__(self):
        try:
            if self.__managed:
                self.active = True
                if not self.__registered:
                    self.update_epoch()
                    self.__core.gc.register(self)
            return next(self.__generator)
        finally:
            if self.__managed:
                self.update_epoch()
                self.active = False
                
    def update_epoch(self):
        self.epoch = self.__core.gc.next_epoch()
                
    def __iter__(self):
        return self
                
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
        self.__last_known_epoch = wrapper.epoch
        self.deletable = False
        
    def __lt__(self, other):
        assert isinstance(other, GeneratorRef)
        return self.__last_known_epoch < other.__last_known_epoch
    
    def __eq__(self, other):
        return self is other
    
    def update(self):
        wrapper = self.__wrapper()
        if wrapper:
            if wrapper.active: wrapper.update_epoch()
            self.deletable = self.__last_known_epoch == wrapper.epoch
            if not self.deletable: self.__last_known_epoch = wrapper.epoch
        else:
            self.deletable = True
            
    def close(self):
        generator = self.__wrapper()
        if generator:
            generator.close()
            
    def __str__(self):
        generator = self.__wrapper()
        if generator:
            return '{0} ({1})'.format(generator, self.__last_known_epoch)
        else:
            return 'Empty ref'
    
    def __repr__(self):
        return str(self)


class GeneratorControl(LogMixin):
    '''
    This manages the priority queue, etc.
    '''
    
    def __init__(self, max_queue):
        '''
        The maximum size is only a recommendation - we do not discard active
        generators so there is an effective minimum size which takes priority.
        '''
        super().__init__()
        self.__max_queue = 0
        self.__queue = []
        self.__epoch = 0
        self.max_queue = max_queue
            
    @property
    def max_queue(self):
        '''
        This is the maximum number of generators (effectively, the number of
        'saved' matchers available for backtracking) that can exist at any one
        time.  It is not exact, because generators that are currently in use
        cannot be deleted.  A value of zero disables the early deletion of
        generators, allowing full back-tracking.
        '''
        return self.__max_queue
    
    @max_queue.setter
    def max_queue(self, max_queue):
        if max_queue == 0:
            # discard any known generators
            self.__queue = []
        self.__max_queue = max_queue
        self.__ideal_max_queue = max_queue
        if self.__max_queue > 0:
            self._debug('Maximum number of generators: {0}'
                        .format(max_queue))
        else:
            self._debug('No limit to number of generators stored')
        
    def next_epoch(self):
        '''
        This is called every time a generator updates its state (typically on
        first registering, on returning a value, and when being resubmitted
        because it is in use).
        '''
        self.__epoch += 1
        self._debug('Tick: {0}'.format(self.__epoch))
        return self.__epoch
    
    def register(self, wrapper):
        '''
        This is called every time a generator is created (when the generator
        returns its first value).

        If we delete a generator when one is added then we keep a constant 
        number.  So in 'normal' use i hope this is fairly efficient (the
        many loops are only needed when the queue is too small).
        '''
        # do we need to worry at all about resources?
        if self.__max_queue > 0:
            wrapper_ref = GeneratorRef(wrapper)
            self._debug('Queue size: {0}/{1}'
                        .format(len(self.__queue), self.__max_queue))
            self._debug(self.__queue)
            # if we have space, simply save with no expiry
            if len(self.__queue) < self.__max_queue:
                self._debug('Free space, so add {0}'.format(wrapper_ref))
                heappush(self.__queue, wrapper_ref)
            else:
                # we attempt up to 2*max_queue times to delete (once to update
                # data, once to verify it is still active)
                for retry in range(2 * self.__max_queue):
                    candidate_ref = heappushpop(self.__queue, wrapper_ref)
                    self._debug('Exchanged {0} for {1}'
                                .format(wrapper_ref, candidate_ref))
                    # if we can delete this, do so
                    if self.__deleted(candidate_ref):
                        # check whether we have the required queue size
                        if len(self.__queue) <= self.__max_queue:
                            return
                        # otherwise, try deleting the next entry
                        else:
                            wrapper_ref = heappop(self.__queue)
                    else:
                        # try again (candidate has been updated)
                        wrapper_ref = candidate_ref
                # if we are here, queue is too small
                heappush(self.__queue, wrapper_ref)
                self._warn('Queue is too small - temporarily extending to {0}'
                           .format(len(self.__queue)))
                self._warn('The parser will run significantly slower')
                
    def __deleted(self, candidate_ref):
        '''
        Delete the candidate if possible.
        '''
        candidate_ref.update()
        if candidate_ref.deletable:
            self._debug('Close and discard {0}'.format(candidate_ref))
            candidate_ref.close()
        return candidate_ref.deletable
    
