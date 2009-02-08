
from types import MethodType

from lepl.graph import order, FORWARD 
from lepl.manager import managed
from lepl.operators import Matcher
from lepl.stream import Stream
    
    

def decorate_generators(matcher, decorator):
    for m in order(matcher, FORWARD, type_=Matcher):
        m.match = MethodType(decorator(m.match.__func__), m)
    return matcher

DECORATORS = 'decorators'
DEFAULT_DECORATORS = [managed]

def decorate(matcher, options):
    if DECORATORS in options:
        decorators = options[DECORATORS]
        del options[DECORATORS]
    else:
        decorators = DEFAULT_DECORATORS
    for decorator in decorators:
        matcher = decorate_generators(matcher, decorator)
    return (matcher, options)

    
def string_parser(matcher, **options):
    (matcher, options) = decorate(matcher, options)
    return lambda text: matcher(Stream.from_string(text, **options))

