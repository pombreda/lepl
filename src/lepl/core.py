 
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
The core provides a central repository for 'global' data used during a parse.
'''

from lepl.resource import GeneratorControl
from lepl.trace import BlackBox


class Core():
    '''
    Data store for a single parse.
    A core instance is embedded in the streams used to wrap the text.
    
    It currently exposes these attributes:
    
    **source**
      The source of the data (a path, filename, or descriptive string of
      the form '<type>').
    
    **gc** 
      The `lepl.resources.GeneratorControl` instance that stores
      references to generators.
    
    **description_length**
      The amount of text to take from the stream when printing descriptions 
      (eg in debug messages).
      
    **bb**
      The `lepl.trace.BlackBox` instance that keeps a record of the longest
      match made.
    '''

    def __init__(self, source=None, min_queue=0, description_length=6, memory=0):
        '''
        Create a new core.  This is typically called during the creation of
        `lepl.stream.Stream`.
        
        :Parameters:
        
          min_queue
            The minimum length of the queue used to store backtrack
            state.  Legal values are:
            
            0 (zero, the default)
              The core will monitor backtracking state, but will not force
              early deletion.  So backtracking is unrestricted and
              `lepl.match.Commit` can be used.
              
            None
              The core will not monitor backtracking state.  Backtracking is
              unrestricted and the system may run more quickly (without the
              overhead of monitoring), but `lepl.match.Commit` will not work.
              
            A positive integer
              The core will monitor state and attempt to free resources when
              the number of generators reaches this value.  So the number
              gives an indication of "how much backtracking is possible" 
              (a larger value supports deeper searches).  Memory use should
              be reduced, but backtracking will be unreliable if the value
              is too small.  The value may be increased if the number of
              active generators is exceed the length of the queue.
          
          description_length
            The amount of text to take from the stream when printing 
            descriptions (eg in debug messages).
            
          memory
            The number of matches to store for the longest match.  This can
            be a triple (matches before, failures after, successes after) or
            a single value (equivalent to the triple (memory, 3, 3)).
        '''
        self.source = source
        self.gc = GeneratorControl(min_queue=min_queue)
        self.bb = BlackBox(self, memory=memory)
        self.description_length = description_length
        