#LICENCE

'''
Unlike the other engines, this is for replacing text (eg `re.sub()`).

Like the other engines, it "runs" against a set of compiled functions
generated from a graph of nodes, which is generated from the text via a
parser.
'''

from lepl.rxpy.graph.base_compilable import BaseReplaceTarget, compile
from lepl.rxpy.parser.replace import parse_replace
from lepl.rxpy.support import RxpyError


class ReplaceEngine(BaseReplaceTarget):

    def __init__(self, replacement, parser_state):
        (self.__parser_state, graph) = parse_replace(replacement, parser_state)
        self.__program = compile(graph, self)

    def evaluate(self, match):
        self.__match = match
        self.__replacement = []
        state = 0
        self.__program[state]()
        return self.__parser_state.alphabet.join(*self.__replacement)

    def string(self, next, text):
        self.__replacement.append(text)
        return False # loop internally til done

    def group_reference(self, next, number):
        match = self.__match.group(number)
        if match:
            self.__replacement.append(match)
            return False # loop internally til done
        else:
            raise RxpyError('No match for group ' + str(number))

    def match(self):
        return True # exit loop


def compile_replacement(replacement, parser_state):
    '''
    Generate a function which, when applied to a match, generates new text based on
    the value of `replacement`.

    `replacement` may be a function or an expression.  If it a function we evaluate
    it and return the result.  Otherwise, we need to compile (cached in case the
    compiled result is called multiple times) and then evaluate it.
    '''
    cache = []
    def compiled(match):
        try:
            return replacement(match)
        except TypeError:
            if not cache:
                cache.append(ReplaceEngine(replacement, parser_state))
        return cache[0].evaluate(match)
    return compiled
