#LICENCE

'''
A replacement for Python's `re` package that uses the lexer engine.
'''

from lepl.rxpy.compat.module import Re
from lepl.rxpy.engine.lexer.engine import LexerEngine

_re = Re(LexerEngine, 'Lexer')

compile = _re.compile
RegexObject = _re.RegexObject
MatchIterator = _re.MatchIterator
match = _re.match    
search = _re.search
findall = _re.findall
finditer = _re.finditer    
sub = _re.sub    
subn = _re.subn    
split = _re.split    
error = _re.error
escape = _re.escape    
Scanner = _re.Scanner    

(I, M, S, U, X, A, _L, _C, _E, _U, _G, _B, IGNORECASE, MULTILINE, DOT_ALL, UNICODE, VERBOSE, ASCII, _LOOP_UNROLL, _CHARS, _EMPTY, _UNSAFE, _GROUPS, _LOOKBACK) = _re.FLAGS
