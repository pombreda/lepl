
class Base(object):
    
    def __init__(self):
        from lepl._circle.first import First
        from lepl._circle.second import Second
        self.first = lambda *args: First(*args)
        self.second = lambda *args: Second(*args)
