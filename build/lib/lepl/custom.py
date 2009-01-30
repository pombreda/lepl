
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
Allow the redefinition of operators.
'''

from threading import local


class Namespace(local):
    '''
    A store for operator definitions.
    
    This subclasses threading.local so each thread effectively has its own 
    instance (see test).
    '''
    
    def __init__(self):
        super(Namespace, self).__init__()
        self.__stack = [{}]
        
    def push(self, extra={}):
        '''
        Add further names, savign the current state to the stack.
        '''
        self.__stack.append(dict(self.current()))
        for name in extra:
            self.set_opt(name, extra[name])
        
    def pop(self):
        '''
        Return the previous state from the stack.
        '''
        self.__stack.pop(-1)
        
    def __enter__(self):
        '''
        Allow use within a with context by duplicating the current state
        and saving to the stack.  Returns self to allow manipulation via set.
        '''
        self.push()
        return self
        
    def __exit__(self, *args):
        '''
        Restore the previous state from the stack on leaving the context.
        '''
        self.pop()
        
    def current(self):
        '''
        The current state (a map from names to operator implementations).
        '''
        return self.__stack[-1]
    
    def set(self, name, value):
        '''
        Set a value.
        '''
        self.current()[name] = value
        
    def set_opt(self, name, value):
        '''
        Set a value if it is not None.
        '''
        if value != None:
            self.set(name, value)
        
    def get(self, name, default=None):
        '''
        Get a value.  If there is no entry for the given name, return default. 
        '''
        return self.current().get(name, default)
    

NAMESPACE = Namespace()
'''Global (per-thread) binding from operator name to implementation'''

SPACE_OPT = '/'
'''Name for / operator.'''
SPACE_REQ = '//'
'''Name for // operator.'''
ADD = '+'
'''Name for + operator.'''
AND = '&'
'''Name for & operator.'''
OR = '|'
'''Name for | operator.'''
APPLY = '>'
'''Name for > operator.'''
NOT = '~'
'''Name for ~ operator.'''
ARGS = '*'
'''Name for * operator.'''
KARGS = '**'
'''Name for ** operator.'''
RAISE = '^'
'''Name for ^ operator.'''
REPEAT = '[]'
'''Name for [] operator.'''


class Override(object):
    '''
    Allow an operator to be redefined within a with context.
    '''

    def __init__(self, space_opt=None, space_req=None, repeat=None,
                  add=None, and_=None, or_=None, not_=None, 
                  apply=None, args=None, kargs=None, raise_=None):
        self.__frame ={SPACE_OPT: space_opt, SPACE_REQ: space_req,
                       REPEAT: repeat, ADD: add, AND: and_, OR: or_, 
                       NOT: not_, APPLY: apply, ARGS: args, KARGS: kargs, 
                       RAISE: raise_}
        
    def __enter__(self):
        '''
        On entering the context, add the new definitions.
        '''
        NAMESPACE.push(self.__frame)
        
    def __exit__(self, *args):
        '''
        On leaving the context, return to previous definition.
        '''
        NAMESPACE.pop()

