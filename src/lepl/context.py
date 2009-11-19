
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
Allow global per-thread values to be defined within a certain scope.  This
allows with contexts to influence local statements.
'''

from collections import deque
#from logging import getLogger
from threading import local

from lepl.support import singleton, format


class ContextError(Exception):
    '''
    Exception raised on problems with context.
    '''
    pass


# pylint: disable-msg=R0903
class NamespaceMap(local):
    '''
    A store for namespaces.
    
    This subclasses threading.local so each thread effectively has its own 
    instance (see test).
    '''
    
    def __init__(self):
        super(NamespaceMap, self).__init__()
        self.__map = {}
        
    def get(self, name, default=None):
        '''
        This gets the namespace associated with the name, creating a new
        namespace from the second arguent if necessary.
        '''
        from lepl.operators import DefaultNamespace
        if name not in self.__map:
            self.__map[name] = DefaultNamespace() if default is None \
                                                  else default()
        return self.__map[name] 


class Namespace(object):
    '''
    A store for global definitions.
    '''
    
    def __init__(self, base=None):
        self.__stack = deque([{} if base is None else base])
        
    def push(self, extra=None):
        '''
        Copy the current state to the stack and modify it.  Values in extra
        that map to None are ignored.
        '''
        self.__stack.append(dict(self.current()))
        extra = {} if extra is None else extra
        for name in extra:
            self.set_if_not_none(name, extra[name])
        
    def pop(self):
        '''
        Return the previous state from the stack.
        '''
        self.__stack.pop()
        
    def __enter__(self):
        '''
        Allow use within a with context by duplicating the current state
        and saving to the stack.  Returns self to allow manipulation via set.
        '''
        self.push()
        return self
       
    def __exit__(self, *_args):
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
        
    def set_if_not_none(self, name, value):
        '''
        Set a value if it is not None.
        '''
        if value != None:
            self.set(name, value)
            
    def get(self, name, default):
        '''
        Get a value if defined, else the default.
        '''
        return self.current().get(name, default)
    
    
class OnceOnlyNamespace(Namespace):
    '''
    Allow some values to be set only once.
    '''
    
    def __init__(self, base=None, once_only=None):
        super(OnceOnlyNamespace, self).__init__(base)
        self.__once_only = set() if once_only is None else once_only
        
    def once_only(self, name):
        '''
        The given name can be set only once.
        '''
        self.__once_only.add(name)
        
    def set(self, name, value):
        '''
        Set a value (if it has not already been set).
        '''
        if name in self.__once_only and self.get(name, None) is not None:
            raise ContextError(format('{0} can only be set once', name))
        else:
            super(OnceOnlyNamespace, self).set(name, value)
        

# pylint: disable-msg=C0103, W0603
def Global(name, default=None):
    '''
    Global (per-thread) binding from operator name to implementation, by
    namespace.
    '''
    # Delay creation to handle circular dependencies.
    assert name
    namespace_map = singleton(NamespaceMap)
    return namespace_map.get(name, default)


class NamespaceMixin(object):
    '''
    Allow access to global (per-thread) values.
    '''

    def __init__(self, name, namespace):
        super(NamespaceMixin, self).__init__()
        self.__name = name
        self.__namespace = namespace
        
    def _lookup(self, name, default=None):
        '''
        Retrieve the named namespace from the global (per thread) store.
        '''
        return Global(self.__name, self.__namespace).get(name, default)


class Scope(object):
    '''
    Base class supporting dedicated syntax for particular options.
    '''

    def __init__(self, name, namespace, frame):
        self.__name = name
        self.__namespace = namespace
        self.__frame = frame
        
    def __enter__(self):
        '''
        On entering the context, add the new definitions.
        '''
        Global(self.__name, self.__namespace).push(self.__frame)
        
    def __exit__(self, *_args):
        '''
        On leaving the context, return to previous definition.
        '''
        Global(self.__name, self.__namespace).pop()


