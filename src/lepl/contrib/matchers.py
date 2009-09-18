
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

from lepl.functions import Optional
from lepl.matchers import And, Or, _BaseSearch, Transform
from lepl.operators import _BaseSeparator


# (c) 2009 "mereandor" / mereandor at gmail dot com (Roman), Andrew Cooke

# pylint: disable-msg=R0903
class SmartSeparator2(_BaseSeparator):
    '''
    A substitute `Separator` with different semantics for optional matchers.
    This identifies optional matchers by type (whether they subclass 
    `_BaseSearch`) and then constructs a replacement that adds space only
    when both matchers are used.
    
    See also `SmartSeparator1`, which is more general but less efficient.
    '''
    
    def _replacements(self, separator):
        '''
        Provide alternative definitions of '&` and `[]`.
        '''
        
        def non_optional_copy(matcher):
            '''
            Check whether a matcher is optional and, if so, make it not so.
            '''
            # both of the "copy" calls below make me nervous - it's not the
            # way the rest of lepl works - but i don't have any specific
            # criticism, or a good alternative.
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

        # pylint: disable-msg=W0141
        def and_(matcher_a, matcher_b):
            '''
            Combine two matchers.
            '''
            (requireda, optionala) = non_optional_copy(matcher_a)
            (requiredb, optionalb) = non_optional_copy(matcher_b)
          
            if not (optionala or optionalb):
                return And(matcher_a, separator, matcher_b)
            else:
                matcher = Or(
                    *filter((lambda x: x is not None), [
                        And(Optional(And(requireda, separator)), requiredb) 
                            if optionala else None,
                        And(requireda, Optional(And(separator, requiredb))) 
                            if optionalb else None]))
                if optionala and optionalb:
                    # making this explicit allows chaining (we can detect it
                    # when called again in a tree of "ands")
                    matcher = Optional(matcher)
                return matcher
        return (and_, self._repeat(separator))
    
