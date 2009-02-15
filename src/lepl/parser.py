
from types import MethodType, GeneratorType

from lepl.core import CoreConfiguration
from lepl.graph import order, FORWARD, preorder, clone, Clone, post_clone
from lepl.operators import Matcher
from lepl.stream import Stream
from lepl.support import BaseGeneratorWrapper
from lepl.trace import TraceResults, RecordDeepest
    
    
def tagged(call):
    '''
    Decorator for generators to add extra attributes.
    '''
    def tagged_call(matcher, stream):
        return GeneratorWrapper(call(matcher, stream), stream, matcher)
    return tagged_call


class GeneratorWrapper(BaseGeneratorWrapper):
    '''
    Associate basic info about call that created the generator with the 
    generator itself.  This lets us manage resources and provide logging.
    '''

    def __init__(self, generator, stream, matcher):
        super(GeneratorWrapper, self).__init__(generator)
        self.stream = stream
        self.matcher = matcher
        

class Configuration(CoreConfiguration):
    
    def __init__(self, flatten=None, memoizers=None, monitor=None, queue_len=None):
        super(Configuration, self).__init__(queue_len)
        self.flatten = [] if flatten is None else flatten 
        self.memoizers = [] if memoizers is None else memoizers
        self.monitor = monitor
        
        
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


class CloneWithDescribe(Clone):
    
    def constructor(self, *args, **kargs):
        node = super(CloneWithDescribe, self).constructor(*args, **kargs)
        node.describe = self._node.describe
        return node    
    

def flatten(matcher, conf):
    if conf.flatten:
        matcher = matcher.postorder(CloneWithDescribe(make_flatten(conf.flatten)))
    return matcher


def memoize(matcher, conf):
    for memoizer in conf.memoizers:
        matcher = matcher.postorder(CloneWithDescribe(post_clone(memoizer)))
    return matcher


def trampoline(main, monitor=None):
    stack = []
    value = main
    exception = False
    while True:
        try:
            if monitor: monitor.next_iteration(value, exception, stack)
            if type(value) is GeneratorWrapper:
                if monitor: monitor.push(value)
                stack.append(value)
                if monitor: monitor.before_next(value)
                value = next(value)
                if monitor: monitor.after_next(value)
            else:
                pop = stack.pop()
                if monitor: monitor.pop(pop)
                if stack:
                    if exception:
                        exception = False
                        if monitor: monitor.before_throw(stack[-1], value)
                        value = stack[-1].throw(value)
                        if monitor: monitor.after_throw(value)
                    else:
                        if monitor: monitor.before_send(stack[-1], value)
                        value = stack[-1].send(value)
                        if monitor: monitor.after_send(value)
                else:
                    if exception:
                        if monitor: monitor.raise_(value)
                        raise value
                    else:
                        if monitor: monitor.yield_(value)
                        yield value
                    value = main
        except Exception as e:
            if exception:
                raise value
            else:
                value = e
                exception = True
                if monitor: monitor.exception(value)
                
    
def prepare(matcher, stream, conf):
    matcher = flatten(matcher, conf)
    matcher = memoize(matcher, conf)
    parser = lambda arg: trampoline(matcher(stream(arg, conf)), monitor=conf.monitor)
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

