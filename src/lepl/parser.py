
from types import MethodType

from lepl.graph import order, FORWARD, preorder
from lepl.manager import managed
from lepl.matchers import And, Or
from lepl.operators import Matcher
from lepl.stream import Stream
    
    

def opt_karg(options, name, default):
    if name in options:
        value = options[name]
        del options[name]
    else:
        value = default
    return (options, value)
    

DECORATORS = 'decorators'
DEFAULT_DECORATORS = [managed]

def decorate_generators(matcher, decorator):
    for m in order(matcher, FORWARD, type_=Matcher):
        m.match = MethodType(decorator(m.match.__func__), m)
    return matcher

def decorate(matcher, options):
    (options, decorators) = opt_karg(DECORATORS, DEFAULT_DECORATORS)
    for decorator in decorators:
        matcher = decorate_generators(matcher, decorator)
    return (matcher, options)


TO_FLATTEN = 'to_flatten'
DEFAULT_TO_FLATTEN = {And:'matchers', Or:'matchers'}

def flatten(matcher, **options):
    (options, to_flatten) = opt_karg(TO_FLATTEN, DEFAULT_TO_FLATTEN)
    nodes = preorder(matcher, type_=Matcher)
    for node in nodes:
        class_ = node.__class__
        if class_ in targets:
            children = getattr(node, targets[class_])
            for i in range(len(children)):
                child = children[i]
                if isinstance(child, class_):
                    grandchildren = getattr(child, targets[class_])
                    del children[i]
                    children.insert(i, grandchildren)
                    setattr(child, targets[class_], None)
                    reset(nodes)
    return (matcher, options)

    
def string_parser(matcher, **options):
    (matcher, options) = decorate(matcher, options)
    (matcher, options) = flattent(matcher, options)
    parser = lambda text: matcher(Stream.from_string(text, **options))
    parser.matcher = matcher
    return parser

