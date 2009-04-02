
'''
What we want to do here is rewrite the tree of matchers from the bottom up
using regular expressions.  this is complicated by a number of things.

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
from traceback import format_exc

from lepl.matchers \
    import Any, Or, And, Add, add, Transformable, _NULL_TRANSFORM, Transform, \
    Transformation
from lepl.regexp.core import Choice, Sequence
from lepl.regexp.interval import Character
from lepl.regexp.matchers import NfaRegexp
from lepl.rewriters import copy_standard_attributes, clone, DelayedClone


class RegexpContainer(object):
    
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
    def build(node, regexp, alphabet):
        '''
        If the node is a Transformable with a Transformation then we must
        stop at this point.
        '''
        matcher = single(node, regexp, alphabet)
        print(matcher.describe)
        if isinstance(node, Transformable) \
                and node.function.describe is not _NULL_TRANSFORM:
            return matcher
        else:
            return RegexpContainer(matcher, regexp)
        

def single(node, regexp, alphabet):
    matcher = NfaRegexp(regexp, alphabet)
    copy_standard_attributes(node, matcher, describe=False)
    return matcher

        
class Unsuitable(Exception):
    pass

class Tagged(Unsuitable):
    pass


[_TAG_ADD_REQUIRED] = range(1)


def make_clone(alphabet, old_clone):
    
    # clone functions below take the "standard" clone and the node, and then
    # reproduce the normal argument list of the matcher being cloned.
    # they should return either a container or a matcher.
    
    def clone_any(orignal, node, restrict=None):
        '''
        We can always convert Any() to a regular expression; the only question
        is whether we have an open range or not.
        '''
        assert not isinstance(node, Transformable)
        if restrict is None:
            regexp = Character([(alphabet.min, alphabet.max)], alphabet)
        else:
            regexp = Character(((char, char) for char in restrict), alphabet)
        regexp = Sequence([regexp], alphabet)
        return RegexpContainer.build(node, regexp, alphabet)
        
    def clone_or(orignal, node, *matchers):
        '''
        We can convert an Or only if all the sub-matchers have possible
        regular expressions.
        '''
        try:
            regexp = Choice((RegexpContainer.to_regexp(matcher) 
                             for matcher in matchers), alphabet)
            print(regexp)
            return RegexpContainer.build(node, regexp, alphabet)
        except Unsuitable:
            return original

    def clone_and(original, node, *matchers):
        '''
        We can convert an And only if all the sub-matchers have possible
        regular expressions, and even then we must tag the result unless
        an add transform is present.
        '''
        try:
            regexp = Sequence((RegexpContainer.to_regexp(matcher) 
                               for matcher in matchers), alphabet)
            if node.function.describe is add:
                # we can abuse original here, since it is discarded
                original.function = Transformation()
                return RegexpContainer(single(original, regexp, alphabet), 
                                       regexp)
            elif node.function.describe is _NULL_TRANSFORM:
                return RegexpContainer(original, regexp, _TAG_ADD_REQUIRED)
            else:
                return original
        except Unsuitable:
            return original
    
    def clone_transform(original, node, matcher, function, raw=False, args=False):
        '''
        We can assume that function is a transformation.  The null 
        transformation has no effect on a regular expression; add joins into
        a sequence.
        '''
        assert isinstance(function, Transformation)
        try:
            print('**********', matcher)
            regexp = RegexpContainer.to_regexp(matcher, tag=_TAG_ADD_REQUIRED) 
            print('transform', regexp, function.describe)
            if function.describe is add:
                return single(node, regexp, alphabet)
            elif function.describe is _NULL_TRANSFORM:
                return RegexpContainer(original, regexp, _TAG_ADD_REQUIRED)
            else:
                return original
        except Unsuitable:
            return original
    
    # TODO - need to support repeat, literal, etc

    map = {Any: clone_any, 
           Or: clone_or, 
           And: clone_and,
           Transform: clone_transform}
    
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


def regexp_rewriter(alphabet):
    def rewriter(graph):
        new_clone = make_clone(alphabet, clone)
        graph = graph.postorder(DelayedClone(new_clone))
        if isinstance(graph, RegexpContainer):
            graph = graph.matcher
        return graph 
    return rewriter
