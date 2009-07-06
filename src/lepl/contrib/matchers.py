
# Copyright 2009 Andrew Cooke and contributors (see below)

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
Contributed matchers.
'''

from copy import copy

from lepl.functions import Repeat
from lepl.matchers import And, Or, _BaseSearch, Transform
from lepl.operators import _BaseSeparator


class SmartSeparator2(_BaseSeparator):
    '''
    A substitude Separator with different semantics for optional matchers.
    
    (c) 2009 "mereandor" <mereandor@gmail.com> (Roman), Andrew Cooke

    See also `SmartSeparator1`
    '''
    
    def _replacements(self, separator):
        '''
        Provide alternative definitions of '&` and `[]`.
        '''
        
        def non_optional_copy(matcher):
            '''
            Check whether a matcher is optional and, if so, make it not so.
            '''
            required, optional = matcher, False
            if isinstance(matcher, Transform):
                temp, optional = non_optional_copy(matcher.matcher)
                if optional:
                    required = copy(matcher)
                    required.matcher = temp
            elif isinstance(matcher, _BaseSearch):
                optional = (matcher.start == 0)
                if optional:
                    required = copy(matcher)
                    required.start = 1
                    if required.stop == 1:
                        required = required.first
            return required, optional

        def optional(matcher):
            return Repeat(matcher, 0, 1, 'd', None, False)

        def and_(a, b):
            (requireda, optionala) = non_optional_copy(a)
            (requiredb, optionalb) = non_optional_copy(b)
          
            if not (optionala or optionalb):
                return And(a, separator, b)
            else:
                return Or(
                    *filter((lambda x: x is not None), [
                        And(optional(And(requireda, separator)), requiredb) 
                            if optionala else None,
                        And(requireda, optional(And(separator, requiredb))) 
                            if optionalb else None]))

        return (and_, self._repeat(separator))
    
