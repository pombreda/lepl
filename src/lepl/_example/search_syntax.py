
'''
http://stackoverflow.com/questions/2364683/what-is-a-good-python-parser-for-a-google-like-search-query
'''

from unittest import TestCase

from lepl import *


class SearchTest(TestCase):
    
    def compile(self):
        
        class Alternatives(Node):
            pass
        
        class Query(Node):
            pass
        
        class Text(Node):
            pass

        qualifier      = Word() + Drop(':')           > 'qualifier'
        word           = ~Lookahead('OR') & Word()
        phrase         = String()
        text           = (phrase | word)
        word_or_phrase = (Optional(qualifier) & text) > Text
        space          = Drop(Space()[1:])
        query          = word_or_phrase[1:, space]    > Query
        separator      = Drop(space & 'OR' & space)
        alternatives   = query[:, separator]          > Alternatives
        return alternatives.get_parse_string()
        
    def test_word(self):
        result = self.compile()('word')
        #print(str(result[0]))
        assert result, result
        
    def test_complex(self):
        result = self.compile()('all of these words "with this phrase" '
                                'OR that OR this site:within.site '
                                'filetype:ps from:lastweek')
        #print(str(result[0]))
        assert result, result
        
        