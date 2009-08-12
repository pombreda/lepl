
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
Support the "offside rule" by generating tokens for indent and dedent (which
can be treated like open and close parentheses, for example).

We add this by doing the following:
- Preprocessing the input stream (of text) to include a start of line marker
- Extending the given alphabet to include the start of line marker
- Providing Indent and Dedent token classes (which are not actually used in
  the matching part of the tokenizer)
- Adding a "hidden" token StartOfLine, that matches start of line
- Postprocessing the output stream (of tokens) to convert StartOfLine tokens
  to Indent, Dedent, or nothing (ie silently dropped) depending on relative
  indent.
  
NOTE - ALSO NEED TO WORRY ABOUT PARENS (SEE DISCUSSION ON GROUPS)
'''
