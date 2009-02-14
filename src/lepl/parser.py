
from types import MethodType, GeneratorType


from lepl.core import CoreConfiguration
from lepl.graph import order, FORWARD, preorder, clone, Clone, post_clone
from lepl.manager import managed, GeneratorWrapper
from lepl.operators import Matcher
from lepl.stream import Stream
    
    
class Configuration(CoreConfiguration):
    
    def __init__(self, flatten=None, memoizers=None, queue_len=None, trace_len=None):
        super(Configuration, self).__init__(queue_len, trace_len)
        self.flatten = [] if flatten is None else flatten 
        self.memoizers = [] if memoizers is None else memoizers
        
        
#DECORATORS = 'decorators'
#DEFAULT_DECORATORS = [managed]
#
#def decorate_generators(matcher, decorator):
#    for m in order(matcher, FORWARD, type_=Matcher):
#        m.match = MethodType(decorator(m.match.__func__), m)
#    return matcher
#
#def decorate(matcher, options):
#    (options, decorators) = opt_karg(options, DECORATORS, DEFAULT_DECORATORS)
#    for decorator in decorators:
#        matcher = decorate_generators(matcher, decorator)
#    return (matcher, options)


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
    

def flatten(matcher, conf):
    if conf.flatten:
        matcher = matcher.postorder(Clone(make_flatten(conf.flatten)))
    return matcher


def memoize(matcher, conf):
    for memoizer in conf.memoizers:
        matcher = matcher.postorder(Clone(post_clone(memoizer)))
    return matcher


def trampoline(main):
    stack = []
    value = main
    exception = False
    while True:
        try:
            if type(value) in (GeneratorType, GeneratorWrapper):
                stack.append(value)
                value = next(value)
            else:
                stack.pop()
                if stack:
                    if exception:
                        exception = False
                        value = stack[-1].throw(value)
                    else:
                        value = stack[-1].send(value)
                else:
                    if exception:
                        raise value
                    else:
                        yield value
                    value = main
        except Exception as e:
            if exception:
                raise value
            else:
                value = e
                exception = True
    
    
def prepare(matcher, stream, conf):
    matcher = flatten(matcher, conf)
    matcher = memoize(matcher, conf)
    parser = lambda arg: trampoline(matcher(stream(arg, conf)))
    parser.matcher = matcher
    return parser


def make_parser(matcher, stream, conf):
    matcher = prepare(matcher, stream, conf)
    def single(arg):
        try:
            return next(matcher(arg))[0]
        except StopIteration:
            return None
    single.matcher = matcher.matcher
    return single

    
def make_matcher(matcher, stream, conf):
    return prepare(matcher, stream, conf)

    
def file_parser(matcher, conf):
    return make_parser(matcher, Stream.from_file, conf)

def list_parser(matcher, conf):
    return make_parser(matcher, Stream.from_list, conf)

def path_parser(matcher, conf):
    return make_parser(matcher, Stream.from_path, conf)

def string_parser(matcher, conf):
    return make_parser(matcher, Stream.from_string, conf)


def file_matcher(matcher, conf):
    return make_matcher(matcher, Stream.from_file, conf)

def list_matcher(matcher, conf):
    return make_matcher(matcher, Stream.from_list, conf)

def path_matcher(matcher, conf):
    return make_matcher(matcher, Stream.from_path, conf)

def string_matcher(matcher, conf):
    return make_matcher(matcher, Stream.from_string, conf)

