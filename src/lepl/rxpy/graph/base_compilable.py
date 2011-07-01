#LICENCE

'''
Base classes for opcodes and compilation.

The graph nodes defined in lepl.rxpy.graph.base focus only on graphs.  But
these graphs are used to drive matching of a regular expression - they are
opcodes that are interpreted by various engines.  So the classes here are
mixins that provide this additional functionality.
'''

from lepl.rxpy.graph.support import node_iterator
from lepl.rxpy.support import UnsupportedOperation
from lepl.support.lib import unimplemented


#noinspection PyUnusedLocal
class BaseMatchTarget(object):
    '''
    The interface against which the opcodes "execute" when matching.  In
    simple terms, an engine implements the methods below, and the graph
    node calls the appropriate method.

    In practice, there is an initial "compilation" step in which the node
    is passed the engine and returns a function that, when called, calls the
    interface.  This allows any "once only" pre-computation to be done before
    matching.

    Note that the arguments and in alphabetical order(!).  This is used by
    `BaseCompilableMixin` below to map from node attributes to method args.
    This ties in with the node constructor arguments via `AutoClone`.
    '''

    def string(self, next, text, length):
        '''Match the given literal.'''
        raise UnsupportedOperation('string')

    def character(self, charset):
        '''Match the given character (more exactly, a "string" of length 1).'''
        raise UnsupportedOperation('character')

    def start_group(self, number):
        '''Start a numbered group.'''
        raise UnsupportedOperation('start_group')

    def end_group(self, number):
        '''End a numbered group (called symmetrically with `start_group()`).'''
        raise UnsupportedOperation('end_group')

    def match(self):
        '''Indicate a successful (end of) a match.'''
        raise UnsupportedOperation('match')

    def no_match(self):
        '''Indicate a failure to match.'''
        raise UnsupportedOperation('no_match')

    def dot(self, multiline):
        '''Match "any" character (exact details depend on regexp options).'''
        raise UnsupportedOperation('dot')

    def start_of_line(self, multiline):
        '''Match the start of a line.'''
        raise UnsupportedOperation('start_of_line')

    def end_of_line(self, multiline):
        '''Match the end of a line.'''
        raise UnsupportedOperation('end_of_line')

    def word_boundary(self, inverted):
        '''Match a word boundary.'''
        raise UnsupportedOperation('word_boundary')

    def digit(self, inverted):
        '''Match a digit.'''
        raise UnsupportedOperation('digit')

    def space(self, inverted):
        '''Match a space character.'''
        raise UnsupportedOperation('space')

    def word(self, inverted):
        '''Match a word.'''
        raise UnsupportedOperation('word')

    def checkpoint(self, id):
        '''
        Successive calls to checkpoint with the same id must consume text.
        If they don't, there is an error (a repeating empy loop) and the
        engine should abort (raise an exception).
        '''
        raise UnsupportedOperation('checkpoint')

    # following opcodes allow branching

    def group_reference(self, next, number):
        '''Match a previously matched group.'''
        raise UnsupportedOperation('group_reference')

    def conditional(self, next, number):
        '''Condition on a previously matched group.'''
        raise UnsupportedOperation('conditional')

    def split(self, next):
        '''
        A branch (alternatives ordered by priority).
        For example, this is used to implement repetition.
        '''
        raise UnsupportedOperation('split')

    def lookahead(self, next, equal, forwards):
        '''Perform a lookahead match.'''
        raise UnsupportedOperation('lookahead')

    def repeat(self, next, begin, end, lazy):
        '''Perform a counted repetition.'''
        raise UnsupportedOperation('repeat')


class BaseReplaceTarget(object):
    '''
    As `BaseMatchTarget`, but for replacing results (eg. using `re.sub()`).
    '''

    def string(self, next, text, length):
        '''Literal text replacement.'''
        raise UnsupportedOperation('string')

    def group_reference(self, next, number):
        '''Replace with matched data.'''
        raise UnsupportedOperation('group_reference')

    def match(self):
        '''Indicate a successful (end of) a replacement.'''
        raise UnsupportedOperation('match')


def compile(graph, target):
    '''
    Compilation is a two-step process that supports (1) pre-computation of
    values and (2) rapid access to other nodes.

    A compiled node is a function that takes no arguments and returns the
    next compiled node for evaluation (the end of the process is signalled
    to the engine via the `.match()` and `.no_match()` callbacks above).

    It's non-trivial (I think?) to make an efficient closure that includes
    loops, so the compilation avoids this.  Instead, indices into an array
    of nodes are used.  So the compilation process works as follows:
      1. - The `.compile()` method is passed the engine (`BaseMatchTarget` above)
           and numbered.  It returns a "compiler" function.
      2. - The compiler function is called with the map from nodes to indices
           and the (future) table of compiled nodes by index.  This converts
           any node references to indices and returns the "compiled" node,
           which is stored in the table.
    At run-time, when the compiled node is called it must:
      3. - Call the target interface as necessary.
      4. - Return the next node.  To obtain the next node it will use the
           indices generated above to lookup the node from the table.
    Note that the state (position in the input text, matched groups, etc) is
    managed by the engine itself.  The nodes simply trigger the correct
    processing.
    '''
    compilers = [(node, node.compile(target)) for node in node_iterator(graph)]
    node_index = dict((node, index)
                      for (index, (node, _compiler)) in enumerate(compilers))
    table = []
    for (node, compiler) in compilers:
        table.append(compiler(node_index, table))
    return table


class BaseCompilableMixin(object):
    '''
    Mixin with support for compiling nodes.   This assumes it will be used
    with `AutoClone` (which provides `._kargs()`), while subclasses assume
    `BaseNode` (which provides `.next`).
    '''

    #noinspection PyArgumentList
    def __init__(self, *args, **kargs):
        super(BaseCompilableMixin, self).__init__(*args, **kargs)

    def _compile_name(self):
        '''
        If classes are named after the methods on `BaseMatchTarget` that they will
        call then we can find the correct name by converting from CamelCase
        to dash_separated.
        '''
        def with_dashes(name):
            '''Lower-case and insert dashes between words.'''
            first = True
            for letter in name:
                if letter.isupper() and not first:
                    yield '_'
                first = False
                yield letter.lower()
        return ''.join(with_dashes(self.__class__.__name__))

    #noinspection PyUnusedLocal
    @unimplemented
    def compile(self, compiled):
        '''
        Compile the node.  See the `compile()` function for full details.
        '''
        pass

    def _compile_args(self):
        '''
        The method arguments in `BaseMatchTarget` are in alphabetical order.
        This method maps from node attributes (kargs via `AutoClone`) to
        the method arguments.
        '''
        #noinspection PyUnresolvedReferences
        kargs = self._kargs()
        return list(kargs[name] for name in sorted(kargs))


class SimpleCompilableMixin(BaseCompilableMixin):
    '''
    A node that calls the target and then returns next state.  It assumes
    that the target method (named after the node) returns True on
    consumption and False otherwise.
    '''

    def compile(self, target):
        '''
        Compile the node.  See the `compile()` function for full details.
        '''
        method = getattr(target, self._compile_name())
        args = self._compile_args()
        return self._make_compiler(method, args)

    def _make_compiler(self, method, args):
        '''
        Given a target method and a list of arguments, generate a compiler
        that finds the next node ID and returns the compiled function.
        '''
        def compiler(node_to_index, table):
            '''Find the next ID and return the compiled function.'''
            try: # TODO - is this try necessary?
                #noinspection PyUnresolvedReferences
                next = node_to_index[self.next[0]]
            except IndexError:
                next = None
            def compiled():
                '''
                Evaluate and return next node.

                The node should return True if input is consumed.  Otherwise,
                it should return False and the next opcode is invoked immediately.
                This means that we only return to the caller when input is
                consumed (so position in input indicates state of system).
                '''
                if method(*args):
                    return next
                else:
                    return table[next]()
            return compiled
        return compiler


class BaseNodeIdCompilableMixin(SimpleCompilableMixin):
    '''
    Some nodes pass in a node ID as the first argument (see subclasses).
    This is a base class that supports such nodes by (1) allowing them
    to provide a modified set of args via `._compile_args()` and (2)
    translating the first argument to a node ID.
    '''
    # TODO - do we ever need the node id?

    @unimplemented
    def _compile_args(self):
        '''Subclasses add an extra node here, adding `._untranslated_args()`'''
        pass

    def _untranslated_args(self):
        '''Rename `._compile_args()` from the super class.'''
        return super(BaseNodeIdCompilableMixin, self)._compile_args()

    def _make_compiler(self, method, args):
        '''Extend the superclass with a conversion of args[0].'''
        def compiler(node_to_index, table):
            '''Extend the superclass with a conversion of args[0].'''
            try: # TODO - is this try necessary?
                #noinspection PyUnresolvedReferences
                next = node_to_index[self.next[0]]
            except IndexError:
                next = None
            args[0] = node_to_index[args[0]]
            def compiled():
                '''Evaluate and return next node.'''
                if method(*args):
                    return next
                else:
                    return table[next]()
            return compiled
        return compiler


class SelfIdCompilableMixin(BaseNodeIdCompilableMixin):
    '''
    First arg is `self`, transformed to index.
    '''

    def _compile_args(self):
        return [self] + list(self._untranslated_args())


class NextCompilableMixin(BaseNodeIdCompilableMixin):
    '''
    First arg is `next[0]`, transformed to index

    Expects to be combined with a `BaseNode` which provides .next.
    '''
    # TODO - why is next (first arg) nececssary at all?  is it used by any engine?

    def _compile_args(self):
        #noinspection PyUnresolvedReferences
        return [self.next[0]] + self._untranslated_args()


class BranchCompilableMixin(BaseCompilableMixin):
    '''
    Expects `method` to return the required index, which is evaluated until
    input is consumed.

    Expects to be combined with a `BaseNode` which provides .next.
    '''

    def compile(self, target):
        '''
        Compile the node.  See the `compile()` function for full details.
        '''
        method = getattr(target, self._compile_name())
        args = self._compile_args()
        def compiler(node_to_index, table):
            '''
            Call the method with a list of translated node IDs as the first arg,
            then return the node for the returned ID.
            '''
            #noinspection PyUnresolvedReferences
            next = list(map(lambda node: (node_to_index[node], node), self.next))
            new_args = [next] + args
            def compiled():
                '''When matching, invoke the branch selected.'''
                return table[next[method(*new_args)][0]]()
            return compiled
        return compiler
