#LICENCE

from _collections import deque
from bisect import bisect_left


def edge_iterator(node):
    '''
    Generate a sequence of all the edges (as ordered node pairs) reachable
    in the graph starting from the given node.
    '''
    stack = [node]
    visited = set()
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            for next in node.next:
                edge = (node, next)
                yield edge
                if next not in visited:
                    stack.append(next)


def node_iterator(node):
    '''
    Generate a sequence of all the nodes reachable in the graph starting
    from the given node (DFS).
    '''
    stack = [node]
    visited = set()
    while stack:
        node = stack.pop()
        yield node
        visited.add(node)
        for next in node.next:
            if next not in visited:
                stack.append(next)


class ReadsGroup(object):
    '''
    Used to identify opcodes that require groups.
    '''


class CharSet(object):
    '''
    A set of possible values for a character, described as a collection of
    intervals.  Each interval is [a, b] (ie a <= x <= b, where x is a character
    code).  We use open bounds to avoid having to specify an "out of range"
    value.

    The intervals are stored in a normalised list, ordered by a, joining
    overlapping intervals as necessary.
    '''

    def __init__(self, intervals, alphabet):
        self.intervals = deque()
        self.__index = None
        self.__str = None
        for interval in intervals:
            self.append(interval, alphabet)

    def append(self, interval, alphabet):
        '''
        Add an interval to the existing intervals.

        This maintains self.intervals in the normalized form described above.
        '''
        self.__index = None
        self.__str = None

        (a1, b1) = map(alphabet.expression_to_letter, interval)
        if b1 < a1:
            (a1, b1) = (b1, a1)
        intervals = deque()
        done = False
        while self.intervals:
            (a0, b0) = self.intervals.popleft()
            if a0 <= a1:
                if b0 < a1 and (b0 != alphabet.before(a1)):
                    # old interval starts and ends before new interval
                    # so keep old interval and continue
                    intervals.append((a0, b0))
                elif b1 <= b0:
                    # old interval starts before and ends after new interval
                    # so keep old interval, discard new interval and slurp
                    intervals.append((a0, b0))
                    done = True
                    break
                else:
                    # old interval starts before new, but partially overlaps
                    # so discard old interval, extend new interval and continue
                    # (since it may overlap more intervals...)
                    (a1, b1) = (a0, b1)
            else:
                if b1 < a0 and (b1 != alphabet.before(a0)):
                    # new interval starts and ends before old, so add both
                    # and slurp
                    intervals.append((a1, b1))
                    intervals.append((a0, b0))
                    done = True
                    break
                elif b0 <= b1:
                    # new interval starts before and ends after old interval
                    # so discard old and continue (since it may overlap...)
                    pass
                else:
                    # new interval starts before old, but partially overlaps,
                    # add extended interval and slurp rest
                    intervals.append((a1, b0))
                    done = True
                    break
        if not done:
            intervals.append((a1, b1))
        intervals.extend(self.intervals) # slurp remaining
        self.intervals = intervals

    def __contains__(self, c):
        '''
        Does the value lie within the intervals?
        '''
        if self.__index is None:
            self.__index = [interval[1] for interval in self.intervals]
        if self.__index:
            index = bisect_left(self.__index, c)
            if index < len(self.intervals):
                (a, b) = self.intervals[index]
                return a <= c <= b
        return False

    def __format_interval(self, interval, alphabet):
        (a, b) = interval
        if a == b:
            return alphabet.letter_to_str(a)
        elif a == alphabet.before(b):
            return alphabet.letter_to_str(a) + alphabet.letter_to_str(b)
        else:
            return alphabet.letter_to_str(a) + '-' + alphabet.letter_to_str(b)

    def to_str(self, alphabet):
        '''
        Format the interval, given a particular alphabet.
        '''
        if self.__str is None:
            self.__str = ''.join(map(lambda x: self.__format_interval(x, alphabet),
                                     self.intervals))
        return self.__str

    def simplify(self, alphabet, default):
        '''
        Reduce to a simpler opcode when possible.
        '''
        from lepl.rxpy.graph.opcode import String, Dot
        if len(self.intervals) == 1:
            if self.intervals[0][0] == self.intervals[0][1]:
                return String(self.intervals[0][0])
            elif self.intervals[0][0] == alphabet.min and \
                    self.intervals[0][1] == alphabet.max:
                return Dot(True)
        return default

    def __bool__(self):
        return bool(self.intervals)

    def __nonzero__(self):
        return self.__bool__()


def contains_instance(graph, type_):
    for node in node_iterator(graph):
        if isinstance(node, type_):
            return True
    return False
