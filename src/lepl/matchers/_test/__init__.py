
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
Tests for the lepl.matchers package.
'''

from sys import version

# we need to import all files used in the automated self-test

# pylint: disable-msg=E0611
#@PydevCodeAnalysisIgnore
import lepl.matchers._test.combine
import lepl.matchers._test.core
import lepl.matchers._test.derived
import lepl.matchers._test.error
import lepl.matchers._test.memo
import lepl.matchers._test.operators
import lepl.matchers._test.separators
if version[0] == '2':
    import lepl.matchers._test.support
else:
    import lepl.matchers._test.support3
import lepl.matchers._test.variables
