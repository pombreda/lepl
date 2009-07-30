
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
Provide a with-context syntax for cairo.
'''

class cset(object):
    '''
    Allow automatic scoping of the given parameters.
    '''
    
    def __init__(self,
                 ctx,
                 line_width=None,
                 operator=None, 
                 source_rgb=None
                 ):
        self.__ctx = ctx
        self.__line_width = line_width
        self.__operator = operator
        self.__source_rgb = source_rgb
        
    def __enter__(self):
        self.__ctx.save()
        if self.__line_width is not None:
            self.__ctx.set_line_width(self.__line_width)
        if self.__operator is not None:
            self.__ctx.set_operator(self.__operator)
        if self.__source_rgb is not None:
            self.__ctx.set_source_rgb(*self.__source_rgb)
    
    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.__ctx.restore()
    
    