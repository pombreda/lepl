

from lepl import *
from string import ascii_uppercase, ascii_lowercase, ascii_letters


def line(matcher):
    return ~Space()[:] & matcher & ~Space()[:] & ~Literal('\n')


@trampoline_matcher_factory()
def make_pair(start, end, contents):
    def matcher(support, stream0):
        (match, stream1) = yield start._match(stream0)
        label = match[0]
        result = []
        while True:
            try:
                (match, stream2) = yield end._match(stream1)
                if match:
                    if match[0] == label:
                        yield ([(label, result)], stream2)
                        return
                    else:
                        support._debug('Bad end: %s' % match[0])
            except StopIteration:
                pass
            (match, stream2) = yield contents._match(stream1)
            result += match
            stream1 = stream2
    return matcher


def base():
    nested = Delayed()
    start = line(~Literal(':') & Word())
    end = line(~Literal(':e') & Word())
    contents = nested | line(Word()[:,~Space()[:]])
    nested += make_pair(start, end, contents)
    nested.config.no_memoize()
    return nested

def restricted():
    nested = Delayed()
    camel = Word(ascii_uppercase, ascii_lowercase)[1:, ...]
    start = line(~Literal(':') & camel)
    end = line(~Literal(':e') & camel)
    anything = AnyBut('\n')[:, ...] & ~Literal('\n')
    contents = nested | anything
    nested += make_pair(start, end, contents)
    nested.config.no_memoize()
    return nested


def restricted_with_tokens():

    tok_start = Token('[ \t]*:(?:[A-z][a-z]*)+[ \t]*\n')
    tok_end = Token('[ \t]*:e(?:[A-z][a-z]*)+[ \t]*\n')
    tok_line = Token('[^\n]*\n')

    start = tok_start(Regexp('\\s*:([A-z][a-z]*)+\\s*\n'))
    end = tok_end(Regexp('\\s*:e([A-z][a-z]*)+\\s*\n'))

    nested = Delayed()
    contents = nested | tok_line
    nested += make_pair(start, end, contents)
    nested.config.no_memoize()
    return nested
