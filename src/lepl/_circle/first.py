
from lepl._circle.base import Base

class First(Base):
    
    def __init__(self, *args):
        super(First, self).__init__()
        self.__args = args
        
    def __repr__(self):
        return 'First(%r)' % self.__args
    