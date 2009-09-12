
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
Support for offisde and line-aware parsing.
'''


class LineAwareError(Exception):
    '''
    The exception raised by problems in line-aware code (functionality that
    flags or detects markers for the start and end of lines).
    '''


class OffsideError(Exception):
    '''
    The exception raised by problems when parsing whitespace significant
    code.
    '''
