
# THIS FILE FROM PYTHON SOURCE - SEPARATE LICENCE

from __future__ import print_function
import sys, traceback
from weakref import proxy

from lepl.rxpy.engine._test.base import BaseTest
from lepl.support.lib import PYTHON3, chr, bytes

if PYTHON3:
    u = str
else:
    u = lambda x: unicode(x, encoding='unicode-escape')

# Misc tests from Tim Peters' self._re.doc

# WARNING: Don't change details in these tests if you don't know
# what you're doing. Some of these tests were carefully modeled to
# cover most of the code.


#noinspection PyUnresolvedReferences
class ReTests(BaseTest):

    def test_weakref(self):
        s = 'QabbbcR'
        x = self._re.compile('ab+c')
        y = proxy(x)
        self.assertEqual(x.findall('QabbbcR'), y.findall('QabbbcR'))

    def test_search_star_plus(self):
        self.assertEqual(self._re.search('x*', 'axx').span(0), (0, 0))
        self.assertEqual(self._re.search('x*', 'axx').span(), (0, 0))
        self.assertEqual(self._re.search('x+', 'axx').span(0), (1, 3))
        self.assertEqual(self._re.search('x+', 'axx').span(), (1, 3))
        self.assertEqual(self._re.search('x', 'aaa'), None)
        self.assertEqual(self._re.match('a*', 'xxx').span(0), (0, 0))
        self.assertEqual(self._re.match('a*', 'xxx').span(), (0, 0))
        self.assertEqual(self._re.match('x*', 'xxxa').span(0), (0, 3))
        self.assertEqual(self._re.match('x*', 'xxxa').span(), (0, 3))
        self.assertEqual(self._re.match('a+', 'xxx'), None)

    def bump_num(self, matchobj):
        int_value = int(matchobj.group(0))
        return str(int_value + 1)

    def test_basic_re_sub(self):
        self.assertEqual(self._re.sub("(?i)b+", "x", "bbbb BBBB"), 'x x')
        self.assertEqual(self._re.sub(r'\d+', self.bump_num, '08.2 -2 23x99y'),
                         '9.3 -3 24x100y')
        self.assertEqual(self._re.sub(r'\d+', self.bump_num, '08.2 -2 23x99y', 3),
                         '9.3 -3 23x99y')

        self.assertEqual(self._re.sub('.', lambda m: r"\n", 'x'), '\\n')
        self.assertEqual(self._re.sub('.', r"\n", 'x'), '\n')

        s = r"\1\1"
        self.assertEqual(self._re.sub('(.)', s, 'x'), 'xx')
        self.assertEqual(self._re.sub('(.)', self._re.escape(s), 'x'), s)
        self.assertEqual(self._re.sub('(.)', lambda m: s, 'x'), s)

        self.assertEqual(self._re.sub('(?P<a>x)', '\g<a>\g<a>', 'xx'), 'xxxx')
        self.assertEqual(self._re.sub('(?P<a>x)', '\g<a>\g<1>', 'xx'), 'xxxx')
        self.assertEqual(self._re.sub('(?P<unk>x)', '\g<unk>\g<unk>', 'xx'), 'xxxx')
        self.assertEqual(self._re.sub('(?P<unk>x)', '\g<1>\g<1>', 'xx'), 'xxxx')

        self.assertEqual(self._re.sub('a',r'\t\n\v\r\f\a\b\B\Z\a\A\w\W\s\S\d\D','a'),
                         '\t\n\v\r\f\a\b\\B\\Z\a\\A\\w\\W\\s\\S\\d\\D')
        self.assertEqual(self._re.sub('a', '\t\n\v\r\f\a', 'a'), '\t\n\v\r\f\a')
        self.assertEqual(self._re.sub('a', '\t\n\v\r\f\a', 'a'),
                         (chr(9)+chr(10)+chr(11)+chr(13)+chr(12)+chr(7)))

        self.assertEqual(self._re.sub('^\s*', 'X', 'test'), 'Xtest')

    def test_bug_449964(self):
        # fails for group followed by other escape
        self.assertEqual(self._re.sub(r'(?P<unk>x)', '\g<1>\g<1>\\b', 'xx'),
                         'xx\bxx\b')

    def test_bug_449000(self):
        # Test for sub() on escaped characters
        self.assertEqual(self._re.sub(r'\r\n', r'\n', 'abc\r\ndef\r\n'),
                         'abc\ndef\n')
        self.assertEqual(self._re.sub('\r\n', r'\n', 'abc\r\ndef\r\n'),
                         'abc\ndef\n')
        self.assertEqual(self._re.sub(r'\r\n', '\n', 'abc\r\ndef\r\n'),
                         'abc\ndef\n')
        self.assertEqual(self._re.sub('\r\n', '\n', 'abc\r\ndef\r\n'),
                         'abc\ndef\n')

    def test_bug_1661(self):
        # Verify that flags do not get silently ignored with compiled patterns
        pattern = self._re.compile('.')
        self.assertRaises(ValueError, self._re.match, pattern, 'A', self._re.I)
        self.assertRaises(ValueError, self._re.search, pattern, 'A', self._re.I)
        self.assertRaises(ValueError, self._re.findall, pattern, 'A', self._re.I)
        self.assertRaises(ValueError, self._re.compile, pattern, self._re.I)

    def test_bug_3629(self):
        # A regex that triggered a bug in the sre-code validator
        self._re.compile("(?P<quote>)(?(quote))")

    def test_sub_template_numeric_escape(self):
        # bug 776311 and friends
        self.assertEqual(self._re.sub('x', r'\0', 'x'), '\0')
        self.assertEqual(self._re.sub('x', r'\000', 'x'), '\000')
        self.assertEqual(self._re.sub('x', r'\001', 'x'), '\001')
        self.assertEqual(self._re.sub('x', r'\008', 'x'), '\0' + '8')
        self.assertEqual(self._re.sub('x', r'\009', 'x'), '\0' + '9')
        self.assertEqual(self._re.sub('x', r'\111', 'x'), '\111')
        self.assertEqual(self._re.sub('x', r'\117', 'x'), '\117')

        self.assertEqual(self._re.sub('x', r'\1111', 'x'), '\1111')
        self.assertEqual(self._re.sub('x', r'\1111', 'x'), '\111' + '1')

        self.assertEqual(self._re.sub('x', r'\00', 'x'), '\x00')
        self.assertEqual(self._re.sub('x', r'\07', 'x'), '\x07')
        self.assertEqual(self._re.sub('x', r'\08', 'x'), '\0' + '8')
        self.assertEqual(self._re.sub('x', r'\09', 'x'), '\0' + '9')
        self.assertEqual(self._re.sub('x', r'\0a', 'x'), '\0' + 'a')

        self.assertEqual(self._re.sub('x', r'\400', 'x'), '\0')
        self.assertEqual(self._re.sub('x', r'\777', 'x'), '\377')

        self.assertRaises(self._re.error, self._re.sub, 'x', r'\1', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\8', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\9', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\11', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\18', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\1a', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\90', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\99', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\118', 'x') # r'\11' + '8'
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\11a', 'x')
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\181', 'x') # r'\18' + '1'
        self.assertRaises(self._re.error, self._re.sub, 'x', r'\800', 'x') # r'\80' + '0'

        # in python2.3 (etc), these loop endlessly in sre_parser.py
        self.assertEqual(self._re.sub('(((((((((((x)))))))))))', r'\11', 'x'), 'x')
        self.assertEqual(self._re.sub('((((((((((y))))))))))(.)', r'\118', 'xyz'),
                         'xz8')
        self.assertEqual(self._re.sub('((((((((((y))))))))))(.)', r'\11a', 'xyz'),
                         'xza')

    def test_qualified_re_sub(self):
        self.assertEqual(self._re.sub('a', 'b', 'aaaaa'), 'bbbbb')
        self.assertEqual(self._re.sub('a', 'b', 'aaaaa', 1), 'baaaa')

    def test_bug_114660(self):
        self.assertEqual(self._re.sub(r'(\S)\s+(\S)', r'\1 \2', 'hello  there'),
                         'hello there')

    def test_bug_462270(self):
        # Test for empty sub() behaviour, see SF bug #462270
        self.assertEqual(self._re.sub('x*', '-', 'abxd'), '-a-b-d-')
        self.assertEqual(self._re.sub('x+', '-', 'abxd'), 'ab-d')

    def test_symbolic_refs(self):
        self.assertRaises(self._re.error, self._re.sub, '(?P<a>x)', '\g<a', 'xx')
        self.assertRaises(self._re.error, self._re.sub, '(?P<a>x)', '\g<', 'xx')
        self.assertRaises(self._re.error, self._re.sub, '(?P<a>x)', '\g', 'xx')
        self.assertRaises(self._re.error, self._re.sub, '(?P<a>x)', '\g<a a>', 'xx')
        self.assertRaises(self._re.error, self._re.sub, '(?P<a>x)', '\g<1a1>', 'xx')
        self.assertRaises(IndexError, self._re.sub, '(?P<a>x)', '\g<ab>', 'xx')
        self.assertRaises(self._re.error, self._re.sub, '(?P<a>x)|(?P<b>y)', '\g<b>', 'xx')
        self.assertRaises(self._re.error, self._re.sub, '(?P<a>x)|(?P<b>y)', '\\2', 'xx')
        self.assertRaises(self._re.error, self._re.sub, '(?P<a>x)', '\g<-1>', 'xx')

    def test_re_subn(self):
        self.assertEqual(self._re.subn("(?i)b+", "x", "bbbb BBBB"), ('x x', 2))
        self.assertEqual(self._re.subn("b+", "x", "bbbb BBBB"), ('x BBBB', 1))
        self.assertEqual(self._re.subn("b+", "x", "xyz"), ('xyz', 0))
        self.assertEqual(self._re.subn("b*", "x", "xyz"), ('xxxyxzx', 4))
        self.assertEqual(self._re.subn("b*", "x", "xyz", 2), ('xxxyz', 2))

    def test_re_split(self):
        self.assertEqual(self._re.split(":", ":a:b::c"), ['', 'a', 'b', '', 'c'])
        self.assertEqual(self._re.split(":*", ":a:b::c"), ['', 'a', 'b', 'c'])
        self.assertEqual(self._re.split("(:*)", ":a:b::c"),
                         ['', ':', 'a', ':', 'b', '::', 'c'])
        self.assertEqual(self._re.split("(?::*)", ":a:b::c"), ['', 'a', 'b', 'c'])
        self.assertEqual(self._re.split("(:)*", ":a:b::c"),
                         ['', ':', 'a', ':', 'b', ':', 'c'])
        self.assertEqual(self._re.split("([b:]+)", ":a:b::c"),
                         ['', ':', 'a', ':b::', 'c'])
        self.assertEqual(self._re.split("(b)|(:+)", ":a:b::c"),
                         ['', None, ':', 'a', None, ':', '', 'b', None, '',
                          None, '::', 'c'])
        self.assertEqual(self._re.split("(?:b)|(?::+)", ":a:b::c"),
                         ['', 'a', '', '', 'c'])

    def test_qualified_re_split(self):
        self.assertEqual(self._re.split(":", ":a:b::c", 2), ['', 'a', 'b::c'])
        self.assertEqual(self._re.split(':', 'a:b:c:d', 2), ['a', 'b', 'c:d'])
        self.assertEqual(self._re.split("(:)", ":a:b::c", 2),
                         ['', ':', 'a', ':', 'b::c'])
        self.assertEqual(self._re.split("(:*)", ":a:b::c", 2),
                         ['', ':', 'a', ':', 'b::c'])

    def test_re_findall(self):
        self.assertEqual(self._re.findall(":+", "abc"), [])
        self.assertEqual(self._re.findall(":+", "a:b::c:::d"), [":", "::", ":::"])
        self.assertEqual(self._re.findall("(:+)", "a:b::c:::d"), [":", "::", ":::"])
        self.assertEqual(self._re.findall("(:)(:*)", "a:b::c:::d"), [(":", ""),
                                                               (":", ":"),
                                                               (":", "::")])

    def test_bug_117612(self):
        self.assertEqual(self._re.findall(r"(a|(b))", "aba"),
                         [("a", ""),("b", "b"),("a", "")])

    def test_re_match(self):
        self.assertEqual(self._re.match('a', 'a').groups(), ())
        self.assertEqual(self._re.match('(a)', 'a').groups(), ('a',))
        self.assertEqual(self._re.match(r'(a)', 'a').group(0), 'a')
        self.assertEqual(self._re.match(r'(a)', 'a').group(1), 'a')
        self.assertEqual(self._re.match(r'(a)', 'a').group(1, 1), ('a', 'a'))

        pat = self._re.compile('((a)|(b))(c)?')
        self.assertEqual(pat.match('a').groups(), ('a', 'a', None, None))
        self.assertEqual(pat.match('b').groups(), ('b', None, 'b', None))
        self.assertEqual(pat.match('ac').groups(), ('a', 'a', None, 'c'))
        self.assertEqual(pat.match('bc').groups(), ('b', None, 'b', 'c'))
        self.assertEqual(pat.match('bc').groups(""), ('b', "", 'b', 'c'))

        # A single group
        m = self._re.match('(a)', 'a')
        self.assertEqual(m.group(0), 'a')
        self.assertEqual(m.group(0), 'a')
        self.assertEqual(m.group(1), 'a')
        self.assertEqual(m.group(1, 1), ('a', 'a'))

        pat = self._re.compile('(?:(?P<a1>a)|(?P<b2>b))(?P<c3>c)?')
        self.assertEqual(pat.match('a').group(1, 2, 3), ('a', None, None))
        self.assertEqual(pat.match('b').group('a1', 'b2', 'c3'),
                         (None, 'b', None))
        self.assertEqual(pat.match('ac').group(1, 'b2', 3), ('a', None, 'c'))

    def test_re_groupref_exists(self):
        self.assertEqual(self._re.match('^(\()?([^()]+)(?(1)\))$', '(a)').groups(),
                         ('(', 'a'))
        self.assertEqual(self._re.match('^(\()?([^()]+)(?(1)\))$', 'a').groups(),
                         (None, 'a'))
        self.assertEqual(self._re.match('^(\()?([^()]+)(?(1)\))$', 'a)'), None)
        self.assertEqual(self._re.match('^(\()?([^()]+)(?(1)\))$', '(a'), None)
        self.assertEqual(self._re.match('^(?:(a)|c)((?(1)b|d))$', 'ab').groups(),
                         ('a', 'b'))
        self.assertEqual(self._re.match('^(?:(a)|c)((?(1)b|d))$', 'cd').groups(),
                         (None, 'd'))
        self.assertEqual(self._re.match('^(?:(a)|c)((?(1)|d))$', 'cd').groups(),
                         (None, 'd'))
        self.assertEqual(self._re.match('^(?:(a)|c)((?(1)|d))$', 'a').groups(),
                         ('a', ''))

        # Tests for bug #1177831: exercise groups other than the first group
        p = self._re.compile('(?P<g1>a)(?P<g2>b)?((?(g2)c|d))')
        self.assertEqual(p.match('abc').groups(),
                         ('a', 'b', 'c'))
        self.assertEqual(p.match('ad').groups(),
                         ('a', None, 'd'))
        self.assertEqual(p.match('abd'), None)
        self.assertEqual(p.match('ac'), None)

    def test_re_groupref(self):
        self.assertEqual(self._re.match(r'^(\|)?([^()]+)\1$', '|a|').groups(),
                         ('|', 'a'))
        self.assertEqual(self._re.match(r'^(\|)?([^()]+)\1?$', 'a').groups(),
                         (None, 'a'))
        self.assertEqual(self._re.match(r'^(\|)?([^()]+)\1$', 'a|'), None)
        self.assertEqual(self._re.match(r'^(\|)?([^()]+)\1$', '|a'), None)
        self.assertEqual(self._re.match(r'^(?:(a)|c)(\1)$', 'aa').groups(),
                         ('a', 'a'))
        self.assertEqual(self._re.match(r'^(?:(a)|c)(\1)?$', 'c').groups(),
                         (None, None))

    def test_groupdict(self):
        self.assertEqual(self._re.match('(?P<first>first) (?P<second>second)',
                                  'first second').groupdict(),
                         {'first':'first', 'second':'second'})

    def test_expand(self):
        self.assertEqual(self._re.match("(?P<first>first) (?P<second>second)",
                                  "first second")
                                  .expand(r"\2 \1 \g<second> \g<first>"),
                         "second first second first")

    def test_repeat_minmax(self):
        self.assertEqual(self._re.match("^(\w){1}$", "abc"), None)
        self.assertEqual(self._re.match("^(\w){1}?$", "abc"), None)
        self.assertEqual(self._re.match("^(\w){1,2}$", "abc"), None)
        self.assertEqual(self._re.match("^(\w){1,2}?$", "abc"), None)

        self.assertEqual(self._re.match("^(\w){3}$", "abc").group(1), "c")
        self.assertEqual(self._re.match("^(\w){1,3}$", "abc").group(1), "c")
        self.assertEqual(self._re.match("^(\w){1,4}$", "abc").group(1), "c")
        self.assertEqual(self._re.match("^(\w){3,4}?$", "abc").group(1), "c")
        self.assertEqual(self._re.match("^(\w){3}?$", "abc").group(1), "c")
        self.assertEqual(self._re.match("^(\w){1,3}?$", "abc").group(1), "c")
        self.assertEqual(self._re.match("^(\w){1,4}?$", "abc").group(1), "c")
        self.assertEqual(self._re.match("^(\w){3,4}?$", "abc").group(1), "c")

        self.assertEqual(self._re.match("^x{1}$", "xxx"), None)
        self.assertEqual(self._re.match("^x{1}?$", "xxx"), None)
        self.assertEqual(self._re.match("^x{1,2}$", "xxx"), None)
        self.assertEqual(self._re.match("^x{1,2}?$", "xxx"), None)

        self.assertNotEqual(self._re.match("^x{3}$", "xxx"), None)
        self.assertNotEqual(self._re.match("^x{1,3}$", "xxx"), None)
        self.assertNotEqual(self._re.match("^x{1,4}$", "xxx"), None)
        self.assertNotEqual(self._re.match("^x{3,4}?$", "xxx"), None)
        self.assertNotEqual(self._re.match("^x{3}?$", "xxx"), None)
        self.assertNotEqual(self._re.match("^x{1,3}?$", "xxx"), None)
        self.assertNotEqual(self._re.match("^x{1,4}?$", "xxx"), None)
        self.assertNotEqual(self._re.match("^x{3,4}?$", "xxx"), None)

        self.assertEqual(self._re.match("^x{}$", "xxx"), None)
        self.assertNotEqual(self._re.match("^x{}$", "x{}"), None)

    def test_getattr(self):
        self.assertEqual(self._re.compile(u("(?i)(a)(b)")).pattern, u("(?i)(a)(b)"))
        # the 63 below masks the expended flags used by RXPY
        self.assertEqual(self._re.compile(u("(?i)(a)(b)")).flags & 63, self._re.I | self._re.U)
        self.assertEqual(self._re.compile(u("(?i)(a)(b)")).groups, 2)
        self.assertEqual(self._re.compile(u("(?i)(a)(b)")).groupindex, {})
        self.assertEqual(self._re.compile(u("(?i)(?P<first>a)(?P<other>b)")).groupindex,
                         {'first': 1, 'other': 2})

        self.assertEqual(self._re.match("(a)", "a").pos, 0)
        self.assertEqual(self._re.match("(a)", "a").endpos, 1)
        self.assertEqual(self._re.match("(a)", "a").string, "a")
        self.assertEqual(self._re.match("(a)", "a").regs, ((0, 1), (0, 1)))
        self.assertNotEqual(self._re.match("(a)", "a").re, None)

    def test_special_escapes(self):
        if PYTHON3:
            u2 = u
        else:
            u2 = unicode # avoid strange escape error for \b
        self.assertEqual(self._re.search(r"\b(b.)\b",
                                   "abcd abc bcd bx").group(1), "bx")
        self.assertEqual(self._re.search(r"\B(b.)\B",
                                   "abc bcd bc abxd").group(1), "bx")
#        self.assertEqual(self._re.search(r"\b(b.)\b",
#                                   "abcd abc bcd bx", self._re.LOCALE).group(1), "bx")
#        self.assertEqual(self._re.search(r"\B(b.)\B",
#                                   "abc bcd bc abxd", self._re.LOCALE).group(1), "bx")
        self.assertEqual(self._re.search(u2(r"\b(b.)\b"),
                                   u2("abcd abc bcd bx"), self._re.UNICODE).group(1), "bx"
)
        self.assertEqual(self._re.search(u2(r"\B(b.)\B"),
                                  u2("abc bcd bc abxd"), self._re.UNICODE).group(1), "bx"
)
        self.assertEqual(self._re.search(u2(r"^abc$"), u2("\nabc\n"), self._re.M).group(0), "abc")
        self.assertEqual(self._re.search(u2(r"^\Aabc\Z$"), u2("abc"), self._re.M).group(0), "abc")
        self.assertEqual(self._re.search(u2(r"^\Aabc\Z$"), u2("\nabc\n"), self._re.M), None)
        self.assertEqual(self._re.search(u2(r"\b(b.)\b"),
                                   u2("abcd abc bcd bx")).group(1), "bx")
        self.assertEqual(self._re.search(u2(r"\B(b.)\B"),
                                   u2("abc bcd bc abxd")).group(1), "bx")
        self.assertEqual(self._re.search(u2(r"^abc$"), u2("\nabc\n"), self._re.M).group(0), "abc")
        self.assertEqual(self._re.search(u2(r"^\Aabc\Z$"), u2("abc"), self._re.M).group(0), "abc")
        self.assertEqual(self._re.search(u2(r"^\Aabc\Z$"), u2("\nabc\n"), self._re.M), None)
        self.assertEqual(self._re.search(u2(r"\d\D\w\W\s\S"),
                                   u2("1aa! a")).group(0), "1aa! a")
#        self.assertEqual(self._re.search(r"\d\D\w\W\s\S",
#                                   "1aa! a", self._re.LOCALE).group(0), "1aa! a")
        self.assertEqual(self._re.search(u2(r"\d\D\w\W\s\S"),
                                   u2("1aa! a"), self._re.UNICODE).group(0), "1aa! a")

    def test_bigcharset(self):
        self.assertEqual(self._re.match(u("([\u2222\u2223])"),
                                   u("\u2222")).group(1), u("\u2222"))
        self.assertEqual(self._re.match(u("([\u2222\u2223])"),
                                  u("\u2222"), self._re.UNICODE).group(1), u("\u2222"))

    def test_anyall(self):
        self.assertEqual(self._re.match("a.b", "a\nb", self._re.DOT_ALL).group(0),
                         "a\nb")
        self.assertEqual(self._re.match("a.*b", "a\n\nb", self._re.DOT_ALL).group(0),
                         "a\n\nb")

    def test_non_consuming(self):
        self.assertEqual(self._re.match("(a(?=\s[^a]))", "a b").group(1), "a")
        self.assertEqual(self._re.match("(a(?=\s[^a]*))", "a b").group(1), "a")
        self.assertEqual(self._re.match("(a(?=\s[abc]))", "a b").group(1), "a")
        self.assertEqual(self._re.match("(a(?=\s[abc]*))", "a bc").group(1), "a")
        self.assertEqual(self._re.match(r"(a)(?=\s\1)", "a a").group(1), "a")
        self.assertEqual(self._re.match(r"(a)(?=\s\1*)", "a aa").group(1), "a")
        self.assertEqual(self._re.match(r"(a)(?=\s(abc|a))", "a a").group(1), "a")

        self.assertEqual(self._re.match(r"(a(?!\s[^a]))", "a a").group(1), "a")
        self.assertEqual(self._re.match(r"(a(?!\s[abc]))", "a d").group(1), "a")
        self.assertEqual(self._re.match(r"(a)(?!\s\1)", "a b").group(1), "a")
        self.assertEqual(self._re.match(r"(a)(?!\s(abc|a))", "a b").group(1), "a")

    def test_ignore_case(self):
        self.assertEqual(self._re.match("abc", "ABC", self._re.I).group(0), "ABC")
        self.assertEqual(self._re.match("abc", "ABC", self._re.I).group(0), "ABC")
        self.assertEqual(self._re.match(r"(a\s[^a])", "a b", self._re.I).group(1), "a b")
        self.assertEqual(self._re.match(r"(a\s[^a]*)", "a bb", self._re.I).group(1), "a bb")
        self.assertEqual(self._re.match(r"(a\s[abc])", "a b", self._re.I).group(1), "a b")
        self.assertEqual(self._re.match(r"(a\s[abc]*)", "a bb", self._re.I).group(1), "a bb"
)
        self.assertEqual(self._re.match(r"((a)\s\2)", "a a", self._re.I).group(1), "a a")
        self.assertEqual(self._re.match(r"((a)\s\2*)", "a aa", self._re.I).group(1), "a aa")
        self.assertEqual(self._re.match(r"((a)\s(abc|a))", "a a", self._re.I).group(1), "a a")
        self.assertEqual(self._re.match(r"((a)\s(abc|a)*)", "a aa", self._re.I).group(1), "a aa")

    def test_category(self):
        self.assertEqual(self._re.match(r"(\s)", " ").group(1), " ")

    def test_getlower(self):
        import _sre
        self.assertEqual(_sre.getlower(ord('A'), 0), ord('a'))
#        self.assertEqual(_sre.getlower(ord('A'), self._re.LOCALE), ord('a'))
        self.assertEqual(_sre.getlower(ord('A'), self._re.UNICODE), ord('a'))

        self.assertEqual(self._re.match("abc", "ABC", self._re.I).group(0), "ABC")
        self.assertEqual(self._re.match("abc", "ABC", self._re.I).group(0), "ABC")

    def test_not_literal(self):
        self.assertEqual(self._re.search("\s([^a])", " b").group(1), "b")
        self.assertEqual(self._re.search("\s([^a]*)", " bb").group(1), "bb")

    def test_search_coverage(self):
        self.assertEqual(self._re.search("\s(b)", " b").group(1), "b")
        self.assertEqual(self._re.search("a\s", "a ").group(0), "a ")

    def test_re_escape(self):
        p=""
        self.assertEqual(self._re.escape(p), p)
        for i in range(0, 256):
            p = p + chr(i)
            self.assertEqual(self._re.match(self._re.escape(chr(i)), chr(i)) is not None,
                             True)
            self.assertEqual(self._re.match(self._re.escape(chr(i)), chr(i)).span(), (0,1))

        pat=self._re.compile(self._re.escape(p))
        self.assertEqual(pat.match(p) is not None, True)
        self.assertEqual(pat.match(p).span(), (0,256))

    def test_re_escape_byte(self):
        p=b""
        self.assertEqual(self._re.escape(p), p)
        for i in range(0, 256):
            b = bytes([i])
            p += b
            self.assertEqual(self._re.match(self._re.escape(b), b) is not None, True)
            self.assertEqual(self._re.match(self._re.escape(b), b).span(), (0,1), msg=str(b))

        pat=self._re.compile(self._re.escape(p))
        self.assertEqual(pat.match(p) is not None, True)
        self.assertEqual(pat.match(p).span(), (0,256))

    def pickle_test(self, pickle):
        oldpat = self._re.compile('a(?:b|(c|e){1,2}?|d)+?(.)')
        s = pickle.dumps(oldpat)
        newpat = pickle.loads(s)
        self.assertEqual(oldpat, newpat)

    def test_constants(self):
        self.assertEqual(self._re.I, self._re.IGNORECASE)
#        self.assertEqual(self._re.L, self._re.LOCALE)
        self.assertEqual(self._re.M, self._re.MULTILINE)
        self.assertEqual(self._re.S, self._re.DOT_ALL)
        self.assertEqual(self._re.X, self._re.VERBOSE)

    def test_flags(self):
#        for flag in [self._re.I, self._re.M, self._re.X, self._re.S, self._re.L]:
        for flag in [self._re.I, self._re.M, self._re.X, self._re.S]:
            self.assertNotEqual(self._re.compile('^pattern$', flag), None)

    def test_sre_character_literals(self):
        for i in [0, 8, 16, 32, 64, 127, 128, 255]:
            self.assertNotEqual(self._re.match(u(r"\%03o") % i, chr(i)), None)
            self.assertNotEqual(self._re.match(u(r"\%03o0") % i, chr(i)+"0"), None)
            self.assertNotEqual(self._re.match(u(r"\%03o8") % i, chr(i)+"8"), None)
            if PYTHON3:
                self.assertNotEqual(self._re.match(u(r"\x%02x") % i, chr(i)), None)
                self.assertNotEqual(self._re.match(u(r"\x%02x0") % i, chr(i)+"0"), None)
                self.assertNotEqual(self._re.match(u(r"\x%02xz") % i, chr(i)+"z"), None)
        self.assertRaises(self._re.error, self._re.match, "\911", "")

    def test_sre_character_class_literals(self):
        for i in [0, 8, 16, 32, 64, 127, 128, 255]:
            self.assertNotEqual(self._re.match(u(r"[\%03o]") % i, chr(i)), None)
            self.assertNotEqual(self._re.match(u(r"[\%03o0]") % i, chr(i)), None)
            self.assertNotEqual(self._re.match(u(r"[\%03o8]") % i, chr(i)), None)
            if PYTHON3: # i give up
                self.assertNotEqual(self._re.match(u(r"[\x%02x]") % i, chr(i)), None)
                self.assertNotEqual(self._re.match(u(r"[\x%02x0]") % i, chr(i)), None)
                self.assertNotEqual(self._re.match(u(r"[\x%02xz]") % i, chr(i)), None)
        self.assertRaises(self._re.error, self._re.match, u("[\911]"), "")

    def test_bug_113254(self):
        self.assertEqual(self._re.match(r'(a)|(b)', 'b').start(1), -1)
        self.assertEqual(self._re.match(r'(a)|(b)', 'b').end(1), -1)
        self.assertEqual(self._re.match(r'(a)|(b)', 'b').span(1), (-1, -1))

    def test_bug_527371(self):
        # bug described in patches 527371/672491
        self.assertEqual(self._re.match(r'(a)?a','a').lastindex, None)
        self.assertEqual(self._re.match(r'(a)(b)?b','ab').lastindex, 1)
        self.assertEqual(self._re.match(r'(?P<a>a)(?P<b>b)?b','ab').lastgroup, 'a')
        self.assertEqual(self._re.match("(?P<a>a(b))", "ab").lastgroup, 'a')
        self.assertEqual(self._re.match("((a))", "a").lastindex, 1)

    def test_bug_545855(self):
        # bug 545855 -- This pattern failed to cause a compile error as it
        # should, instead provoking a TypeError.
        self.assertRaises(self._re.error, self._re.compile, 'foo[a-')

    def test_bug_418626(self):
        # bugs 418626 at al. -- Testing Greg Chapman's addition of op code
        # SRE_OP_MIN_REPEAT_ONE for eliminating recursion on simple uses of
        # pattern '*?' on a long string.
        self.assertEqual(self._re.match('.*?c', 10000*'ab'+'cd').end(0), 20001)
        self.assertEqual(self._re.match('.*?cd', 5000*'ab'+'c'+5000*'ab'+'cde').end(0),
                         20003)
        self.assertEqual(self._re.match('.*?cd', 20000*'abc'+'de').end(0), 60001)
        # non-simple '*?' still used to hit the recursion limit, before the
        # non-recursive scheme was implemented.
        self.assertEqual(self._re.search('(a|b)*?c', 10000*'ab'+'cd').end(0), 20001)

    def test_bug_612074(self):
        pat="["+self._re.escape("\u2039")+"]"
        self.assertEqual(self._re.compile(pat) and 1, 1)

    def test_scanner(self):
        def s_ident(scanner, token): return token
        def s_operator(scanner, token): return "op%s" % token
        def s_float(scanner, token): return float(token)
        def s_int(scanner, token): return int(token)

        scanner = self._re.Scanner([
            (r"[a-zA-Z_]\w*", s_ident),
            (r"\d+\.\d*", s_float),
            (r"\d+", s_int),
            (r"=|\+|-|\*|/", s_operator),
            (r"\s+", None),
            ])

        self.assertNotEqual(scanner.scanner.scanner("").pattern, None)

        self.assertEqual(scanner.scan("sum = 3*foo + 312.50 + bar"),
                         (['sum', 'op=', 3, 'op*', 'foo', 'op+', 312.5,
                           'op+', 'bar'], ''))

    def test_bug_448951(self):
        # bug 448951 (similar to 429357, but with single char match)
        # (Also test greedy matches.)
        for op in '','?','*':
            self.assertEqual(self._re.match(r'((.%s):)?z'%op, 'z').groups(),
                             (None, None))
            self.assertEqual(self._re.match(r'((.%s):)?z'%op, 'a:z').groups(),
                             ('a:', 'a'))

    def test_bug_725106(self):
        # capturing groups in alternatives in repeats
        self.assertEqual(self._re.match('^((a)|b)*', 'abc').groups(),
                         ('b', 'a'))
        self.assertEqual(self._re.match('^(([ab])|c)*', 'abc').groups(),
                         ('c', 'b'))
        self.assertEqual(self._re.match('^((d)|[ab])*', 'abc').groups(),
                         ('b', None))
        self.assertEqual(self._re.match('^((a)c|[ab])*', 'abc').groups(),
                         ('b', None))
        self.assertEqual(self._re.match('^((a)|b)*?c', 'abc').groups(),
                         ('b', 'a'))
        self.assertEqual(self._re.match('^(([ab])|c)*?d', 'abcd').groups(),
                         ('c', 'b'))
        self.assertEqual(self._re.match('^((d)|[ab])*?c', 'abc').groups(),
                         ('b', None))
        self.assertEqual(self._re.match('^((a)c|[ab])*?c', 'abc').groups(),
                         ('b', None))

    def test_bug_725149(self):
        # mark_stack_base restoring before restoring marks
        self.assertEqual(self._re.match('(a)(?:(?=(b)*)c)*', 'abb').groups(),
                         ('a', None))
        self.assertEqual(self._re.match('(?_e)(a)((?!(b)*))*', 'abb').groups(),
                         ('a', None, None))

    def test_bug_764548(self):
        # bug 764548, self._re.compile() barfs on str/unicode subclasses
        class my_unicode(str): pass
        pat = self._re.compile(my_unicode("abc"))
        self.assertEqual(pat.match("xyz"), None)

    def test_finditer(self):
        iter = self._re.finditer(r":+", "a:b::c:::d")
        self.assertEqual([item.group(0) for item in iter],
                         [":", "::", ":::"])

    def test_bug_926075(self):
        self.assertTrue(self._re.compile('bug_926075') is not
                     self._re.compile(b'bug_926075'))

    def test_bug_931848(self):
        pattern = eval(u('"[\u002E\u3002\uFF0E\uFF61]"'))
        self.assertEqual(self._re.compile(pattern).split("a.b.c"),
                         ['a','b','c'])

    def test_bug_581080(self):
        iter = self._re.finditer(r"\s", "a b")
        self.assertEqual(next(iter).span(), (1,2))
        self.assertRaises(StopIteration, next, iter)

        scanner = self._re.compile(r"\s").scanner("a b")
        self.assertEqual(scanner.search().span(), (1, 2))
        self.assertEqual(scanner.search(), None)

    def test_bug_817234(self):
        iter = self._re.finditer(r".*", "asdf")
        self.assertEqual(next(iter).span(), (0, 4))
        self.assertEqual(next(iter).span(), (4, 4))
        self.assertRaises(StopIteration, next, iter)

    def test_bug_6561(self):
        # '\d' should match characters in Unicode category 'Nd'
        # (Number, Decimal Digit), but not those in 'Nl' (Number,
        # Letter) or 'No' (Number, Other).
        decimal_digits = [
            u('\u0037'), # '\N{DIGIT SEVEN}', category 'Nd'
            u('\u0e58'), # '\N{THAI DIGIT SIX}', category 'Nd'
            u('\uff10'), # '\N{FULLWIDTH DIGIT ZERO}', category 'Nd'
            ]
        for x in decimal_digits:
            self.assertEqual(self._re.match(u('^\d$'), x).group(0), x)

        not_decimal_digits = [
            '\u2165', # '\N{ROMAN NUMERAL SIX}', category 'Nl'
            '\u3039', # '\N{HANGZHOU NUMERAL TWENTY}', category 'Nl'
            '\u2082', # '\N{SUBSCRIPT TWO}', category 'No'
            '\u32b4', # '\N{CIRCLED NUMBER THIRTY NINE}', category 'No'
            ]
        for x in not_decimal_digits:
            self.assertIsNone(self._re.match('^\d$', x))

    def test_empty_array(self):
        # SF buf 1647541
        import array
        for typecode in 'bBuhHiIlLfd':
            a = array.array(typecode)
            self.assertEqual(self._re.compile(b"bla").match(a), None)
            self.assertEqual(self._re.compile(b"").match(a).groups(), ())

    def test_inline_flags(self):
        # Bug #1700
        upper_char = chr(0x1ea0) # Latin Capital Letter A with Dot Bellow
        lower_char = chr(0x1ea1) # Latin Small Letter A with Dot Bellow

        p = self._re.compile(upper_char, self._re.I | self._re.U)
        q = p.match(lower_char)
        self.assertNotEqual(q, None)

        p = self._re.compile(lower_char, self._re.I | self._re.U)
        q = p.match(upper_char)
        self.assertNotEqual(q, None)

        p = self._re.compile('(?i)' + upper_char, self._re.U)
        q = p.match(lower_char)
        self.assertNotEqual(q, None)

        p = self._re.compile('(?i)' + lower_char, self._re.U)
        q = p.match(upper_char)
        self.assertNotEqual(q, None)

        p = self._re.compile('(?iu)' + upper_char)
        q = p.match(lower_char)
        self.assertNotEqual(q, None)

        p = self._re.compile('(?iu)' + lower_char)
        q = p.match(upper_char)
        self.assertNotEqual(q, None)

    def test_dollar_matches_twice(self):
        "$ matches the end of string, and just before the terminating \n"
        pattern = self._re.compile('$')
        self.assertEqual(pattern.sub('#', 'a\nb\n'), 'a\nb#\n#')
        self.assertEqual(pattern.sub('#', 'a\nb\nc'), 'a\nb\nc#')
        self.assertEqual(pattern.sub('#', '\n'), '#\n#')

        pattern = self._re.compile('$', self._re.MULTILINE)
        self.assertEqual(pattern.sub('#', 'a\nb\n' ), 'a#\nb#\n#' )
        self.assertEqual(pattern.sub('#', 'a\nb\nc'), 'a#\nb#\nc#')
        self.assertEqual(pattern.sub('#', '\n'), '#\n#')

    def test_bytes_str_mixing(self):
        # Mixing str and bytes is disallowed
        pat = self._re.compile(u('.'))
        bpat = self._re.compile(b'.')
        self.assertRaises(TypeError, pat.match, b'b')
        self.assertRaises(TypeError, bpat.match, u('b'))
        self.assertRaises(TypeError, pat.sub, b'b', u('c'))
        self.assertRaises(TypeError, pat.sub, 'b', b'c')
        self.assertRaises(TypeError, pat.sub, b'b', b'c')
        self.assertRaises(TypeError, bpat.sub, b'b', u('c'))
        self.assertRaises(TypeError, bpat.sub, u('b'), b'c')
        self.assertRaises(TypeError, bpat.sub, u('b'), u('c'))

    def test_ascii_and_unicode_flag(self):
        # String patterns
        for flags in (0, self._re.UNICODE):
            pat = self._re.compile(u('\xc0'), flags | self._re.IGNORECASE)
            self.assertNotEqual(pat.match(u('\xe0')), None)
            pat = self._re.compile(u('\w'), flags)
            self.assertNotEqual(pat.match(u('\xe0')), None)
        pat = self._re.compile(u('\xc0'), self._re.ASCII | self._re.IGNORECASE)
        self.assertEqual(pat.match(u('\xe0')), None)
        pat = self._re.compile(u('(?a)\xc0'), self._re.IGNORECASE)
        self.assertEqual(pat.match(u('\xe0')), None)
        pat = self._re.compile(u('\w'), self._re.ASCII)
        self.assertEqual(pat.match(u('\xe0')), None)
        pat = self._re.compile(u('(?a)\w'))
        self.assertEqual(pat.match(u('\xe0')), None)
        # Bytes patterns
        for flags in (0, self._re.ASCII):
            pat = self._re.compile(b'\xc0', self._re.IGNORECASE)
            self.assertEqual(pat.match(b'\xe0'), None)
            pat = self._re.compile(b'\w')
            self.assertEqual(pat.match(b'\xe0'), None)
        # Incompatibilities
        self.assertRaises(ValueError, self._re.compile, b'\w', self._re.UNICODE)
        self.assertRaises(ValueError, self._re.compile, b'(?u)\w')
        self.assertRaises(ValueError, self._re.compile, '\w', self._re.UNICODE | self._re.ASCII)
        self.assertRaises(ValueError, self._re.compile, '(?u)\w', self._re.ASCII)
        self.assertRaises(ValueError, self._re.compile, '(?a)\w', self._re.UNICODE)
        self.assertRaises(ValueError, self._re.compile, '(?au)\w')

def run_re_tests():
    from test.re_tests import tests, SUCCEED, FAIL, SYNTAX_ERROR
    if verbose:
        print('Running re_tests test suite')
    else:
        # To save time, only run the first and last 10 tests
        #tests = tests[:10] + tests[-10:]
        pass

    for t in tests:
        sys.stdout.flush()
        pattern = s = outcome = repl = expected = None
        if len(t) == 5:
            pattern, s, outcome, repl, expected = t
        elif len(t) == 3:
            pattern, s, outcome = t
        else:
            raise ValueError('Test tuples should have 3 or 5 fields', t)

        try:
            obj = self._re.compile(pattern)
        except self._re.error:
            if outcome == SYNTAX_ERROR: pass  # Expected a syntax error
            else:
                print('=== Syntax error:', t)
        except KeyboardInterrupt: raise KeyboardInterrupt
        except:
            print('*** Unexpected error ***', t)
            if verbose:
                traceback.print_exc(file=sys.stdout)
        else:
            try:
                result = obj.search(s)
            except self._re.error as msg:
                print('=== Unexpected exception', t, repr(msg))
            if outcome == SYNTAX_ERROR:
                # This should have been a syntax error; forget it.
                pass
            elif outcome == FAIL:
                if result is None: pass   # No match, as expected
                else: print('=== Succeeded incorrectly', t)
            elif outcome == SUCCEED:
                if result is not None:
                    # Matched, as expected, so now we compute the
                    # result string and compare it to our expected result.
                    start, end = result.span(0)
                    vardict={'found': result.group(0),
                             'groups': result.group(),
                             'flags': result.self._re.flags}
                    for i in range(1, 100):
                        try:
                            gi = result.group(i)
                            # Special hack because else the string concat fails:
                            if gi is None:
                                gi = "None"
                        except IndexError:
                            gi = "Error"
                        vardict['g%d' % i] = gi
                    for i in result.self._re.groupindex.keys():
                        try:
                            gi = result.group(i)
                            if gi is None:
                                gi = "None"
                        except IndexError:
                            gi = "Error"
                        vardict[i] = gi
                    repl = eval(repl, vardict)
                    if repl != expected:
                        print('=== grouping error', t, end=' ')
                        print(repr(repl) + ' should be ' + repr(expected))
                else:
                    print('=== Failed incorrectly', t)

                # Try the match with both pattern and string converted to
                # bytes, and check that it still succeeds.
                try:
                    bpat = bytes(pattern, "ascii")
                    bs = bytes(s, "ascii")
                except UnicodeEncodeError:
                    # skip non-ascii tests
                    pass
                else:
                    try:
                        bpat = self._re.compile(bpat)
                    except Exception:
                        print('=== Fails on bytes pattern compile', t)
                        if verbose:
                            traceback.print_exc(file=sys.stdout)
                    else:
                        bytes_result = bpat.search(bs)
                        if bytes_result is None:
                            print('=== Fails on bytes pattern match', t)

                # Try the match with the search area limited to the extent
                # of the match and see if it still succeeds.  \B will
                # break (because it won't match at the end or start of a
                # string), so we'll ignore patterns that feature it.

                if pattern[:2] != '\\B' and pattern[-2:] != '\\B' \
                               and result is not None:
                    obj = self._re.compile(pattern)
                    result = obj.search(s, result.start(0), result.end(0) + 1)
                    if result is None:
                        print('=== Failed on range-limited match', t)

                # Try the match with IGNORECASE enabled, and check that it
                # still succeeds.
                obj = self._re.compile(pattern, self._re.IGNORECASE)
                result = obj.search(s)
                if result is None:
                    print('=== Fails on case-insensitive match', t)

                # Try the match with LOCALE enabled, and check that it
                # still succeeds.
#                if '(?u)' not in pattern:
#                    obj = self._re.compile(pattern, self._re.LOCALE)
#                    result = obj.search(s)
#                    if result is None:
#                        print('=== Fails on locale-sensitive match', t)

                # Try the match with UNICODE locale enabled, and check
                # that it still succeeds.
                obj = self._re.compile(pattern, self._re.UNICODE)
                result = obj.search(s)
                if result is None:
                    print('=== Fails on unicode-sensitive match', t)
