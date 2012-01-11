
from lepl.lexer.matchers import Token

def tokens():
    ML_COMMENT = Token(r'/\*([^\*]*\*)*/')


def parser():
    tokens()
    


if __name__ == '__main__':
    parser = parser()
    grammar = parser.parse_file(
        '/home/andrew/projects/personal/lepl/lepl-hg/src/lepl/contrib/ANTLRv3.g.txt')
