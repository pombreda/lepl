#LICENCE

from lepl.rxpy.compat.support import compile as compile_, \
    RegexObject as RegexObject_, MatchIterator as MatchIterator_, \
    match as match_, search as search_, findall as findall_, \
    finditer as finditer_, sub as sub_, subn as subn_, \
    split as split_, error as error_, escape as escape_, Scanner as Scanner_
from lepl.rxpy.support import _FLAGS
from lepl.stream.factory import DEFAULT_STREAM_FACTORY


class Re(object):
    
    def __init__(self, engine, name):
        self.__engine = engine
        self.__name = name
        self.error = error_
        self.escape = escape_
        self.FLAGS = _FLAGS
        (self.I, self.M, self.S, self.U, self.X, self.A, 
         self._L, self._C, self._E, self._U, self._G, self._B,
         self.IGNORECASE, self.MULTILINE, self.DOT_ALL, self.UNICODE,
         self.VERBOSE, self.ASCII, 
         self._LOOP_UNROLL, self._CHARS, self._EMPTY, self._UNSAFE, 
         self._GROUPS, self._LOOKBACK) = _FLAGS

    def __str__(self):
        return self.__name

    def _engine(self, engine):
        if engine:
            return engine
        else:
            return self.__engine
        
    def compile(self, pattern, flags=None, alphabet=None, engine=None,
                factory=DEFAULT_STREAM_FACTORY.from_string):
        return compile_(pattern, flags=flags, alphabet=alphabet,
                        engine=self._engine(engine), factory=factory)

    @property
    def RegexObject(self):
        class RegexObject(RegexObject_):
            #noinspection PyMethodParameters
            def __init__(inner, parsed, pattern=None, engine=None,
                factory=DEFAULT_STREAM_FACTORY.from_string):
                super(RegexObject_, inner).__init__(
                                    parsed, pattern=pattern,
                                    engine=self._engine(engine), factory=factory)
        return RegexObject

    @property
    def MatchIterator(self):
        class MatchIterator(MatchIterator_):
            #noinspection PyMethodParameters
            def __init__(inner, re, parsed, text, pattern, pos=0, endpos=None,
                         engine=None, factory=DEFAULT_STREAM_FACTORY.from_string):
                super(MatchIterator_, inner).__init__(
                                    re, parsed, text, pattern,
                                    pos=pos, endpos=endpos,
                                    engine=self._engine(engine),
                                    factory=factory)
        return MatchIterator

    def match(self, pattern, text, flags=0, alphabet=None, engine=None,
                factory=DEFAULT_STREAM_FACTORY.from_string):
        return match_(pattern, text, flags=flags, alphabet=alphabet,
                      engine=self._engine(engine), factory=factory)
        
    def search(self, pattern, text, flags=0, alphabet=None, engine=None,
                factory=DEFAULT_STREAM_FACTORY.from_string):
        return search_(pattern, text, flags=flags, alphabet=alphabet,
                      engine=self._engine(engine), factory=factory)

    def findall(self, pattern, text, flags=0, alphabet=None, engine=None,
                factory=DEFAULT_STREAM_FACTORY.from_string):
        return findall_(pattern, text, flags=flags, alphabet=alphabet,
                        engine=self._engine(engine), factory=factory)

    def finditer(self, pattern, text, flags=0, alphabet=None, engine=None,
                factory=DEFAULT_STREAM_FACTORY.from_string):
        return finditer_(pattern, text, flags=flags, alphabet=alphabet,
                         engine=self._engine(engine), factory=factory)
        
    def sub(self, pattern, repl, text, count=0, flags=0, alphabet=None, 
            engine=None, factory=DEFAULT_STREAM_FACTORY.from_string):
        return sub_(pattern, repl, text, count=count, flags=flags, 
                    alphabet=alphabet, engine=self._engine(engine),
                    factory=factory)

    def subn(self, pattern, repl, text, count=0, flags=0, alphabet=None, 
             engine=None, factory=DEFAULT_STREAM_FACTORY.from_string):
        return subn_(pattern, repl, text, count=count, flags=flags, 
                     alphabet=alphabet, engine=self._engine(engine),
                     factory=factory)

    def split(self, pattern, text, maxsplit=0, flags=0, alphabet=None, 
              engine=None, factory=DEFAULT_STREAM_FACTORY.from_string):
        return split_(pattern, text, maxsplit=maxsplit, flags=flags, 
                      alphabet=alphabet, engine=self._engine(engine),
                      factory=factory)

    @property
    def Scanner(self):
        class Scanner(Scanner_):
            #noinspection PyMethodParameters
            def __init__(inner, pairs, flags=0, alphabet=None, engine=None,
                factory=DEFAULT_STREAM_FACTORY.from_string):
                super(Scanner, inner).__init__(
                                    pairs, flags=flags, alphabet=alphabet,
                                    engine=self._engine(engine),
                                    factory=factory)
        return Scanner

    