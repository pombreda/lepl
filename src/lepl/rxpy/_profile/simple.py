#LICENCE

import re as R_PYTHON
from time import time

from lepl.rxpy.engine.simple.re import _re as R_S

def main(engine):
    regexp = engine.compile(r'.*\d{2}')
    start = time()
    for i in range(1000):
        s = 'a' * i + '42'
#        print(s)
        match = regexp.match(s)
#        print(match.group(0))
    print(time() - start)

if __name__ == '__main__':
    main(R_S)
#    main(R_PYTHON)
