#LICENCE

from math import log, log10
from os.path import join
from time import time

from lepl.rxpy._bench.re_python import _re as R_PYTHON
from lepl.rxpy.engine.backtrack.re import _re as R_B
from lepl.rxpy.engine.complex.re import _re as R_C
from lepl.rxpy.engine.hybrid.re import _re as R_H
from lepl.rxpy.engine.simple.re import _re as R_S


def execute(engines, benchmarks, trace=False, repeat=3):
    for benchmark in benchmarks:
        if trace: print benchmark
        def results():
            for engine in engines:
                if trace: print '.',
                secs = [benchmark(engine) for _i in range(repeat)]
                secs.sort()
                secs = secs[repeat/2]
                yield (engine, secs)
            if trace: print
        yield (benchmark, results())
    
        
def write(engines, benchmarks, directory='./'):
    for (benchmark, data) in execute(engines, benchmarks):
        with file(join(directory, str(benchmark) + '.dat'), 'w') as out:
            for (engine, secs) in data:
                print >> out, secs, ';', str(engine)
                
                
def text_histogram(engines, benchmarks):
    
    def right(text, width):
        text = str(text)
        l = len(text)
        if l > width:
            return text[0:width-3] + '...'
        else:
            return (width - l) * ' ' + text
        
    def lin_bar(x, all, l):
        m = max(all)
        x = int(float(x) / (float(m) / l) + 0.5)
        return min(l, max(x, 0))
        
    def log_bar(x, all, l):
        mn, mx = min(all), max(all)
        x = int(log(float(x) / mn) / log(float(mx) / mn) * l + 0.5)
        return min(l, max(x, 0))
    
    def bar(x, all, l):
        ln = lin_bar(x, all, l)
        lg = log_bar(x, all, l)
        line = ['#'] * ln
        if lg > ln:
            line += [' '] * (lg-ln-1) + [']']
        else:
            if line and lg > 0:
                line[lg-1] = ']'
        if line:
            if line[0] == ']':
                line[0] = '|'
            else:
                line[0] = '['
        return ''.join(line + [' '] * (l-max(lg,ln)))
        
    for (benchmark, data) in execute(engines, benchmarks):
        print
        print benchmark
        (engines, secs) = zip(*list(data))
        for (engine, sec) in zip(engines[1:], secs[1:]):
            print '{0} {1}{2:7.0f} [{3:3.1f}]'.format(
                right(engine, 25), bar(sec, secs, 40), 
                sec/secs[0], log10(sec/secs[0]))
            

class BaseBenchmark(object):
    
    def __init__(self, name, count):
        self.__name = name
        self._count = count
        
    def __str__(self):
        return self.__name
    
    def start(self):
        self.__start = time()

    def finish(self):
        return (time() - self.__start) / float(self._count)
    
    
class CompileBenchmark(BaseBenchmark):
    
    def __init__(self, name, pattern, count):
        super(CompileBenchmark, self).__init__(name, count)
        self._pattern = pattern
        
    def __call__(self, engine):
        self.start()
        for _i in range(self._count):
            engine.compile(self._pattern)
        return self.finish()


class MatchBenchmark(CompileBenchmark):
    
    def __init__(self, name, pattern, count, text, search=False, match=True):
        super(MatchBenchmark, self).__init__(name, pattern, count)
        self._text = text
        self._search = search
        self._match = match
        
    def __call__(self, engine):
        regexp = engine.compile(self._pattern)
        self.start()
        for _i in range(self._count):
            if self._search:
                result = regexp.search(self._text)
            else:
                result = regexp.match(self._text)
            assert bool(result) == self._match, repr((result, engine))
        return self.finish()
    
    
def exponential(n):
    return MatchBenchmark('Match a?^na^n against a^n for n=' + str(n), 
                          n * 'a?' + n * 'a', 1000, n*'a')

def exponential2(n):
    return MatchBenchmark('Match (?:ab)?^n(?:ab)^n against (ab)^n for n=' + str(n), 
                          n * '(?:ab)?' + n * '(?:ab)', 10, n*'ab')

def exponential3(n):
    return MatchBenchmark('Match (?:a*b)?^n(?:a*b)^n against (ab)^n for n=' + str(n), 
                          n * '(?:a*b)?' + n * '(?:a*b)', 10, n*'ab')

def exponential4(n):
    return MatchBenchmark('Match (?:a|b)?^2n(?:ab)^n against (ab)^n for n=' + str(n), 
                          2 * n * '(?:a|b)?' + n * 'ab', 10, n*'ab')

def exponential5(n):
    return MatchBenchmark('Match (a|b)?^2n(?:ab)^n against (ab)^n for n=' + str(n), 
                          2 * n * '(a|b)?' + n * 'ab', 10, n*'ab')
    
def prime(n, match=True):
    return MatchBenchmark('Primality ' + str(n), 
                          r'^1?$|^(11+?)\1+$', 1, n * '1', match=match)

def prime2(n, match=True):
    return MatchBenchmark('Primality (eager) ' + str(n), 
                          r'^1?$|^(11+)\1+$', 1, n * '1', match=match)

    

if __name__ == '__main__':
    text_histogram([R_PYTHON, R_B, R_C, R_H, R_S], [
        MatchBenchmark('Match . against a', 
                       '.', 100, 'a'),
        ])
    text_histogram([R_PYTHON, R_B, R_C, R_H], [
        MatchBenchmark('Match a(.)c against abc', 
                       'a(.)c', 100, 'abc'),
#        MatchBenchmark('Match (a)b(?<=(?(1)b|x))(c) against abc',
#                       '(a)b(?<=(?(1)b|x))(c)', 100, 'abc'),
        ])
    text_histogram([R_PYTHON, R_B, R_C, R_H, R_S], [
        MatchBenchmark('Match a*b against a^100b', 
                       'a*b', 2, 100*'a' + 'b'),
        MatchBenchmark('Search .*b against a^100b',
            '.*b', 1, 100*'a' + 'b', search=True),
        MatchBenchmark('Match .*b against a^100b',
                       '.*b', 2, 100*'a' + 'b'),
        ])
    text_histogram([R_PYTHON, R_C, R_H, R_S], [
        MatchBenchmark('Match .*b against a^100b',
            '.*b', 2, 100*'a' + 'b'),
        ])
    text_histogram([R_PYTHON, R_B, R_C, R_H], [
        MatchBenchmark('Match (.*) (.*) (.*)  against abc abc abc', 
                       '(.*) (.*) (.*)', 10, 'abc abc abc'),
        ])
    print
    text_histogram([R_PYTHON, R_B, R_C, R_H, R_S], [
        MatchBenchmark('Search .*?a*b against a^10b', 
                       '.*?a*b', 1, 10*'a' + 'b', search=True),
        ])
    text_histogram([R_PYTHON, R_B, R_C, R_H, R_S], [
        MatchBenchmark('Search .*?a*b against a^100b', 
                       '.*?a*b', 1, 100*'a' + 'b', search=True),
        ])
    text_histogram([R_PYTHON, R_B, R_C, R_H, R_S], [
        MatchBenchmark('Search .*?a*b against a^1000b', 
                       '.*?a*b', 1, 1000*'a' + 'b', search=True),
        ])
    print
    text_histogram([R_PYTHON, R_C, R_H], [
        exponential5(4),
        ])
    text_histogram([R_PYTHON, R_C, R_H], [
        exponential5(6),
        ])
    print
    text_histogram([R_PYTHON, R_C, R_H, R_S], [
        exponential4(4),
        ])
    text_histogram([R_PYTHON, R_C, R_H, R_S], [
        exponential4(6),
        ])
    text_histogram([R_PYTHON, R_C, R_H, R_S], [
        exponential4(8),
        exponential(8),
        ])
    print
    text_histogram([R_PYTHON, R_C, R_H], [
        prime(32),
        prime(37, False),
        ])
    text_histogram([R_PYTHON, R_C, R_H], [
        prime(128),
        prime(131, False),
        ])
    text_histogram([R_PYTHON, R_C, R_H], [
        prime2(32),
        prime2(37, False),
        ])
    text_histogram([R_PYTHON, R_C, R_H], [
        prime2(128),
        prime2(131, False),
        ])
    
