from __future__ import generators

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

from contextlib import contextmanager
from sys import stderr, _getframe

from lepl.matchers.support import trampoline_matcher_factory
from lepl.core.parser import tagged, GeneratorWrapper
from lepl.support.lib import format


@trampoline_matcher_factory(False)
def NamedResult(name, matcher, out=stderr):
    
    def format_stream(stream):
        text = str(stream)
        if len(text) > 20:
            text = text[:17] + '...'
        return text
    
    def record_success(count, stream_in, result):
        (value, stream_out) = result
        print(format('{0} {1} = {2}\n    "{3}" -> "{4}"', count, name, value, 
                     format_stream(stream_in), format_stream(stream_out)), 
              file=out)
        
    def record_failure(count, stream_in):
        print(format('! {0} (after {1} matches)\n    "{2}"', name, count, 
                     format_stream(stream_in)),
              file=out)
    
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


@contextmanager
def log_these_variables():
    before = _getframe(2).f_locals.copy()
    x = _getframe(2).f_globals.copy()
    yield None
    after = _getframe(2).f_locals
    y = _getframe(2).f_globals
    originals = {}
    for key in after:
        value = after[key]
        if key not in before or value != before[key]:
            # unwrap anything that has already been wrapped
            if value in originals:
                value = originals[value]
            wrapped = NamedResult(key, value)
            originals[wrapped] = value
            print(repr(wrapped))
            _getframe(2).f_locals[key] = wrapped
            

