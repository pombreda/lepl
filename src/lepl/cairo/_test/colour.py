
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
Test the Colour class.
'''

from unittest import TestCase

from lepl.cairo.colour import Colour, RED, GREEN, BLUE, WHITE, BLACK


class ColourTest(TestCase):
    '''
    Check that the Colour class behaves OK. 
    '''
    
    def test_constructor(self):
        '''
        Test clipping with pre-multiplication of alpha.
        '''
        red = Colour(1, 0, 0)
        assert red.rgb() == (1, 0, 0)
        green = Colour(0, 2, 0)
        assert green.rgb() == (0, 1, 0)
        half_blue = Colour(0, 0, 1, 0.5)
        assert half_blue.rgb() == (0, 0, 0.5)
        black = Colour(-1, -1, -1)
        assert black.rgb() == (0, 0, 0)
    
    def test_multiplication(self):
        assert RED * 0.5 == Colour(0.5, 0, 0, 1)
        assert GREEN * (1, 0.5) == Colour(0, 0.5, 0, 0.5)
    
