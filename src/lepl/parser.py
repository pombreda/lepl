
from types import MethodType

from lepl.graph import order, FORWARD, preorder, clone, Clone
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
    (options, decorators) = opt_karg(options, DECORATORS, DEFAULT_DECORATORS)
    for decorator in decorators:
        matcher = decorate_generators(matcher, decorator)
    return (matcher, options)


TO_FLATTEN = 'to_flatten'
DEFAULT_TO_FLATTEN = {And:'*matchers', Or:'*matchers'}

def make_flatten(table):
    def flatten(node, old_args, kargs):
        if type(node) in table:
            attribute_name = table[type(node)]
            new_args = []
            for arg in old_args:
                if type(arg) is type(node):
                    if attribute_name.startswith('*'):
                        new_args.extend(getattr(arg, attribute_name[1:]))
                    else:
                        new_args.append(getattr(arg, attribute_name))
                else:
                    new_args.append(arg)
        else:
            new_args = old_args
        return clone(node, new_args, kargs)
    return flatten
    

def flatten(matcher, options):
    (options, to_flatten) = opt_karg(options, TO_FLATTEN, DEFAULT_TO_FLATTEN)
    if to_flatten:
        matcher = matcher.postorder(Clone(make_flatten(to_flatten)))
    return (matcher, options)

    
def string_parser(matcher, **options):
    (matcher, options) = flatten(matcher, options)
    # this must come after flattening, since that clones the tree
    (matcher, options) = decorate(matcher, options)
    parser = lambda text: matcher(Stream.from_string(text, **options))
    parser.matcher = matcher
    return parser

