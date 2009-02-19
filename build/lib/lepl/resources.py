
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
Manage resources.

We can attempt to control resource consumption by closing generators - the 
problem is which generators to close?

At first it seems that the answer is going to be connected to tree traversal,
but after some thought it's not so clear exactly what tree is being traversed,
and how that identifies what generators should be closed.  In particular, an 
"imperative" implementation with generators does not have the same meaning of 
"depth" as a recursive functional implementation (but see the related 
discussion in the `manual <../closing.html#search-and-backtracking>`_).

A better approach seems to be to discard those that have not been used "for a
long time".  A variation on this - keep a maximum number of the youngest 
generators - is practical.  But care is needed to both in identifying what is 
used, and when it starts being unused, and in implementing that efficiently.

Here all generators are stored in a priority queue using weak references.  The 
"real" priority is given by the "last used date" (a value read from a counter 
in core each time a value is returned), but the priority in the queue is
frozen when inserted.  So on removing from the queue the priority must be
checked to ensure it has not changed (and, if so, it must be updated with the
real value and replaced).

Note that the main aim here is to restrict resource consumption without 
damaging performance too much.  The aim is not to control parse results by 
excluding certain matches.  For efficiency, the queue length is increased 
(doubled) whenever the queue is filled by active generators.

For the control of parse results see the `lepl.match.Commit()` matcher.
'''

#from heapq import heappop, heappush
#try:
#    from heapq import heappushpop
#except ImportError: # Python 2.5
#    from heapq import heapreplace
#    def heappushpop(heap, item):
#        if heap and item < heap[0]:
#            return heapreplace(heap, item)
#        else:
#            return item
#from traceback import print_exc
#from weakref import ref
#
#from lepl.trace import LogMixin, traced
#
#
#class property2(property):
#
#    def setter(self, fget):
#        return property(self.fset, fget)
#
#
#def managed(f):
#    '''
#    Decorator for managed generators (ie all generators returned by
#    matchers)
#    '''
#    def call(self, stream):
#        return GeneratorWrapper(f(self, stream), self, stream)
#    return call
#
#
#class GeneratorWrapper(LogMixin):
#    '''
#    This provides basic support for the GC process, but uses normal 
#    references and exists within the main body of the code.  It is added
#    to generators via a decorator when first returned from a match object.
#    
#    It assumes that the match includes the logMixin, but is resilient to
#    simple list streams (in which case no GC will occur).
#    
#    Note - not implemented with BaseGeneratorWrapper because it just seemed
#    to confuse things more.
#    '''
#    
#    def __init__(self, generator, match, stream):
#        super(GeneratorWrapper, self).__init__()
#        self.__generator = generator
#        # we do try/except, rather than testing for stream's type, to simplify
#        # the dependency between modules
#        try:
#            # required by @traced
#            self.register = stream.core.bb.register
#            self.__description = stream.core.bb.preformatter(match, stream)
#        except:
#            self.register = lambda *args: None
#            self.__description = match.describe()
#        try:
#            self.__core = stream.core
#            self.epoch = 0
#            self.active = False
#            self.__registered = False
#            self.__managed = True
#        except:
#            self.__managed = False
#        self.__repr = repr(match)
#        self._debug('Created {0!r}, managed: {1}'.format(self, self.__managed))
#    
#    @traced
#    def __next__(self):
#        try:
#            if self.__managed:
#                self.active = True
#            return next(self.__generator)
#        finally:
#            if self.__managed:
#                self.update_epoch()
#                self.active = False
#                if not self.__registered:
#                    self.__core.gc.register(self)
#                    self.__registered = True
#                    
#    # for 2.6
#    def next(self):
#        return self.__next__()
#                
#    def update_epoch(self):
#        if self.active:
#            self.epoch = self.__core.gc.next_epoch()
#                
#    def __iter__(self):
#        return self
#                
#    def close(self):
#        self.__generator.close()
#        
#    def __str__(self):
#        return self.__description
#    
#    def __repr__(self):
#        return self.__repr
#
#
#class GeneratorRef():
#    '''
#    This contains the weak reference to the GeneratorWrapper and is stored
#    in the GC priority queue.
#    '''
#    
#    def __init__(self, wrapper):
#        self.__wrapper = ref(wrapper)
#        self.__last_known_epoch = wrapper.epoch
#        self.deletable = False
#        
#    def __lt__(self, other):
#        assert isinstance(other, GeneratorRef)
#        return self.__last_known_epoch < other.__last_known_epoch
#    
#    def __eq__(self, other):
#        return self is other
#    
#    def check(self):
#        '''
#        A generator is deletable if it no longer exists(!) or if the epoch
#        has not changed since it was registered (this is used as the priority
#        in the heap, so guarantees that the heap position is correct, since
#        other epochs can only increase).  A live generator cannot be deleted;
#        this is consistent with the statement above because a live element has
#        an updated epoch.
#        '''
#        wrapper = self.__wrapper()
#        if wrapper:
#            wrapper.update_epoch()
#            self.deletable = self.__last_known_epoch == wrapper.epoch
#            self.__last_known_epoch = wrapper.epoch
#        else:
#            self.deletable = True
#            
#    def active(self):
#        generator = self.__wrapper()
#        if generator:
#            return generator.active
#        else:
#            return False
#            
#    def close(self):
#        generator = self.__wrapper()
#        if generator:
#            generator.close()
#            
#    def __str__(self):
#        generator = self.__wrapper()
#        if generator:
#            return '{0!r} ({1})'.format(generator, self.__last_known_epoch)
#        else:
#            return 'Empty ref'
#    
#    def __repr__(self):
#        return str(self)
#
#
#class GeneratorControl(LogMixin):
#    '''
#    This manages the priority queue, etc.
#    '''
#    
#    def __init__(self, min_queue):
#        '''
#        The maximum size is only a recommendation - we do not discard active
#        generators so there is an effective minimum size which takes priority.
#        '''
#        super(GeneratorControl, self).__init__()
#        self.__min_queue = 0
#        self.__queue = []
#        self.__epoch = 0
#        self.min_queue = min_queue
#            
#    @property2
#    def min_queue(self):
#        '''
#        This is the current number of generators (effectively, the number of
#        'saved' matchers available for backtracking) that can exist at any one
#        time.  A value of zero disables the early deletion of generators, 
#        allowing full back-tracking.
#        
#        This is intended for freeing resources, not for controlling parse
#        results by restricting matches.  It may be increased by the system
#        (hence "min") when necessary.
#        '''
#        return self.__min_queue
#    
#    @min_queue.setter
#    def min_queue(self, min_queue):
#        self.__min_queue = min_queue
#        if min_queue is None:
#            self.__queue = None
#            self._debug('No monitoring of backtrack state.')
#        else:
#            if min_queue > 0:
#                self._debug('Queue size: {0}'.format(min_queue))
#            else:
#                self._debug('No limit to number of generators stored')
#        
#    def next_epoch(self):
#        '''
#        This is called every time a generator updates its state (typically on
#        first registering, on returning a value, and when being resubmitted
#        because it is in use).
#        '''
#        self.__epoch += 1
#        self._debug('Tick: {0}'.format(self.__epoch))
#        return self.__epoch
#    
#    def epoch(self):
#        return self.__epoch
#    
#    def register(self, wrapper):
#        '''
#        This is called every time a generator is created (when the generator
#        returns its first value).
#        '''
#        # do we need to worry at all about resources?
#        if self.__min_queue != None:
#            wrapper_ref = GeneratorRef(wrapper)
#            self.__add_and_delete(wrapper_ref)
#            return wrapper_ref
#        else:
#            return None
#        
#    def __add_and_delete(self, wrapper_ref):
#        '''
#        If we delete a generator when one is added then we keep a constant 
#        number.  So in 'normal' use this is fairly efficient (the
#        many loops are only needed when the queue is too small).
#        '''
#        self._debug('Queue size: {0}/{1}'
#                    .format(len(self.__queue), self.__min_queue))
#        # if we have space, simply save with no expiry
#        if self.__min_queue == 0 or len(self.__queue) < self.__min_queue:
#            self._debug('Free space, so add {0}'.format(wrapper_ref))
#            heappush(self.__queue, wrapper_ref)
#        else:
#            # we attempt up to 2*min_queue times to delete (once to update
#            # data; once to verify it is still active)
#            for retry in range(2 * len(self.__queue)):
#                candidate_ref = heappushpop(self.__queue, wrapper_ref)
#                self._debug('Exchanged {0} for {1}'
#                            .format(wrapper_ref, candidate_ref))
#                # if we can delete this, do so
#                if self.__deleted(candidate_ref):
#                    # check whether we have the required queue size
#                    if len(self.__queue) <= self.__min_queue:
#                        return
#                    # otherwise, try deleting the next entry
#                    else:
#                        wrapper_ref = heappop(self.__queue)
#                else:
#                    # try again (candidate has been updated)
#                    wrapper_ref = candidate_ref
#            # if we are here, queue is too small
#            heappush(self.__queue, wrapper_ref)
#            # this is currently 1 too small, and zero means unlimited, so
#            # doubling should always be sufficient.
#            self.min_queue = self.min_queue * 2
#            self._warn('Queue is too small - extending to {0}'
#                       .format(self.min_queue))
#    
#    def erase(self):
#        '''
#        Delete all non-active generators.
#        '''
#        if self.__queue:
#            for retry in range(len(self.__queue)):
#                candidate_ref = heappop(self.__queue)
#                if candidate_ref.active():
#                    candidate_ref.check() # forces epoch update
#                    heappush(self.__queue, candidate_ref)
#                else:
#                    candidate_ref.close()
#                
#    def __deleted(self, candidate_ref):
#        '''
#        Delete the candidate if possible.
#        '''
#        candidate_ref.check()
#        if candidate_ref.deletable:
#            self._debug('Close and discard {0}'.format(candidate_ref))
#            candidate_ref.close()
#        return candidate_ref.deletable
