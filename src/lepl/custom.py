
from threading import local


class Namespace(local):
    
    def __init__(self):
        super().__init__()
        self.__stack = [{}]
        
    def push(self, extra={}):
        self.__stack.append(dict(self.current()))
        for name in extra:
            self.set_opt(name, extra[name])
        
    def pop(self):
        self.__stack.pop(-1)
        
    def __enter__(self):
        self.push()
        
    def __exit__(self, *args):
        self.pop()
        
    def current(self):
        return self.__stack[-1]
    
    def set(self, name, value):
        self.current()[name] = value
        
    def set_opt(self, name, value):
        if value != None:
            self.set(name, value)
        
    def get(self, name, default=None):
        return self.current().get(name, default)
    

NAMESPACE = Namespace()

SPACE_OPT = '/'
SPACE_REQ = '//'
ADD = '+'
AND = '&'
OR = '|'
APPLY = '>'
NOT = '~'
ARGS = '*'
KARGS = '**'
RAISE = '^'
REPEAT = '[]'


class Override():

    def __init__(self, space_opt=None, space_req=None, repeat=None,
                  add=None, and_=None, or_=None, not_=None, 
                  apply=None, args=None, kargs=None, raise_=None):
        self.__frame ={SPACE_OPT: space_opt, SPACE_REQ: space_req,
                       REPEAT: repeat, ADD: add, AND: and_, OR: or_, 
                       NOT: not_, APPLY: apply, ARGS: args, KARGS: kargs, 
                       RAISE: raise_}
        
    def __enter__(self):
        NAMESPACE.push(self.__frame)
        
    def __exit__(self, *args):
        NAMESPACE.pop()

