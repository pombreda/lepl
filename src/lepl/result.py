
'''
Manage the results of parsing.
'''


class ResultMixin():
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
    
    def __rshift__(self, *spec):
        return Result(self, *spec)
    
    
class Result():
    
    def __init__(self, *spec):
        '''
        We support dual syntax here - spec may be a single string or 
        '''
        