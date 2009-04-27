
from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class ArgsExample(Example):
    
    def test_args(self):
        basicConfig(level=DEBUG)
    
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
            karg   = (ident & Drop('=') & value              > tuple) >> 'karg'
            expr   = (karg | arg)[:, comma] & Drop(Eos())    > Node
            
        parser = expr.string_parser()
        ast = parser('True, type=rect, sizes=[3, 4], coords = ([1,2],[3,4])')
        self.examples([(lambda: ast[0], '''Node
 +- arg True
 +- karg ('type', 'rect')
 +- karg ('sizes', [3, 4])
 `- karg ('coords', ([1, 2], [3, 4]))'''),
                       (lambda: ast[0].arg, '[True]'),
                       (lambda: ast[0].karg, 
                        "[('type', 'rect'), ('sizes', [3, 4]), ('coords', ([1, 2], [3, 4]))]")])
        
        ast = parser('None, str="a string"')
        self.examples([(lambda: ast[0], """Node
 +- arg None
 `- karg ('str', 'a string')"""),
                       (lambda: ast[0].arg, "[None]"),
                       (lambda: ast[0].karg, "[('str', 'a string')]")])
