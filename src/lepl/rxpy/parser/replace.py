#LICENCE

'''
Additional parser code for the expressions used in `re.sub` and similar
routines, where a "replacement" can be specified, containing group references
and escaped characters.
'''                                         

from string import digits

from lepl.rxpy.support import RxpyError
from lepl.rxpy.graph.container import Sequence
from lepl.rxpy.graph.opcode import GroupReference, Match, String
from lepl.rxpy.parser.support import parse, Builder, ALPHANUMERIC
from lepl.rxpy.parser.pattern import IntermediateEscapeBuilder


class ReplacementEscapeBuilder(IntermediateEscapeBuilder):
    '''
    Parse escaped characters in a "replacement".
    '''
    
    def append_character(self, character):
        if not character:
            raise RxpyError('Incomplete character escape')
        elif character == 'g':
            return ReplacementGroupReferenceBuilder(self._parser_state,
                                                    self._parent)
        else:
            return super(ReplacementEscapeBuilder, self).append_character(character)
        
    def _unexpected_character(self, character):
        '''
        Unexpected escapes are preserved during substitution.
        '''
        self._parent.append_character('\\', escaped=True)
        self._parent.append_character(character, escaped=True)
        return self._parent
        
        
class ReplacementGroupReferenceBuilder(Builder):
    '''
    Parse group references in a "replacement".
    '''
    
    def __init__(self, state, parent):
        super(ReplacementGroupReferenceBuilder, self).__init__(state)
        self.__parent = parent
        self.__buffer = ''
        
    def __decode(self):
        try:
            return GroupReference(
                    self._parser_state.index_for_name_or_count(self.__buffer[1:]))
        except RxpyError:
            raise IndexError('Bad group reference: ' + self.__buffer[1:])
        
    @property
    def __numeric(self):
        if not self.__buffer:
            return False
        elif not self.__buffer[1:]:
            return True
        else:
            try:
                int(self.__buffer[1:])
                return True
            except:
                return False
            
    @property
    def __name(self):
        if not self.__buffer:
            return False
        elif not self.__buffer[1:]:
            return True
        return not self.__buffer[1] in digits
             
    def append_character(self, character):
        # this is so complex because the tests for different errors are so
        # detailed
        if not self.__buffer and character == '<':
            self.__buffer += character
            return self
        elif len(self.__buffer) > 1 and character == '>':
            self.__parent._sequence.append(self.__decode())
            return self.__parent
        elif character and self.__numeric and character in digits:
            self.__buffer += character
            return self
        elif character and self.__name and character in ALPHANUMERIC:
            self.__buffer += character
            return self
        elif character:
            raise RxpyError('Unexpected character in group escape: ' + character)
        else:
            raise RxpyError('Incomplete group escape')
        

class ReplacementBuilder(Builder):
    '''
    Parse a "replacement" (eg for `re.sub`).  Normally this is called via
    `parse_replace`.
    '''
    
    def __init__(self, state):
        super(ReplacementBuilder, self).__init__(state)
        self._sequence = Sequence()
        
    def parse(self, text):
        builder = self
        for character in text:
            builder = builder.append_character(character)
        builder = builder.append_character(None)
        if self != builder:
            raise RxpyError('Incomplete expression')
        return self._sequence.join(Match(), self._parser_state)
    
    def append_character(self, character, escaped=False):
        if not escaped and character == '\\':
            return ReplacementEscapeBuilder(self._parser_state, self)
        elif character:
            self._sequence.append(
                String(self._parser_state.alphabet.join(
                            self._parser_state.alphabet.expression_to_letter(
                                character))))
        return self
    

def parse_replace(text, parser_state):
    '''
    Parse a "replacement" (eg for `re.sub`).

    Returns (parser_state, graph)
    '''
    return parse(text, parser_state, ReplacementBuilder, mutable_flags=False)

