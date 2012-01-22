
#LICENCE

from lepl.lexer.operators import TOKENS, TokenNamespace
from lepl.matchers.support import BaseMatcher
from lepl.support.context import NamespaceMixin
from lepl.support.lib import fmt


class Lexer(NamespaceMixin, BaseMatcher):
    '''
    This takes a set of regular expressions and provides a matcher that
    converts a stream into a stream of tokens, passing the new stream to
    the embedded matcher.

    It is added to the matcher graph by the lexer_rewriter; it is not
    specified explicitly by the user.
    '''

    def __init__(self, matcher, tokens, alphabet, discard,
                 t_regexp=None, s_regexp=None):
        '''
        matcher is the head of the original matcher graph, which will be called
        with a tokenised stream.

        tokens is the set of `Token` instances that define the lexer.

        alphabet is the alphabet for which the regexps are defined.

        discard is the regular expression for spaces (which are silently
        dropped if not token can be matcher).

        t_regexp and s_regexp are internally compiled state, used in cloning,
        and should not be provided by non-cloning callers.
        '''
        super(Lexer, self).__init__(TOKENS, TokenNamespace)
        if t_regexp is None:
            unique = {}
            for token in tokens:
                token.compile(alphabet)
                self._debug(fmt('Token: {0}', token))
                # this just reduces the work for the regexp compiler
                unique[token.id_] = token
            t_regexp = Compiler.multiple(alphabet,
                [(t.id_, t.regexp)
                for t in unique.values() if t.regexp is not None]).dfa()
        if s_regexp is None and discard is not None:
            s_regexp = Compiler.single(alphabet, discard).dfa()
        self._arg(matcher=matcher)
        self._arg(tokens=tokens)
        self._arg(alphabet=alphabet)
        self._arg(discard=discard)
        self._karg(t_regexp=t_regexp)
        self._karg(s_regexp=s_regexp)

    def token_for_id(self, id_):
        '''
        A utility that checks the known tokens for a given ID.  The ID is used
        internally, but is (by default) an unfriendly integer value.  Note that
        a lexed stream associates a chunk of input with a list of IDs - more
        than one regexp may be a maximal match (and this is a feature, not a
        bug).
        '''
        for token in self.tokens:
            if token.id_ == id_:
                return token

    def _tokens(self, stream, max):
        '''
        Generate tokens, on demand.
        '''
        try:
            id_ = s_id(stream)
            while not s_empty(stream):
                # avoid conflicts between tokens
                id_ += 1
                try:
                    (terminals, match, next_stream) =\
                    self.t_regexp.match(stream)
                    self._debug(fmt('Token: {0!r} {1!r} {2!s}',
                        terminals, match, s_debug(stream)))
                    yield (terminals, s_stream(stream, match, max=max, id_=id_))
                except TypeError:
                    (terminals, _size, next_stream) =\
                    self.s_regexp.size_match(stream)
                    self._debug(fmt('Space: {0!r} {1!s}',
                        terminals, s_debug(stream)))
                stream = next_stream
        except TypeError:
            raise RuntimeLexerError(
                s_fmt(stream,
                    'No token for {rest} at {location} of {text}.'))

    @tagged
    def _match(self, in_stream):
        '''
        Implement matching - pass token stream to tokens.
        '''
        (max, clean_stream) = s_new_max(in_stream)
        try:
            length = s_len(in_stream)
        except TypeError:
            length = None
        factory = s_factory(in_stream)
        token_stream = factory.to_token(
            self._tokens(clean_stream, max),
            id=s_id(in_stream), factory=factory,
            max=s_max(in_stream),
            global_kargs=s_global_kargs(in_stream),
            delta=s_delta(in_stream), len=length,
            cache_level=s_cache_level(in_stream)+1)
        in_stream = None
        generator = self.matcher._match(token_stream)
        while True:
            yield (yield generator)
