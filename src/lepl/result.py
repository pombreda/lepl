

class ResultMixin():
    
    def __rshift__(self, *spec):
        return Result(self, *spec)
    
    
class Result():
    
    def __init__(self, *spec):
        '''
        We support dual syntax here - spec may be a single string or 
        '''
        