
# Copyright 2010 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Display information when matchers that are bound to variables are called.

This is possible thanks to a neat trick suggested by Carl Banks on c.l.p 
'''

from __future__ import generators, print_function
from contextlib import contextmanager
from sys import stderr, _getframe

from lepl.matchers.support import trampoline_matcher_factory
from lepl.support.lib import format, str


@trampoline_matcher_factory(False)
def NamedResult(name, matcher, out=stderr):
    
    def format_stream(stream):
        text = str(stream)
        if len(text) > 20:
            text = text[:17] + '...'
        return text
    
    def record_success(count, stream_in, result):
        (value, stream_out) = result
        count_desc = format(' ({0})', count) if count > 1 else ''
        # Python bug #4618
        print(format('{0}{1} = {2}\n    "{3}" -> "{4}"', 
                     name, count_desc, value, 
                     format_stream(stream_in), format_stream(stream_out)), 
              file=out, end=str('\n'))
        
    def record_failure(count, stream_in):
        # Python bug #4618
        print(format('! {0} (after {1} matches)\n    "{2}"', name, count, 
                     format_stream(stream_in)),
              file=out, end=str('\n'))
    
    def match(support, stream):
        count = 0
        generator = matcher._match(stream)
        try:
            while True:
                value = yield generator
                count += 1
                record_success(count, stream, value)
                yield value
        except StopIteration:
            record_failure(count, stream)

    return match


def _adjust(text, width, pad=False, left=False):
    if len(text) > width:
        text = text[:width-3] + '...'
    if pad and len(text) < width:
        space = ' ' * (width - len(text))
        if left:
            text = space + text
        else:
            text = text + space
    return text


def name(name, show_failures=True, width=80, out=stderr):
    
    left = 3 * width // 5 - 1
    right = 2 * width // 5 - 1
    
    def namer(stream_in, matcher):
        try:
            (result, stream_out) = matcher()
            stream = _adjust(format('stream = \'{0}\'', stream_out), right) 
            str_name = _adjust(name, left // 4, True, True)
            match = _adjust(format(' {0} = {1}', str_name, result),
                            left, True)
            # Python bug #4618
            print(match + ' ' + stream, file=out, end=str('\n'))
            return (result, stream_out)
        except StopIteration:
            if show_failures:
                stream = _adjust(format('stream = \'{0}\'', stream_in), right) 
                str_name = _adjust(name, left // 4, True, True)
                match = _adjust(format(' {0} failed', str_name), left, True)
                # Python bug #4618
                print(match + ' ' + stream, file=out, end=str('\n'))
            raise StopIteration
        
    return namer


@contextmanager
def TraceVariables(on=True, show_failures=True, width=80, out=stderr):
    before = _getframe(2).f_locals.copy()
    yield None
    after = _getframe(2).f_locals
    warned = False
    for key in after:
        value = after[key]
        if on and key not in before or value != before[key]:
            try:
                value.wrapper.append(name(key, show_failures, width, out))
            except:
                if not warned:
                    # Python bug #4618
                    print('Unfortunately the following matchers cannot '
                          'be tracked:', end=str('\n'))
                    warned = True
                # Python bug #4618
                print(format('  {0} = {1}', key, value), end=str('\n'))
                    


