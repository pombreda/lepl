
from lepl import *

def with_line(node):
    def wrapper(results, stream_out, **kargs):
        return node(results, ('lineno', s_delta(stream_out)[1]))
    return wrapper

class Greeting(Node): pass
newline = ~Literal('\n')
space = ~Space()
padding = (space | newline)[:]
line = padding & (Literal('howdy:') ** with_line(Greeting)) & padding

ast = line.parse('   \n \n \n howdy: \n \n\n  ')
print(ast[0])
