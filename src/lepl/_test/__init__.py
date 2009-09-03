
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

import lepl._test.bug_stalled_parser
import lepl._test.error
import lepl._test.functions
import lepl._test.graph
import lepl._test.manager
import lepl._test.matchers
import lepl._test.memo
import lepl._test.node
import lepl._test.operators
import lepl._test.parser
import lepl._test.rewriters
import lepl._test.separators
import lepl._test.stream
import lepl._test.support


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
        print('Expect 21-22 failures in Python 2.6: {0:d}'
              .format(len(result.failures)))
        assert 21 <= len(result.failures) <= 22, len(result.failures)
        target = 211 # no bin/cairo tests
    else:
        print('Expect at most 1 failure in Python 3: {0:d} '
              '(format variations from address size?)'
              .format(len(result.failures)))
        assert len(result.failures) <= 1, len(result.failures)
        target = 233 # no cairo tests
    print('Expect {0:d} tests total: {0:d}'.format(target, result.testsRun))
    assert result.testsRun == target, result.testsRun
    print('\nLooks OK to me!\n\n')


def ls_all_tests():
    '''
    All test modules.
    '''
    for root in ls(lepl, ['bin', 'contrib', 'lexer', 'regexp'], True):
        for child in ls(root, ['_test', '_example']):
            for module in ls(child):
                yield module


def ls(parent, children=None, include_parent=False):
    '''
    Expand and return child modules.
    '''
    if include_parent:
        yield parent
    if not children:
        children = dir(parent)
    for child in children:
        try:
            exec('import {0}.{1}'.format(parent.__name__, child))
            module = getattr(parent, child, None)
            if isinstance(module, ModuleType):
                yield module
        except ImportError:
            pass


if __name__ == '__main__':
    all()
