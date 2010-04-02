
# The contents of this file are subject to the Mozilla Public License
# (MPL) Version 1.1 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License
# at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#
# The Original Code is LEPL (http://www.acooke.org/lepl)
# The Initial Developer of the Original Code is Andrew Cooke.
# Portions created by the Initial Developer are Copyright (C) 2009-2010
# Andrew Cooke (andrew@acooke.org). All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms
# of the LGPL license (the GNU Lesser General Public License,
# http://www.gnu.org/licenses/lgpl.html), in which case the provisions
# of the LGPL License are applicable instead of those above.
#
# If you wish to allow use of your version of this file only under the
# terms of the LGPL License and not to allow others to use your version
# of this file under the MPL, indicate your decision by deleting the
# provisions above and replace them with the notice and other provisions
# required by the LGPL License.  If you do not delete the provisions
# above, a recipient may use your version of this file under either the
# MPL or the LGPL License.

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
    