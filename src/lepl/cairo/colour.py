
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
Provide some short-hand colour definitions for cairo.

As far as I can tell, cairo uses pre-multiplied alpha -
http://en.wikipedia.org/wiki/Alpha_compositing
'''


from collections import namedtuple
from operator import itemgetter


def _replace(index):
    def setter(self, value):
        args = list(self)
        args[index] = value
        return Colour(*args)
    return setter


class Colour(namedtuple('BaseColour', 'r g b a')):
    
    def __new__(cls, r, g, b, a=1.0):
        a = min(1, max(0, a))
        r = min(a, max(0, r))
        g = min(a, max(0, g))
        b = min(a, max(0, b))
        return super(Colour, cls).__new__(cls, r, g, b, a)
    
    r = property(itemgetter(0), _replace(0)) 
    g = property(itemgetter(1), _replace(1)) 
    b = property(itemgetter(2), _replace(2)) 
    a = property(itemgetter(3), _replace(3)) 
    
    @staticmethod
    def from_rgb(rgb):
        return Colour(rgb[0], rgb[1], rgb[2], 1.0)
    
    def rgb(self):
        '''
        Convert to an RGB triplet (alpha is not removed).
        '''
        return (self.r, self.g, self.b)
    
    def __mul__(self, factor):
        '''
        Scale the colour by some factor.
        
        If factor is a single value, it is applied only to the RGB components;
        if it is a pair then the second value is applied to alpha (and
        folded in to RGB too).  So 0.5 would reduce RGB by half; (1, 0.5)
        would reduce alpha by half (and scale RGB correspondingly); (0.5, 0.5)
        would scale RGB *and* reduce alpha (so pre-multiplied RGB would be 
        numerically scaled by 0.25).
        
        After scaling, values are clipped within (0, 1).
        '''
        r, g, b, a = self
        try:
            frgb, fa = factor
            frgb *= fa # pre-multiply
            r *= frgb
            g *= frgb
            b *= frgb
            a *= fa
        except TypeError:
            r *= factor
            g *= factor
            b *= factor
        return Colour(r, g, b, a)
    
    def opaque(self):
        '''
        The same colour, but with alpha forced to 1.
        '''
        return Colour(self.r / self.a, self.g / self.a, self.b / self.a)
    
    def __add__(self, colour):
        '''
        Overlay colours following normal composition (right on top).
        '''
        fa = 1 - colour.a
        r = colour.r + self.r * fa
        g = colour.g + self.g * fa
        b = colour.b + self.b * fa
        a = colour.a + self.a * fa
        return Colour(r, g, b, a)
    

BLACK = Colour(0, 0, 0)
RED = Colour(1, 0, 0)
GREEN = Colour(0, 1, 0)
BLUE = Colour(0, 0, 1)
YELLOW = Colour(1, 1, 0)
CYAN = Colour(0, 1, 1)
MAGENTA = Colour(1, 0, 1)
WHITE = Colour(1, 1, 1)
