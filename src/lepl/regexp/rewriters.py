
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

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

from logging import getLogger

from lepl.operators import Matcher
from lepl.regexp.core import Choice, Sequence, Repeat, Empty
from lepl.regexp.matchers import NfaRegexp
from lepl.regexp.interval import Character
from lepl.rewriters import copy_standard_attributes, clone, DelayedClone
from lepl.support import format, str


class RegexpContainer(object):
    '''
    The container referred to above, which carries a regular expression and
    an alternative matcher "up the tree" during rewriting.
    '''
    
    log = getLogger('lepl.regexp.rewriters.RegexpContainer')

    def __init__(self, matcher, regexp, use, add_reqd=False):
        self.matcher = matcher   # current best matcher (regexp or not)
        self.regexp = regexp     # the current regexp
        self.use = use           # is the regexp a win?
        self.add_reqd = add_reqd # we need "add" to combine values (from And)?
        
    def __str__(self):
        return ','.join([str(self.matcher.__class__), str(self.regexp), 
                         str(self.use), str(self.add_reqd)])

    @classmethod
    def to_regexps(cls, use, possibles, add_reqd=False):
        '''
        Convert to regular expressions.
        '''
        regexps = []
        for possible in possibles:
            if isinstance(possible, RegexpContainer):
                cls.log.debug(format('unpacking: {0!s}', possible))
                if add_reqd is None or possible.add_reqd == add_reqd:
                    regexps.append(possible.regexp)
                    # this flag indicates that it's "worth" using the regexp
                    # so we "inherit"
                    use = use or possible.use
                else:
                    raise Unsuitable('Add inconsistent.')
            else:
                cls.log.debug(format('cannot unpack: {0!s}', 
                                     possible.__class__))
                raise Unsuitable('Not a container.')
        return (use, regexps)
        
    @staticmethod
    def to_matcher(possible):
        '''
        Convert to a matcher.
        '''
        if isinstance(possible, RegexpContainer):
            return possible.matcher
        else:
            return possible
        
    @classmethod
    def build(cls, node, regexp, alphabet, matcher_type, use, 
               add_reqd=False, transform=True):
        '''
        Construct a container or matcher.
        '''
        if use and not add_reqd:
            matcher = single(alphabet, node, regexp, matcher_type, transform)
            # if matcher is a Transformable with a Transformation other than
            # the standard empty_adapter then we must stop
            if len(matcher.function.functions) > 1:
                cls.log.debug(format('Force matcher: {0}', matcher.function))
                return matcher
        else:
            matcher = node
        return RegexpContainer(matcher, regexp, use, add_reqd)
        

def single(alphabet, node, regexp, matcher_type, transform=True):
    '''
    Create a matcher for the given regular expression.
    '''
    # avoid dependency loops
    from lepl.matchers import Transformation
    matcher = matcher_type(regexp, alphabet)
    copy_standard_attributes(node, matcher, describe=False, transform=transform)
    return matcher.precompose_transformation(Transformation(empty_adapter))


def empty_adapter(results, _sin, sout):
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


def make_clone(alphabet, old_clone, matcher_type, use_from_start):
    '''
    Factory that generates a clone suitable for rewriting recursive descent
    to regular expressions.
    '''
    
    # clone functions below take the "standard" clone and the node, and then
    # reproduce the normal argument list of the matcher being cloned.
    # they should return either a container or a matcher.
    
    # Avoid dependency loops
    from lepl.functions import add
    from lepl.matchers import Any, Or, And, Transformable, \
        Transform, Transformation, Literal, DepthFirst

    log = getLogger('lepl.regexp.rewriters.make_clone')
    
    def clone_any(use, original, restrict=None):
        '''
        We can always convert Any() to a regular expression; the only question
        is whether we have an open range or not.
        '''
        assert not isinstance(original, Transformable)
        if restrict is None:
            char = Character([(alphabet.min, alphabet.max)], alphabet)
        else:
            char = Character(((char, char) for char in restrict), alphabet)
        log.debug(format('Any: cloned {0}', char))
        regexp = Sequence([char], alphabet)
        return RegexpContainer.build(original, regexp, alphabet, 
                                     matcher_type, use)
        
    def clone_or(use, original, *matchers):
        '''
        We can convert an Or only if all the sub-matchers have possible
        regular expressions.
        '''
        assert isinstance(original, Transformable)
        try:
            (use, regexps) = RegexpContainer.to_regexps(use, matchers)
            regexp = Choice(regexps, alphabet)
            log.debug(format('Or: cloned {0}', regexp))
            return RegexpContainer.build(original, regexp, alphabet, 
                                         matcher_type, use)
        except Unsuitable:
            log.debug(format('Or not rewritten: {0!r}', original))
            return original

    def clone_and(use, original, *matchers):
        '''
        We can convert an And only if all the sub-matchers have possible
        regular expressions, and even then we must tag the result unless
        an add transform is present.
        '''
        assert isinstance(original, Transformable)
        try:
            # since we're going to require add anyway, we're happy to take
            # other inputs, whether add is required or not.
            (use, regexps) = \
                RegexpContainer.to_regexps(use, matchers, add_reqd=None)
            # if we have regexp sub-expressions, join them
            regexp = Sequence(regexps, alphabet)
            log.debug(format('And: cloning {0}', regexp))
            if use and len(original.function.functions) > 1 \
                    and original.function.functions[0] is add:
                # we have additional functions, so cannot take regexp higher,
                # but use is True, so return a new matcher.
                # hack to copy across other functions
                original.function = \
                        Transformation(original.function.functions[1:])
                log.debug('And: OK (final)')
                # NEED TEST FOR THIS
                return single(alphabet, original, regexp, matcher_type) 
            elif len(original.function.functions) == 1 \
                    and original.function.functions[0] is add:
                # OR JUST ONE?
                # lucky!  we just combine and continue
                log.debug('And: OK')
                return RegexpContainer.build(original, regexp, alphabet, 
                                             matcher_type, use, transform=False)
            elif not original.function:
                # regexp can't return multiple values, so hope that we have
                # an add
                log.debug('And: add required')
                return RegexpContainer.build(original, regexp, alphabet, 
                                             matcher_type, use, add_reqd=True)
            else:
                log.debug(format('And: wrong transformation: {0!r}',
                                 original.function))
                return original
        except Unsuitable:
            log.debug(format('And: not rewritten: {0!r}', original))
            return original
    
    def clone_transform(use, original, matcher, function, 
                          _raw=False, _args=False):
        '''
        We can assume that function is a transformation.  add joins into
        a sequence.
        '''
        assert isinstance(function, Transformation)
        try:
            # this is the only place add is required
            (use, [regexp]) = RegexpContainer.to_regexps(use, [matcher], 
                                                         add_reqd=True)
            log.debug(format('Transform: cloning {0}', regexp))
            if use and len(function.functions) > 1 \
                    and function.functions[0] is add:
                # we have additional functions, so cannot take regexp higher,
                # but use is True, so return a new matcher.
                # hack to copy across other functions
                original.function = Transformation(function.functions[1:])
                log.debug('Transform: OK (final)')
                # NEED TEST FOR THIS
                return single(alphabet, original, regexp, matcher_type) 
            elif len(function.functions) == 1 and function.functions[0] is add:
                # exactly what we wanted!  combine and continue
                log.debug('Transform: OK')
                return RegexpContainer.build(original, regexp, alphabet, 
                                             matcher_type, use, transform=False)
            elif not function:
                # we're just forwarding the add_reqd from before here
                log.debug('Transform: empty, add required')
                return RegexpContainer(original, regexp, use, add_reqd=True)
            else:
                log.debug(format('Transform: wrong transformation: {0!r}',
                                 original.function))
                return original
        except Unsuitable:
            log.debug(format('Transform: not rewritten: {0!r}', original))
            return original
        
    def clone_literal(use, original, text):
        '''
        Literal is transformable, so we need to be careful with any associated
        Transformation.
        '''
        assert isinstance(original, Transformable)
        chars = [Character([(c, c)], alphabet) for c in text]
        regexp = Sequence(chars, alphabet)
        log.debug(format('Literal: cloned {0}', regexp))
        return RegexpContainer.build(original, regexp, alphabet, 
                                     matcher_type, use)
    
    def clone_dfs(use, original, first, start, stop, rest=None):
        '''
        We only convert DFS if start=0 or 1, stop=1 or None and first and 
        rest are both regexps.
        
        This forces use=True as it is likely that a regexp is a gain.
        '''
        assert not isinstance(original, Transformable)
        try:
            if start not in (0, 1) or stop not in (1, None):
                raise Unsuitable()
            (use, [first, rest]) = \
                    RegexpContainer.to_regexps(True, [first, rest])
            # we need to be careful here to get the depth first bit right
            if stop is None:
                regexp = Sequence([first, Repeat([rest], alphabet)], alphabet)
                if start == 0:
                    regexp = Choice([regexp, Empty(alphabet)], alphabet)
            else:
                regexp = first
                if start == 0:
                    regexp = Choice([regexp, Empty(alphabet)], alphabet)
            log.debug(format('DFS: cloned {0}', regexp))
            return RegexpContainer.build(original, regexp, alphabet, 
                                         matcher_type, use, 
                                         add_reqd=stop is None)
        except Unsuitable:
            log.debug(format('DFS: not rewritten: {0!r}', original))
            return original
        
    map_ = {Any: clone_any, 
            Or: clone_or, 
            And: clone_and,
            Transform: clone_transform,
            Literal: clone_literal,
            DepthFirst: clone_dfs}
    
    def clone_(node, args, kargs):
        '''
        Do the cloning, dispatching by type to the methods above.
        '''
        original_args = [RegexpContainer.to_matcher(arg) for arg in args]
        original_kargs = dict((name, RegexpContainer.to_matcher(kargs[name]))
                              for name in kargs)
        original = old_clone(node, original_args, original_kargs)
        type_ = type(node)
        if type_ in map_:
            # pylint: disable-msg=W0142
            return map_[type_](use_from_start, original, *args, **kargs)
        else:
            return original

    return clone_


def regexp_rewriter(alphabet, use=True, matcher=NfaRegexp):
    '''
    Create a rewriter that uses the given alphabet and matcher.
    
    The "use" parameter controls when regular expressions are substituted.
    If true, they are always used.  If false, they are used only if they
    are part of a tree that includes repetition.  The latter case generally
    gives more efficient parsers because it avoids converting already
    efficient literal matchers to regular expressions.
    '''
    def rewriter(graph):
        '''
        The rewriter, using the given alphabet.
        '''
        new_clone = make_clone(alphabet, clone, matcher, use)
        graph = graph.postorder(DelayedClone(new_clone), Matcher)
        if isinstance(graph, RegexpContainer):
            graph = graph.matcher
        return graph 
    return rewriter
