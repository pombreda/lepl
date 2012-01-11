#LICENCE

from lepl.rxpy.graph.base_graph import AutoClone
from lepl.rxpy.graph.opcode import String, Checkpoint, Split, Repeat, NoMatch
from lepl.rxpy.parser.support import ParserState
from lepl.rxpy.support import _CHARS
from lepl.support.lib import unimplemented


class BaseCollection(AutoClone):
    '''
    Standard support for collections of nodes.  These allow the graph to be
    assembled in "logical chunks" and then connected later.
    '''

    def __init__(self, contents=None):
        super(BaseCollection, self).__init__(fixed=['contents', 'fixed'])
        if contents is None:
            contents = []
        self.contents = list(contents)

    def append(self, content):
        '''Add a node (or collection) to this collection.'''
        self.contents.append(content)

    @unimplemented
    def consumer(self, lenient):
        '''Does this collection consume input data?'''
        pass

    @unimplemented
    def join(self, final, parser_state):
        '''Connect this collection so that it ends in `final`.'''
        pass

    def clone(self):
        '''Make a deep copy.'''
        clone = super(BaseCollection, self).clone()
        clone.contents = list(map(lambda x: x.clone(), self.contents))
        return clone

    def __bool__(self):
        return bool(self.contents)

    def __nonzero__(self):
        return self.__bool__()


class Sequence(BaseCollection):
    '''
    A sequence of nodes which are matched in turn.
    '''

    def consumer(self, lenient):
        '''Does this sequence consume input data?'''
        for node in self.contents:
            if node.consumer(lenient):
                return True
        return False

    def join(self, final, parser_state):
        '''Connect this sequence so that it ends in `final`.'''
        self.contents = list(self._unpack_nested_sequences(self.contents))
        if not (parser_state.flags & _CHARS):
            self.contents = list(self._merge_strings(parser_state, self.contents))
        for content in reversed(self.contents):
            final = content.join(final, parser_state)
        return final

    def _unpack_nested_sequences(self, contents):
        for content in contents:
            if type(content) is Sequence:
                for inner in self._unpack_nested_sequences(content.contents):
                    yield inner
            else:
                yield content

    def _merge_strings(self, parser_state, contents):
        current = None
        for content in contents:
            if isinstance(content, String):
                if current:
                    current.extend(content.text, parser_state)
                else:
                    current = content
            else:
                if current:
                    yield current
                    current = None
                yield content
        if current:
            yield current

    def pop(self):
        '''Returns (and removes) the first item, as a sequence.'''
        content = self.contents.pop()
        if not isinstance(content, Sequence):
            content = Sequence([content])
        return content

    def clone(self):
        '''Deep copy, unpkacing singletons.'''
        clone = super(Sequence, self).clone()
        # restrict to this class; subclasses are not un-packable
        if type(clone) is Sequence and len(clone.contents) == 1:
            return clone.contents[0]
        else:
            return clone


class LabelMixin(object):
    '''
    Add a label to a container.
    '''

    #noinspection PyArgumentList
    def __init__(self, contents=None, label=None, **kargs):
        super(LabelMixin, self).__init__(contents=contents, **kargs)
        self.label = label


class LazyMixin(object):
    '''
    Add a "lazy" flag to a container.  This is the opposite of eager (so
    a lazy repeat is only performed if the match fails without).
    '''

    #noinspection PyArgumentList
    def __init__(self, contents=None, lazy=False, **kargs):
        super(LazyMixin, self).__init__(contents=contents, **kargs)
        self.lazy = lazy


class Loop(LazyMixin, LabelMixin, Sequence):
    '''
    A container for a loop (ie. the contents are repeated).
    '''

    def __init__(self, contents=None, parser_state=None, lazy=False,
                 once=False, label=None):
        super(Loop, self).__init__(contents=contents, lazy=lazy, label=label)
        self.once = once

    def join(self, final, parser_state):
        '''Connect to the next node, completing the loop as necessary.'''
        if not super(Loop, self).consumer(False) \
                and not (parser_state.flags & ParserState._UNSAFE):
            self.append(Checkpoint())
        split = Split(self.label, consumes=True)
        inner = super(Loop, self).join(split, parser_state)
        next = [final, inner]
        if not self.lazy:
            next.reverse()
        split.next = next
        if self.once:
            return inner
        else:
            return split

    def consumer(self, lenient):
        '''Does this sequence consume input data?'''
        return self.once


class CountedLoop(LazyMixin, Sequence):
    '''
    A loop with a given range of iterations.
    '''

    def __init__(self, contents, begin, end, parser_state=None, lazy=False):
        super(CountedLoop, self).__init__(contents=contents, lazy=lazy)
        self.begin = begin
        self.end = end
        if end is None and (
                not (self.consumer(False) or (parser_state.flags & ParserState._UNSAFE))):
            self.append(Checkpoint())

    def join(self, final, parser_state):
        '''Connect to the next node, completing the loop as necessary.'''
        count = Repeat(self.begin, self.end, self.lazy)
        inner = super(CountedLoop, self).join(count, parser_state)
        count.next = [final, inner]
        return count

    def consumer(self, lenient):
        '''Does this sequence consume input data?'''
        if not self.begin:
            return False
        else:
            return super(CountedLoop, self).consumer(lenient)


class Alternatives(LabelMixin, BaseCollection):
    '''
    A set of (ordered) alternatives.
    '''

    def __init__(self, contents=None, label='...|...', split=Split):
        super(Alternatives, self).__init__(contents=contents, label=label)
        self.split = split

    def consumer(self, lenient):
        '''Does this sequence consume input data?'''
        for sequence in self.contents:
            if not sequence.consumer(lenient):
                return False
        return True

    def join(self, final, parser_state):
        '''Connect to the next node, completing the loop as necessary.'''
        #noinspection PySimplifyBooleanCheck
        if len(self.contents) == 0:
            return NoMatch().join(final, parser_state)
        elif len(self.contents) == 1:
            return self.contents[0].join(final, parser_state)
        else:
            split = self.split(self.label)
            split.next = list(map(lambda x: x.join(final, parser_state), self.contents))
            return split

    def _assemble(self, final):
        pass


class Optional(LazyMixin, Alternatives):
    '''
    An optional value (or squence, or whatever).
    '''

    def join(self, final, parser_state):
        '''Connect to the next node, completing the loop as necessary.'''
        self.contents.append(Sequence())
        if self.lazy:
            self.contents.reverse()
        return super(Optional, self).join(final, parser_state)

    def consumer(self, lenient):
        '''Does this sequence consume input data?'''
        return False
