
from logging import getLogger
from traceback import print_exc, format_exc
from types import MethodType, GeneratorType

from lepl.core import CoreConfiguration
from lepl.graph import order, FORWARD, preorder, clone, Clone, post_clone
from lepl.monitor import MultipleMonitors
from lepl.operators import Matcher
from lepl.stream import Stream
from lepl.support import BaseGeneratorWrapper
from lepl.trace import TraceResults, RecordDeepest
    
    
def tagged(call):
    '''
    Decorator for generators to add extra attributes.
    '''
    def tagged_call(matcher, stream):
        return GeneratorWrapper(call(matcher, stream), matcher, stream)
    return tagged_call


class GeneratorWrapper(BaseGeneratorWrapper):
    '''
    Associate basic info about call that created the generator with the 
    generator itself.  This lets us manage resources and provide logging.
    '''

    def __init__(self, generator, matcher, stream):
        super(GeneratorWrapper, self).__init__(generator)
        self.matcher = matcher
        self.stream = stream
        self.describe = '{0}({1})'.format(matcher.describe, stream)
        
    def __repr__(self):
        return self.describe
        

class Configuration(object):
    
    def __init__(self, flatten=None, memoizers=None, monitors=None):
        self.flatten = [] if flatten is None else flatten 
        self.memoizers = [] if memoizers is None else memoizers
        if not monitors:
            self.monitor = None
        elif len(monitors) == 1:
            self.monitor = monitors[0]
        else:
            self.monitor = MultipleMonitors(monitors)
            
        
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
        matcher = matcher.postorder(Clone(post_clone(memoizer)))
    return matcher


def trampoline(main, monitor=None):
    stack = []
    value = main
    exception = False
    epoch = 0
    log = getLogger('lepl.parser.trampoline')
    last_exc = None
    while True:
        epoch += 1
        try:
            if monitor: monitor.next_iteration(epoch, value, exception, stack)
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
            if exception: # raising to caller
                raise
            else:
                value = e
                exception = True
                if monitor: monitor.exception(value)
                if type(value) is not StopIteration and value != last_exc:
                    last_exc = value
                    log.warn(format_exc())
                    for generator in stack:
                        log.warn('Stack: ' + generator.matcher.describe)
                
    
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

