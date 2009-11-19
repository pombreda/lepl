
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
Tokens for indents.
'''


from lepl.lexer.matchers import BaseToken
from lepl.offside.monitor import BlockMonitor
from lepl.offside.regexp import START, END
from lepl.parser import tagged
from lepl.support import format


# pylint: disable-msg=R0901, R0904, R0913, E1101
# lepl conventions
class Indent(BaseToken):
    '''
    Match an indent (start of line marker plus spaces and tabs).
    '''
    
    def __init__(self, content=None, id_=None, alphabet=None, complete=True, 
                 compiled=False):
        if id_ is None:
            id_ = START
        super(Indent, self).__init__(content=content, id_=id_, 
                                          alphabet=alphabet, complete=complete, 
                                          compiled=compiled)
        self.regexp = '^[ \t]*'
                
        
class Eol(BaseToken):
    '''
    Match the end of line marker.
    '''
    
    def __init__(self, content=None, id_=None, alphabet=None, complete=True, 
                 compiled=False):
        if id_ is None:
            id_ = END
        super(Eol, self).__init__(content=content, id_=id_, 
                                  alphabet=alphabet, complete=complete, 
                                  compiled=compiled)
        self.regexp = '$'


class BIndent(Indent):
    '''
    Extend `Indent` so that it matches the block indent level.
    
    Content is supported, but checking of matched length happens after
    matching content, so it's probably not that helpful.
    '''
    
    def __init__(self, content=None, id_=None, alphabet=None, complete=True, 
                 compiled=False):
        super(BIndent, self).__init__(content=content, id_=id_, 
                                      alphabet=alphabet, complete=complete, 
                                      compiled=compiled)
        self.monitor_class = BlockMonitor
        self.__current_indent = None
        
    def on_push(self, monitor):
        '''
        Read the global indentation level.
        '''
        self.__current_indent = monitor.indent
        
    def on_pop(self, monitor):
        '''
        Unused
        '''
    
    @tagged
    def _match(self, stream_in):
        '''
        Check that we match the current level
        '''
        try:
            generator = super(BIndent, self)._match(stream_in)
            while True:
                (indent, stream) = yield generator
                if len(indent[0]) == self.__current_indent:
                    yield (indent, stream)
                else:
                    self._debug(
                        format('Incorrect indent ({0:d} != len({1!r}), {2:d})',
                               self.__current_indent, indent[0], 
                               len(indent[0])))
        except StopIteration:
            return


