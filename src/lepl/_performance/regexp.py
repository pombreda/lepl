
from lepl import *
from lepl.regexp import unicode_parser


def test_parser(text):
    return unicode_parser(None, text)

def lexer():
    '''
    Parsing expression seems slow
    '''
    #basicConfig(level=DEBUG)
    c = test_parser('[a-ce-g]')
    assert '[a-ce-g]' == str(c), str(c)
    c = test_parser('[a-cd-f]')
    assert '[a-f]' == str(c), str(c)
    c = test_parser('[a-cc-e]')
    assert '[a-e]' == str(c), str(c)
    c = test_parser('[a-cb-d]')
    assert '[a-d]' == str(c), str(c)
    c = test_parser('[a-ca-c]')
    assert '[a-c]' == str(c), str(c)
    c = test_parser('[a-a]')
    assert 'a' == str(c), str(c)
    c = test_parser('[e-ga-c]')
    assert '[a-ce-g]' == str(c), str(c)
    c = test_parser('[d-fa-c]')
    assert '[a-f]' == str(c), str(c)
    c = test_parser('[c-ea-c]')
    assert '[a-e]' == str(c), str(c)
    c = test_parser('[b-da-c]')
    assert '[a-d]' == str(c), str(c)
    c = test_parser('[a-gc-e]')
    assert '[a-g]' == str(c), str(c)
    c = test_parser('[c-ea-g]')
    assert '[a-g]' == str(c), str(c)
    c = test_parser('[a-eg]')
    assert '[a-eg]' == str(c), str(c)
    c = test_parser('[ga-e]')
    assert '[a-eg]' == str(c), str(c)
    print('done')


def time():
    from timeit import Timer
    t = Timer("lexer()", "from __main__ import lexer")
    print(t.timeit(number=10)) 
    # 10.5
    # 2.6 without GeneratorManager

def profile():
    '''
import pstats
p=pstats.Stats('lexer.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('lexer()', 'lexer.prof')

if __name__ == '__main__':
    time()
#    profile()
#    lexer()

    
    
