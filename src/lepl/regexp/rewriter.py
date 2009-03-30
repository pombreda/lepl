

from lepl.regexp.core import Character, Choice


class PossibleRegexp(object):
    '''
    A marker class that contains both a cloned "original" and a regexp
    based alternative.
    '''
    
    def __init__(self, original, regexp):
        self.original = original
        self.regexp = regexp
        
    @staticmethod
    def unpack(possible):
        if isinstance(possible, PossibleRegexp):
            return possible.regexp
        else:
            raise Unsuitable(possible)

        
class Unsuitable(Exception):
    pass
        
        
def make_clone(alphabet, old_clone):
    
    from lepl import Any, Or, And, Transformable
    
    def clone_any(restrict=None):
        if restrict is None:
            return Character([(alphabet.min, alphabet.max)], alphabet)
        else:
            return Character(((char, char) for char in restrict), alphabet)
        
    def clone_or(*matchers):
        return Choice(PossibleRegexp.unpack(matcher) for matcher in matchers)

    def clone_and(*matchers):
        return Sequence(PossibleRegexp.unpack(matcher) for matcher in matchers)
    
    # need to support repeat, literal, etc

    map = {Any: clone_any, Or: clone_or, And: clone_and}
    
    def build(regexp, function=None):
        # need dfa/nfa matcher that subclasses Transformable
        pass
    
    def clone(node, args, kargs):
        # need to build in args below
        usual = old_clone(node, args, kargs)
        try:
            copy = map[type(node)](*args, **kargs)
            if isinstance(node, Transformable) and node.function:
                return build(copy, function=node.function)
            else:
                return PossibleRegexp(usual, copy)
        except:
            return usual

    return clone
