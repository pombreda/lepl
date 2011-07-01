#LICENCE

'''
A replacement for Python's `re` package that uses the complex engine.
'''

from lepl.rxpy.compat.module import Re
from lepl.rxpy.engine.complex.engine import ComplexEngine

_re = Re(ComplexEngine, 'Complex')

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

(I, M, S, U, X, A, _L, _C, _E, _U, _G, IGNORECASE, MULTILINE, DOT_ALL, UNICODE, VERBOSE, ASCII, _LOOP_UNROLL, _CHARS, _EMPTY, _UNSAFE, _GROUPS) = _re.FLAGS
