
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
Encapsulate global (per thread) state.

This is for state that can affect the current parse.  It's probably simplest to
explain an example of what it can be used for.  Memoization records results
for a particular state to avoid repeating matches needlessly.  The state used
to identify when "the same thing is happening" is based on:
- the matcher being called
- the stream passed to the matcher
- this state

So a good shorthand for deciding whether or not this state should be used is
to ask whether the state will affect whether or not memoisation will work
correctly.

For example, with offside parsing, the current indentation level should be
stored here, because a (matcher, stream) combination that has previously failed
may work correctly when it changes. 
'''

from threading import local

from lepl.support import singleton


class State(local):
    '''
    A thread local map from key (typically calling class) to value.  The hash
    attribute is updated on each mutation and cached for rapid access. 
    '''
    
    def __init__(self):
        '''
        Do not call directly - use the singleton.
        '''
        super(State, self).__init__()
        self.__map = {}
        self.hash = self.__hash()
        
    @classmethod
    def singleton(cls):
        '''
        Get a singleton instance.
        '''
        return singleton(cls)
    
    def __hash(self):
        '''
        Calculate the hash for the current dict.
        '''
        value = 0
        for key in self.__map:
            value ^= hash(key) ^ hash(self.__map[key])
        return value
        
    def __getitem__(self, key):
        return self.__map[key]
    
    def get(self, key, default=None):
        '''
        As for dict (lookup with default).
        '''
        return self.__map.get(key, default)
    
    def __setitem__(self, key, value):
        self.__map[key] = value
        self.hash = self.__hash()
    
    def __delitem__(self, key):
        del self.__map[key]
        self.hash = self.__hash()
       
    def __hash__(self):
        return self.hash
