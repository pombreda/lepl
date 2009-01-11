
'''
A base class for AST nodes.  This is designed to be applied to a list of 
results, via ">".  If the list contains labelled pairs "(str, value)" then
these are added as (list) attributes; similarly for Node subclasses.
'''

class Node():
    
    def __init__(self, children):
        self.__args = []
        self.__named_args = {}
        for arg in args:
            try:
                (name, value) = arg
                if isinstance(name, Node):
                    name = name.__class__.__name__
                if name not in self.__named_args:
                    self.__named_args[name] = []
                self.__named_args[name].append(value)
            finally:
                self.__args.append(arg)
    
    def __getattr__(self, name):
        if name in self.__named_args:
            return self.__named_args[name]
        else:
            raise KeyError(name)
        
    def __getitem__(self, index):
        return self.__args[index]
    
    def __iter__(self):
        return self.__args
    
    def __str__(self):
        