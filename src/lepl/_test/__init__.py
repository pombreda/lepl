
# Copyright 2009 Andrew Cooke

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
Tests for the lepl package.
'''

from logging import getLogger, basicConfig, DEBUG
from sys import version
from types import ModuleType
from unittest import TestSuite, TestLoader, TextTestRunner

import lepl

# we need to import all files used in the automated self-test

# pylint: disable-msg=E0611, W0401
#@PydevCodeAnalysisIgnore
import lepl._test.bug_stalled_parser
import lepl._test.magus


def all():
    '''
    This runs all tests and examples.  It is something of a compromise - seems
    to be the best solution that's independent of other libraries, doesn't
    use the file system (since code may be in a zip file), and keeps the
    number of required imports to a minimum.
    '''
    #basicConfig(level=DEBUG)
    log = getLogger('lepl._test.all.all')
    suite = TestSuite()
    loader = TestLoader()
    runner = TextTestRunner(verbosity=2)
    for module in ls_all_tests():
        log.debug(module.__name__)
        suite.addTest(loader.loadTestsFromModule(module))
    result = runner.run(suite)
    print('\n\n\n----------------------------------------------------------'
          '------------\n')
    if version[0] == '2':
        print('Expect 5 failures + 1 error in Python 2.6: {0:d}, {1:d} '
              '(lenient comparison, format variation from address size, '
              'unicode ranges, weird string difference)'
              .format(len(result.failures), len(result.errors)))
        assert 5 <= len(result.failures) <= 5, len(result.failures)
        assert 1 <= len(result.errors) <= 1, len(result.errors)
        target = 377 - 25 # no bin/cairo tests
    else:
        print('Expect at most 1 failure + 0 errors in Python 3: {0:d}, {1:d} '
              '(format variations from address size?)'
              .format(len(result.failures), len(result.errors)))
        assert 0 <= len(result.failures) <= 1, len(result.failures)
        assert 0 <= len(result.errors) <= 0, len(result.errors)
        target = 377-3 # no cairo tests (2), no random (1)
    print('Expect {0:d} tests total: {1:d}'.format(target, result.testsRun))
    assert result.testsRun == target, result.testsRun
    print('\nLooks OK to me!\n\n')


def ls_all_tests():
    '''
    All test modules.
    '''
    for root in ls_module(lepl, 
                          ['bin', 'contrib', 'core', 'lexer', 'matchers', 
                           'offside', 'regexp', 'stream', 'support'], 
                          True):
        for child in ls_module(root, ['_test', '_example']):
            for module in ls_module(child):
                yield module


def ls_module(parent, children=None, include_parent=False):
    '''
    Expand and return child modules.
    '''
    if include_parent:
        yield parent
    if not children:
        children = dir(parent)
    for child in children:
        try:
            # pylint: disable-msg=W0122
            exec('import {0}.{1}'.format(parent.__name__, child))
            module = getattr(parent, child, None)
            if isinstance(module, ModuleType):
                yield module
        except ImportError:
            pass


if __name__ == '__main__':
    all()
