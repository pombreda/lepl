
from lepl._circle.base import Base

class Second(Base):
    
    def __init__(self, *args):
        super(Second, self).__init__()
        self.__args = args
        
    def __repr__(self):
        return 'Second(%r)' % self.__args
    