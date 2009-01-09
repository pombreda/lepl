

class Any():
    
    def __init__(self):
        super().__init__()
    
    def __call__(self, text):
        '''
        Match any character and progress to the next.
        '''
        yield (text[0], text[1:])

    def __getitem__(self, index):
        '''
        
        '''