

from lepl.graph import Visitor, preorder, SimpleGraphNode, loops


def clone(node, args, kargs):
    '''
    Clone including matcher-specific attributes.
    '''
    from lepl.graph import clone as old_clone
    from lepl.matchers import Transformable
    copy = old_clone(node, args, kargs)
    if isinstance(node, Transformable):
        copy.function = node.function
    copy.describe = node.describe 
    return copy


class DelayedClone(Visitor):    
    '''
    A version of `lepl.parsers.Clone` that uses `lepl.matchers.Delayed` rather
    that `lepl.parsers.Proxy` to handle circular references.
    '''
    
    def __init__(self, clone=clone):
        super(DelayedClone, self).__init__()
        self._clone = clone
        self._delayeds = {}
    
    def loop(self, node):
        '''
        This is called for nodes that are arguments to Delayed.  Since we
        do not know those values yet, we return None.  We will fix the Delayed
        instances later.
        '''
        return None
    
    def node(self, node):
        self._node = node
        
    def constructor(self, *args, **kargs):
        # delayed import to avoid dependency loops
        from lepl.matchers import Delayed
        copy = self._clone(self._node, args, kargs)
        if isinstance(copy, Delayed):
            if self._node in self._delayeds:
                # we already created a replacement for this node, but it's
                # matcher may be contained None (from loop), so fix it
                # up and return it.
                self._delayeds[self._node].matcher = copy.matcher
                copy = already = self._delayeds[self._node]
            else:
                # otherwise, store this version for future use
                self._delayeds[self._node] = copy
        return copy
    
    def leaf(self, value):
        return value
    
    
def post_clone(function):
    '''
    Generate a clone function that applies the given function to the newly
    constructed node, except for Delayed instances (which are effectively
    proxies and so have no functionality of their own (so, when used with 
    `DelayedClone`, effectively performs a map on the graph).
    '''
    from lepl.matchers import Delayed
    def new_clone(node, args, kargs):
        copy = clone(node, args, kargs)
        if not isinstance(node, Delayed):
            copy = function(copy)
        return copy
    return new_clone


def flatten(graph):
    '''
    A rewriter that flattens ``And`` and ``Or`` lists.
    '''
    from lepl.matchers import And, Or
    def new_clone(node, old_args, kargs):
        table = {And: '*matchers', Or: '*matchers'}
        if type(node) in table:
            attribute_name = table[type(node)]
            new_args = []
            for arg in old_args:
                if type(arg) is type(node) and arg.function is node.function:
                    if attribute_name.startswith('*'):
                        new_args.extend(getattr(arg, attribute_name[1:]))
                    else:
                        new_args.append(getattr(arg, attribute_name))
                else:
                    new_args.append(arg)
        else:
            new_args = old_args
        return clone(node, new_args, kargs)
    return graph.postorder(DelayedClone(new_clone))


def compose_transforms(graph):
    '''
    A rewriter that joins adjacent transformations into a single
    operation, avoiding trampolining in some cases.
    '''
    from lepl.matchers import Transform, Transformable
    applied = set()
    def new_clone(node, args, kargs):
        # must always clone or don't know how to access matcher
        copy = clone(node, args, kargs)
        if isinstance(copy, Transform) \
                and isinstance(copy.matcher, Transformable):
            # avoid applying same transform twice via multiple paths
            if node not in applied:
                applied.add(node)
                copy.matcher.compose(copy.function)
            return copy.matcher
        else:
            return copy
    return graph.postorder(DelayedClone(new_clone))


def memoize(memoizer):
    '''
    A rewriter that adds the given memoizer to all nodes in the matcher
    graph.
    '''
    def rewriter(graph):
        return graph.postorder(DelayedClone(post_clone(memoizer)))
    return rewriter


def auto_memoize(conservative=True):
    from lepl.memo import RMemo
    '''
    Generate an all-purpose memoizing rewriter.  It is typically called after
    flattening and composing transforms.
    
    This rewrites the matcher graph to:
    1 - rewrite recursive `Or` calls so that terminating clauses are
    checked first.
    2 - add memoizers as appropriate
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    '''
    def rewriter(graph):
        graph = optimize_or(conservative)(graph)
        graph = context_memoize(conservative)(graph)
        return graph
    return rewriter


def left_loops(node):
    '''
    Return (an estimate of) all left-recursive loops from the given node.
    
    We cannot know for certain whether a loop is left recursive because we
    don't know exactly which parsers will consume data.  But we can estimate
    by assuming that all matchers eventually (ie via their children) consume
    something.  We can also improve that slightly by ignoring `Lookahead`.
    
    So we estimate left-recursive loops as paths that start and end at
    the given node, and which are first children of intermediate nodes
    unless the node is `lepl.matcher.Or`, or the preceding matcher is a
    `lepl.matcher.Lookahead`.  
    
    Each loop is a list that starts and ends with the given node.
    '''
    from lepl.matchers import Or, Lookahead
    stack = [[node]]
    while stack:
        ancestors = stack.pop()
        parent = ancestors[-1]
        if isinstance(parent, SimpleGraphNode):
            for child in parent._children():
                family = list(ancestors) + [child]
                if child is node:
                    yield family
                else:
                    stack.append(family)
                if not isinstance(parent, Or) and not isinstance(child, Lookahead):
                    break
    
                    
def either_loops(node, conservative):
    '''
    Select between the conservative and liberal loop detection algorithms.
    '''
    if conservative:
        return loops(node)
    else:
        return left_loops(node)
    

def optimize_or(conservative=True):
    '''
    Generate a rewriter that re-arranges ``Or`` matcher contents for
    left--recursive loops.
    
    When a left-recursive rule is used, it is much more efficient if it
    appears last in an `Or` statement, since that forces the alternates
    (which correspond to the terminating case in a recursive function)
    to be tested before the LMemo limit is reached.
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    
    `conservative` refers to the algorithm used to detect loops; False
    may classify some left--recursive loops as right--recursive.
    '''
    from lepl.matchers import Delayed, Or
    def rewriter(graph):
        for delayed in [x for x in preorder(graph) if type(x) is Delayed]:
            for loop in either_loops(delayed, conservative):
                for i in range(len(loop)):
                    if isinstance(loop[i], Or):
                        # we cannot be at the end of the list here, since that
                        # is a Delayed instance
                        matchers = loop[i].matchers
                        target = loop[i+1]
                        # move target to end of list
                        index = matchers.index(target)
                        del matchers[index]
                        matchers.append(target)
        return graph
    return rewriter


def context_memoize(conservative=True):
    '''
    Generate a memoizer that only applies LMemo to left recursive loops.
    Everything else can use the simpler RMemo.
    
    `conservative` refers to the algorithm used to detect loops; False
    may classify some left--recursive loops as right--recursive.
    '''
    from lepl.matchers import Delayed
    from lepl.memo import LMemo, RMemo
    def rewriter(graph):
        dangerous = set()
        for delayed in [x for x in preorder(graph) if type(x) is Delayed]:
            for loop in either_loops(delayed, conservative):
                for node in loop:
                    dangerous.add(node)
        def new_clone(node, args, kargs):
            '''
            Clone with the appropriate memoizer 
            (cannot use post_clone as need to test original)
            '''
            copy = clone(node, args, kargs)
            if isinstance(node, Delayed):
                # no need to memoize the proxy (if we do, we also break 
                # rewriting, since we "hide" the Delayed instance)
                return copy
            elif node in dangerous:
                return LMemo(copy)
            else:
                return RMemo(copy)
        return graph.postorder(DelayedClone(new_clone))
    return rewriter


def drop_nested(type_):
    '''
    Generate a rewriter that drops nested instances of the given type
    (the "outer" is discarded).
    '''
    def new_clone(node, args, kargs):
        copy = clone(node, args, kargs)
        all_args = list(args)
        for name in kargs:
            all_args.append(kargs[name])
        if len(all_args) == 1 and isinstance(copy, type_) \
                and isinstance(all_args[0], type_):
            return all_args[0]
        else:
            return copy
    return lambda graph: graph.postorder(DelayedClone(new_clone))
