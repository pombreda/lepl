#LICENCE


from unittest import TestCase

from re import compile


class EscapeTest(TestCase):
    
    def test_literal_escape(self):
        '''
        This shows that the regexp interpreter itself expands literal escape
        characters.
        '''
        p = compile('a\\x62c')
        assert p.match('abc')
        assert not p.match('axc')
        assert p.match('a\x62c')
        
    def test_escape(self):
        '''
        Alternatively, the character can be simply used
        '''
        p = compile('a\x62c')
        assert p.match('abc')
        assert not p.match('axc')
        assert p.match('a\x62c')

    def test_slash_escape(self):
        '''
        See http://groups.google.com/group/comp.lang.python/browse_thread/thread/3a27b819307c0cb6#
        '''
        p = compile('a\\\x62c')
#        assert p.match('a\\bc')

    def test_nested_groups(self):
        p = compile('(.)*')
        m = p.match('ab')
        assert m
        assert m.groups() == ('b',), m.groups()
        assert m.group(0) == 'ab', m.group(0)
        assert m.group(1) == 'b', m.group(1)
        
        p = compile(r'(?:\s*(\b\w+\b)\s*){3}')
        m = p.match('foo bar baz ')
        assert m
        assert m.groups() == ('baz',), m.groups()
        
        p = compile(r'(?:\s*(\b\w*\b)\s*){3}')
        m = p.match(' a ab abc ')
        assert m.group(0) == ' a ab abc ', m.group(0)
        
#        p = compile('(\b.*?\b)*')
#        m = p.match(' a  ab  abc ')
#        assert m.groups() == ('abc'), m.groups()
        
    def test_lookback(self):
        p = compile('..(?<=a)')
        assert p.match('xa')
        assert not p.match('ax')
        
    def test_groups_in_lookback(self):
        p = compile('(.).(?<=a(.))')
        result = p.match('ab')
        assert result
        assert result.group(1) == 'a'
        assert result.group(2) == 'b'

        assert compile('(.).(?<=(?(1)))').match('ab')
        try:
            assert not compile('(.).(?<=(?(2)))').match('ab')
            assert False, 'expected error'
        except:
            pass
        
        # these work as expected
        
        assert compile('(a)b(?<=b)(c)').match('abc')
        assert not compile('(a)b(?<=c)(c)').match('abc')
        assert compile('(a)b(?=c)(c)').match('abc')
        assert not compile('(a)b(?=b)(c)').match('abc')
        
        # but when you add groups, you get bugs
        
        #assert not compile('(?:(a)|(x))b(?<=(?(2)x|c))c').match('abc') # this matches!
        assert not compile('(?:(a)|(x))b(?<=(?(2)b|x))c').match('abc')
        #assert compile('(?:(a)|(x))b(?<=(?(2)x|b))c').match('abc') # this doesn't match!
        #assert not compile('(?:(a)|(x))b(?<=(?(1)c|x))c').match('abc') # this matches!
        #assert compile('(?:(a)|(x))b(?<=(?(1)b|x))c').match('abc') # this doesn't match
        
        # but lookahead works as expected
        
        assert compile('(?:(a)|(x))b(?=(?(2)x|c))c').match('abc')
        assert not compile('(?:(a)|(x))b(?=(?(2)c|x))c').match('abc')
        assert compile('(?:(a)|(x))b(?=(?(2)x|c))c').match('abc')
        assert not compile('(?:(a)|(x))b(?=(?(1)b|x))c').match('abc')
        assert compile('(?:(a)|(x))b(?=(?(1)c|x))c').match('abc')
      
        #assert not compile('(a)b(?<=(?(2)x|c))(c)').match('abc') # this matches!
        assert not compile('(a)b(?<=(?(2)b|x))(c)').match('abc')
        #assert not compile('(a)b(?<=(?(1)c|x))(c)').match('abc') # this matches!
        #assert compile('(a)b(?<=(?(1)b|x))(c)').match('abc') # this doesn't match
        
        assert compile('(a)b(?=(?(2)x|c))(c)').match('abc')
        assert not compile('(a)b(?=(?(2)b|x))(c)').match('abc')
        assert compile('(a)b(?=(?(1)c|x))(c)').match('abc')
        
        # this is the error we should see above
        try:
            compile('(a)\\2(b)')
            assert False, 'expected error'
        except:
            pass
        
    def test_empty_loops(self):
        try:
            compile('a**')
            assert False, 'expected error'
        except:
            pass
        try:
            assert compile('a{0,1}*').match('a')
            assert False, 'expected error'
        except:
            pass
        assert compile('(a|)*').match('ab')
        assert compile('(a|)\\1*').match('b')
