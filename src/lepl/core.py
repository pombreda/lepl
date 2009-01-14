 
'''
The core provides a central repository for 'global' data used during a parse.
'''

from lepl.resources import GeneratorControl


class Core():
    '''
    Data store for a single parse.
    A core instance is embedded in the streams used to wrap the text.
    
    It currently exposes two attributes:
    
    **gc** 
      The `lepl.GeneratorControl` instance that monitors backtracking state.
    
    **description_length**
      The amount of text to take from the stream when printing descriptions 
      (eg in debug messages).
    '''

    def __init__(self, min_queue=0, description_length=6):
        '''
        Create a new core.  This is typically called during the creation of
        `lepl.stream.Stream`.
        
        :Parameters:
        
          min_queue
            The minimum length of the queue used to store backtrack
            state.  Legal values include:
            
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
        '''
        self.gc = GeneratorControl(min_queue)
        self.description_length = description_length
        