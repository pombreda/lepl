
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
Initial exploration of cairo.
'''

import cairo

from lepl.cairo.context import cset
from lepl.cairo.colour import WHITE, BLUE, BLACK

    
def spiral():
    
    width, height = 400, 300
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    
    with cset(ctx,
              source_rgb=WHITE,
              operator=cairo.OPERATOR_SOURCE):
        ctx.paint()

    with cset(ctx,
              line_width=0.1,
              source_rgb=BLACK):
        ctx.rectangle(0.25, 0.25, 0.5, 0.5)
        ctx.stroke()
    
    wd = .02 * width
    hd = .02 * height
    width -= 2
    height -= 2

    with cset(ctx, 
              source_rgb=BLUE):
        ctx.move_to(width + 1, 1 - hd)
        for i in range(9):
            ctx.rel_line_to (0, height - hd * (2 * i - 1))
            ctx.rel_line_to (- (width - wd * (2 *i)), 0)
            ctx.rel_line_to (0, - (height - hd * (2*i)))
            ctx.rel_line_to (width - wd * (2 * i + 1), 0)
        ctx.stroke()

    surface.write_to_png('spiral.png')
   

    
if __name__ == '__main__':
    spiral()
    