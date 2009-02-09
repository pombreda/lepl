

class Foo(object):
    
    def __init__(self):
        self.__bar = 1
    
    @property
    def _bar(self):
        return self.__bar
    
    @_bar.setter
    def _bar(self, bar):
        self.__bar = bar
    
    
if __name__ == '__main__':
    a -= Foo()
    a.bar = 1
    