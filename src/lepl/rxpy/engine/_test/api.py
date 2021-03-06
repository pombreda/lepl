#LICENCE


from lepl.rxpy.engine._test.base import BaseTest


class ReTest(BaseTest):
    
    def assert_groups(self, pattern, text, groups, target):
        try:
            results = self._re.compile(pattern).match(text).group(*groups)
            assert results == target, repr(results)
        except Exception as e:
            if isinstance(target, type):
                assert isinstance(e, target), repr(e)
            else:
                assert False, repr(e)
    
    def test_zero(self):
        self.assert_groups('.*', 'abc', [], 'abc')
        self.assert_groups('.*', 'abc', [0], 'abc')
        self.assert_groups('.(.).', 'abc', [], 'abc')
        self.assert_groups('.(.).', 'abc', [0], 'abc')
    
    def test_numbered(self):
        self.assert_groups('.(.).', 'abc', [1], 'b')
        self.assert_groups('.(.)*', 'abc', [1], 'c')
        self.assert_groups('.(.).(.?)', 'abc', [2], '')
        self.assert_groups('.(.).(.)?', 'abc', [2], None)
        self.assert_groups('.(.).(.?)', 'abc', [3], IndexError)
        self.assert_groups('(?_g)(?P<4>.)(?P<4>.)', 'ab', [4], 'b')
        results = self._re.compile('(?_g)(?P<4>.)(?P<4>.)').match('ab')
        assert results.groups() == ('b',), results.groups()


    def assert_split(self, pattern, text, target, *args):
        result = self._re.compile(pattern).split(text, *args)
        assert result == target, result
        
    def test_split_from_docs(self):
        self.assert_split(r'[^A-Za-z]+', 'Words, words, words.',
                          ['Words', 'words', 'words', ''])
        self.assert_split(r'([^A-Za-z]+)', 'Words, words, words.',
                          ['Words', ', ', 'words', ', ', 'words', '.', ''])
        self.assert_split(r'[^A-Za-z]+', 'Words, words, words.',
                          ['Words', 'words, words.'], 1)
        self.assert_split(r'\W+', 'Words, words, words.',
                          ['Words', 'words', 'words', ''])
        self.assert_split(r'(\W+)', 'Words, words, words.',
                          ['Words', ', ', 'words', ', ', 'words', '.', ''])
        self.assert_split(r'\W+', 'Words, words, words.',
                          ['Words', 'words, words.'], 1)
        
    def test_match(self):
        results = self._re.compile('.*?(x+)').match('axxb')
        assert results
        assert results.group(1) == 'xx', results.group(1)
        
    def test_findall(self):
        match = self._re.compile('(a|(b))').match('aba')
        assert match.re.groups == 2, match.re.groups
        assert match.group(0) == 'a', match.group(0)
        assert match.group(1) == 'a', match.group(1)
        assert match.group(2) == None, match.group(2)
        
        results = self._re.compile('(a|(b))').findall('aba')
        assert results == [('a', ''), ('b', 'b'), ('a', '')], results
        
        results = self._re.compile('x*').findall('a')
        assert len(results) == 2, results
        
    def test_find_from_docs(self):
        assert self._re.search(r"[a-zA-Z]+ly", 
            "He was carefully disguised but captured quickly by police.")
        results = self._re.findall(r"[a-zA-Z]+ly", 
            "He was carefully disguised but captured quickly by police.")
        assert results == ['carefully', 'quickly'], results
        results = self._re.findall(r"\w+ly", 
            "He was carefully disguised but captured quickly by police.")
        assert results == ['carefully', 'quickly'], results
        
    def test_search(self):
        results = self._re.search('a*b', 'aab')
        assert results
        assert results.group(0) == 'aab', results.group(0)
        
    def test_findall_empty(self):
        results = self._re.findall('x+', 'abxd')
        assert results == ['x'], results
        results = self._re.findall('x*', 'abxd')
        # this checks against actual behaviour
        assert results == ['', '', 'x', '', ''], results

    def test_findall_sub(self):
        # this also checks against behaviour
        results = self._re.sub('x*', '-', 'abxd')
        assert results == '-a-b-d-', results
        # this too
        results = self._re.sub('x*?', '-', 'abxd')
        assert results == '-a-b-x-d-', results
        
    def test_end_of_line(self):
        results = list(self._re.compile('$').finditer('ab\n'))
        assert len(results) == 2, len(results)
        assert results[0].group(0) == '', results[0].group(0)
        assert results[0].span(0) == (2,2), results[0].span(0)
        assert results[1].group(0) == '', results[1].group(0)
        assert results[1].span(0) == (3,3), results[1].span(0)
        
        results = self._re.sub('$', 'x', 'ab\n')
        assert results == 'abx\nx', results

    # TODO - make this work
#    def test_pickle(self):
#        import pickle
#        self.pickle_test(pickle)

    def pickle_test(self, pickle):
        oldpat = self._re.compile('a(?:b|(c|e){1,2}?|d)+?(.)')
        s = pickle.dumps(oldpat)
        newpat = pickle.loads(s)
        assert oldpat.deep_eq(newpat)


    def test_escape(self):
        text = '123abc;.,}{? '
        esc = self._re.escape('123abc;.,}{? ')
        assert esc == '123abc\\;\\.\\,\\}\\{\\?\\ ', esc
        result = self._re.compile(esc).match(text)
        assert result


    # TODO - how should this work in 3?
#    def test_types(self):
#        for pattern in ('.', 'a', u'u'):
#            for text in ('a', 'u', u'a', u'u'):
#                for repl in ('A', u'U'):
#                    for flags in (0, ParserState.ASCII, ParserState.UNICODE):
#                        s = self._re.sub(pattern, repl, text, flags=flags)
#                        print(pattern, text, repl, flags, s)
#                        if flags:
#                            if flags == ParserState.ASCII and type(text) == str:
#                                assert type(s) == str, type(s)
#                            else:
#                                assert type(s) == unicode, type(s)
#                        else:
#                            if type(text) == str and type(pattern) == str:
#                                assert type(s) == str, type(s)
#                            else:
#                                assert type(s) == unicode, type(s)

