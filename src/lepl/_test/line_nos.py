
from lepl import *

def with_line(node):
    def wrapper(results, stream_out, **kargs):
        return node(results, ('line_no', s_delta(stream_out)[1]))
    return wrapper

class Greeting(Node): pass
newline = ~Literal('\n')
space = ~Space()
padding = (space | newline)[:]
line = padding & (Literal('howdy:') ** with_line(Greeting)) & padding

ast = line.parse('   \n \n \n howdy: \n \n\n  ')
print(ast[0])



class Block(List): pass

def with_line(node):
    def wrapper(results, stream_in, stream_out):
        print('inside')
        a = s_delta(stream_in)[1]
        try:
            b = s_delta(stream_out)[1]
        except StopIteration:
            b = 'eof'
        return node([results, a, b])
    return wrapper

identifier = Token('[a-zA-Z][a-zA-Z0-9_]*') > List
symbol = Token('[^0-9a-zA-Z \t\r\n]')


#block = (~symbol('{') & (identifier | symbol)[0:] ** with_line(Block) & ~symbol('}')) # V1
block = (~symbol('{') & (identifier | symbol)[0:] & ~symbol('}')) ** with_line(Block) # V2

parser = block.get_parse()

print(parser('{\n Andrew \n}')[0])

