
import sys

class Foo(object):
    
    def __rlshift__(self, name):
        try:
            raise Exception()
        except:
            locals = sys.exc_traceback.tb_frame.f_back.f_locals
            locals[name] = self

if __name__ == '__main__':
    'a' << Foo()
    print(a)
