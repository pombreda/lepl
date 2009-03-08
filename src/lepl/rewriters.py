

from lepl.graph import Visitor, clone, preorder, loops


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
        copy.describe = self._node.describe 
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


def flatten(spec):
    '''
    A rewriter that flattens the matcher graph according to the spec.
    
    The spec is a map from type to attribute name.  If type instances are 
    nested then the nested instance is replaced with the value(s) of the 
    attribute on the instance (see `make_flatten()`).
    '''
    def rewriter(matcher):
        return matcher.postorder(DelayedClone(make_flatten(spec)))
    return rewriter


def make_flatten(table):
    '''
    Create a function that can be applied to a graph of matchers to implement
    flattening.
    '''
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


def memoize(memoizer):
    '''
    A rewriter that adds the given memoizer to all nodes in the matcher
    graph.
    '''
    def rewriter(graph):
        return graph.postorder(DelayedClone(post_clone(memoizer)))
    return rewriter


def auto_memoize(graph):
    '''
    Rewrite the matcher graph to do two things:
    1 - add memoizers as appropriate
    2 - rewrite recursive `Or` calls so that terminating clauses are
    checked first.
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    '''
    graph = optimize_or(graph)
    graph = context_memoize(graph)
    return graph


def optimize_or(graph):
    '''
    When a left-recursive rule is used, it is much more efficient if it
    appears last in an `Or` statement, since that forces the alternates
    (which correspond to the terminating case in a recursive function)
    to be tested before the LMemo limit is reached.
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    '''
    from lepl.matchers import Delayed, Or
    for delayed in [x for x in preorder(graph) if type(x) is Delayed]:
        for loop in loops(delayed):
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


def context_memoize(graph):
    '''
    We only need to apply LMemo to left recursive loops.  Everything else
    can use the simpler RMemo.
    '''
    from lepl.matchers import Delayed
    from lepl.memo import LMemo, RMemo
    dangerous = set()
    for delayed in [x for x in preorder(graph) if type(x) is Delayed]:
        for loop in loops(delayed):
            for node in loop:
                dangerous.add(node)
    def clone(node, args, kargs):
        '''
        Clone with the appropriate memoizer 
        (cannot use post_clone as need to test original)
        '''
        clone = type(node)(*args, **kargs)
        if isinstance(node, Delayed):
            # no need to memoize the proxy (if we do, we also break 
            # rewriting, since we "hide" the Delayed instance)
            return clone
        elif node in dangerous:
            return LMemo(clone)
        else:
            return RMemo(clone)
    return graph.postorder(DelayedClone(clone))
