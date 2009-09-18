
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,R0914
#@PydevCodeAnalysisIgnore
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

#from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class ArgsExample(Example):
    
    def test_args(self):
        #basicConfig(level=DEBUG)
    
        comma  = Drop(',') 
        none   = Literal('None')                        >> (lambda x: None)
        bool   = (Literal('True') | Literal('False'))   >> (lambda x: x == 'True')
        ident  = Word(Letter() | '_', 
                      Letter() | '_' | Digit())
        float_ = Float()                                >> float 
        int_   = Integer()                              >> int
        str_   = String() | String("'")
        item   = str_ | int_ | float_ | none | bool | ident       
        with Separator(~Regexp(r'\s*')):
            value  = Delayed()
            list_  = Drop('[') & value[:, comma] & Drop(']') > list
            tuple_ = Drop('(') & value[:, comma] & Drop(')') > tuple
            value += list_ | tuple_ | item  
            arg    = value                                   >> 'arg'
            karg   = ((ident & Drop('=') & value)            > tuple) >> 'karg'
            expr   = (karg | arg)[:, comma] & Drop(Eos())    > Node
            
        parser = expr.string_parser()
#        ast = parser('True, type=rect, sizes=[3, 4], coords = ([1,2],[3,4])')
#        self.examples([(lambda: ast[0], '''Node
# +- arg True
# +- karg ('type', 'rect')
# +- karg ('sizes', [3, 4])
# `- karg ('coords', ([1, 2], [3, 4]))'''),
#                       (lambda: ast[0].arg, '[True]'),
#                       (lambda: ast[0].karg, 
#                        "[('type', 'rect'), ('sizes', [3, 4]), ('coords', ([1, 2], [3, 4]))]")])
        
        ast = parser('None, str="a string"')
        self.examples([(lambda: ast[0], """Node
 +- arg None
 `- karg ('str', 'a string')"""),
                       (lambda: ast[0].arg, "[None]"),
                       (lambda: ast[0].karg, "[('str', 'a string')]")])
