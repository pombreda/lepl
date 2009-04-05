
'''
Rewrite the tree of matchers from the bottom up (as far as possible)
using regular expressions.  This is complicated by a number of things.

First, intermediate parts of regular expressions are not matchers, so we need 
to keep them inside a special container type that we can detect and convert to
a regular expression when needed (since at some point we cannot continue with
regular expressions).

Second, we sometimes do not know if our regular expression can be used until we 
have moved higher up the matcher tree.  For example, And() might convert all
sub-expressions to a sequence if it's parent is an Apply(add).  So we may
need to store several alternatives, along with a way of selecting the correct
alternative.

So cloning a node may give either a matcher or a container.  The container
will provide both a matcher and an intermediate regular expression.  The logic
for handling odd dependencies is more difficult to implement in a general
way, because it is not clear what all cases may be.  For now, therefore,
we use a simple state machine approach using a tag (which is almost always
None).  
'''

from itertools import count
from logging import getLogger
from traceback import format_exc

from lepl.regexp.core import Choice, Sequence, Repeat, Option, Empty
from lepl.regexp.matchers import NfaRegexp
from lepl.regexp.interval import Character
from lepl.rewriters import copy_standard_attributes, clone, DelayedClone


class RegexpContainer(object):
    '''
    The container referred to above, which carries a regular expression and
    an alternative matcher "up the tree" during rewriting.
    '''
    
    def __init__(self, matcher, regexp, tag=None):
        self.matcher = matcher
        self.regexp = regexp
        self.tag = tag

    @staticmethod
    def to_regexp(possible, tag=None):
        if isinstance(possible, RegexpContainer):
            if possible.tag != tag:
                raise Tagged(possible.tag)
            else:
                return possible.regexp
        else:
            raise Unsuitable(possible)
        
    @staticmethod
    def to_matcher(possible):
        if isinstance(possible, RegexpContainer):
            return possible.matcher
        else:
            return possible
        
    @staticmethod
    def build(node, regexp, alphabet, matcher_type=NfaRegexp):
        '''
        If the node is a Transformable with a Transformation then we must
        stop at this point.
        '''
        from lepl.matchers import Transformable
        matcher = single(node, regexp, alphabet, matcher_type)
        if isinstance(node, Transformable) and node.function:
            return matcher
        else:
            return RegexpContainer(matcher, regexp)
        

def single(node, regexp, alphabet, matcher_type=NfaRegexp):
    '''
    Create a matcher for the given regular expression.
    '''
    # avoid dependency loops
    from lepl.matchers import Transformation
    matcher = matcher_type(regexp, alphabet)
    copy_standard_attributes(node, matcher, describe=False)
    return matcher.precompose_transformation(Transformation(empty_adapter))


def empty_adapter(results, sin, sout):
    '''
    There is a fundamental mis-match between regular expressions and the 
    recursive descent parser on how empty matchers are handled.  The main 
    parser uses empty lists; regexp uses an empty string.  This is a hack
    that converts from one to the other.  I do not see a better solution.
    '''
    if results == ['']:
        results = []
    return (results, sout)

        
class Unsuitable(Exception):
    '''
    Exception thrown when a sub-node does not contain a suitable matcher.
    '''
    pass

class Tagged(Unsuitable):
    '''
    Exception thrown when a sub-node does not contain a suitable matcher
    because of an unexpected tag.
    '''
    pass


# tag(s) used to indicate that a possible regexp has assumed something from
# parent nodes (if this is not met we must use the original matcher)
_TAG_ADD_REQUIRED = 1
'''
The parent matcher must join results with `and`.
'''


def make_clone(alphabet, old_clone, matcher_type):
    '''
    Factory that generates a clone suitable for rewriting recursive descent
    to regular expressions.
    '''
    
    # clone functions below take the "standard" clone and the node, and then
    # reproduce the normal argument list of the matcher being cloned.
    # they should return either a container or a matcher.
    
    # Avoid dependency loops
    from lepl.matchers \
        import Any, Or, And, Add, add, Transformable, \
        Transform, Transformation, Literal, DepthFirst, Apply

    LOG = getLogger('lepl.regexp.rewriters.make_clone')
    
    def clone_any(orignal, node, restrict=None):
        '''
        We can always convert Any() to a regular expression; the only question
        is whether we have an open range or not.
        '''
        assert not isinstance(node, Transformable)
        if restrict is None:
            char = Character([(alphabet.min, alphabet.max)], alphabet)
        else:
            char = Character(((char, char) for char in restrict), alphabet)
        LOG.debug('Any: cloned {0}'.format(char))
        regexp = Sequence([char], alphabet)
        return RegexpContainer.build(node, regexp, alphabet, matcher_type)
        
    def clone_or(original, node, *matchers):
        '''
        We can convert an Or only if all the sub-matchers have possible
        regular expressions.
        '''
        assert isinstance(node, Transformable)
        try:
            regexp = Choice((RegexpContainer.to_regexp(matcher) 
                             for matcher in matchers), alphabet)
            LOG.debug('Or: cloned {0}'.format(regexp))
            return RegexpContainer.build(node, regexp, alphabet, matcher_type)
        except Unsuitable:
            LOG.debug('Or not rewritten: {0!r}'.format(original))
            return original

    def clone_and(original, node, *matchers):
        '''
        We can convert an And only if all the sub-matchers have possible
        regular expressions, and even then we must tag the result unless
        an add transform is present.
        '''
        assert isinstance(node, Transformable)
        try:
            # if we have regexp sub-expressions, join them
            regexp = Sequence((RegexpContainer.to_regexp(matcher) 
                               for matcher in matchers), alphabet)
            LOG.debug('And: cloning {0}'.format(regexp))
            if len(node.function.functions) > 0 and node.function.functions[0] is add:
                # we can abuse original here, since it is discarded
                original.function = Transformation(node.function.functions[1:])
                LOG.debug('And: OK')
                return RegexpContainer(single(original, regexp, alphabet), 
                                       regexp)
            elif not node.function:
                LOG.debug('And: add required')
                return RegexpContainer(original, regexp, _TAG_ADD_REQUIRED)
            else:
                LOG.debug('And: wrong transformation: {0!r}'.format(
                          original.function))
                return original
        except Unsuitable:
            LOG.debug('And: not rewritten: {0!r}'.format(original))
            return original
    
    def clone_transform(original, node, matcher, function, raw=False, args=False):
        '''
        We can assume that function is a transformation.  The null 
        transformation has no effect on a regular expression; add joins into
        a sequence.
        '''
        assert isinstance(function, Transformation)
        try:
            regexp = RegexpContainer.to_regexp(matcher, tag=_TAG_ADD_REQUIRED)
            LOG.debug('Transform: cloning {0}'.format(regexp))
            if len(function.functions) > 0 and function.functions[0] is add:
                # we can abuse original here, since it is discarded
                original.function = Transformation(function.functions[1:])
                LOG.debug('Transform: OK')
                return RegexpContainer(single(original, regexp, alphabet),
                                       regexp)
            elif not function:
                LOG.debug('Transform: add required')
                return RegexpContainer(original, regexp, _TAG_ADD_REQUIRED)
            else:
                LOG.debug('Transform: wrong transformation: {0!r}'.format(
                          original.function))
                return original
        except Unsuitable:
            LOG.debug('Transform: not rewritten: {0!r}'.format(original))
            return original
        
    def clone_literal(original, node, text):
        '''
        Literal is transformable, so we need to be careful with any associated
        Transformation.
        
        We could return just the regexp matcher here.  But by itself a regexp
        is slower than a literal.  So we return a container pair so that the
        regexp is used only if it can be combined with something else.
        '''
        assert isinstance(node, Transformable)
        chars = [Character([(c, c)], alphabet) for c in text]
        regexp = Sequence(chars, alphabet)
        LOG.debug('Literal: cloned {0}'.format(regexp))
        return RegexpContainer(original, regexp)
#        return RegexpContainer.build(node, regexp, alphabet, matcher_type)
    
    def clone_dfs(original, node, first, start, stop, rest=None):
        '''
        We only convert DFS if start=0 or 1, stop=1 or None and first and 
        rest are both regexps.
        '''
        assert not isinstance(node, Transformable)
        try:
            if start not in (0, 1) or stop not in (1, None):
                raise Unsuitable()
            first = RegexpContainer.to_regexp(first)
            rest = RegexpContainer.to_regexp(rest)
            # we need to be careful here to get the depth first bit right
            if stop is None:
                regexp = Sequence([first, Repeat([rest], alphabet)], alphabet)
                if start == 0:
                    regexp = Choice([regexp, Empty(alphabet)], alphabet)
            else:
                regexp = first
                if start == 0:
                    regexp = Choice([regexp, Empty(alphabet)], alphabet)
            LOG.debug('DFS: cloned {0}'.format(regexp))
            return RegexpContainer(original, regexp, 
                                   _TAG_ADD_REQUIRED if stop is None else None)
        except Unsuitable:
            LOG.debug('DFS: not rewritten: {0!r}'.format(original))
            return original
        
    map = {Any: clone_any, 
           Or: clone_or, 
           And: clone_and,
           Transform: clone_transform,
           Literal: clone_literal,
           DepthFirst: clone_dfs}
    
    def clone(node, args, kargs):
        original_args = [RegexpContainer.to_matcher(arg) for arg in args]
        original_kargs = dict((name, RegexpContainer.to_matcher(kargs[name]))
                              for name in kargs)
        original = old_clone(node, original_args, original_kargs)
        type_ = type(node)
        if type_ in map:
            return map[type_](original, node, *args, **kargs)
        else:
            return original

    return clone


def regexp_rewriter(alphabet, matcher=NfaRegexp):
    '''
    Create a rewriter that uses the given alphabet and matcher.
    '''
    def rewriter(graph):
        new_clone = make_clone(alphabet, clone, matcher)
        graph = graph.postorder(DelayedClone(new_clone))
        if isinstance(graph, RegexpContainer):
            graph = graph.matcher
        return graph 
    return rewriter
