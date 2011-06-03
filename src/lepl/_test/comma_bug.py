
from unittest import TestCase
from operator import add, sub, mul, truediv

from lepl import *


def parser():
    
    class Op(List):
        def __float__(self):
            return self._op(float(self[0]), float(self[1]))
    
    class Add(Op): _op = add
    class Sub(Op): _op = sub
    class Mul(Op): _op = mul
    class Div(Op): _op = truediv
    
    class Assign(List): pass
    
    class Eq(List): pass
    class NEq(List): pass
        
    class cGE(List): pass
    class cGT(List): pass
    class cLT(List): pass
    class cLE(List): pass
    class AND(List): pass
    class OR(List): pass
    
    # tokens
    value = Token(UnsignedReal())
    symbol = Token('[^0-9a-zA-Z \t\r\n]')
    
    number = Optional(symbol('-')) + value >> float
    group2, group3 = Delayed(), Delayed()
    
    # first layer, most tightly grouped, is parens and numbers
    parens = ~symbol('(') & group3 & ~symbol(')')
    group1 = parens | number
    
    # second layer, next most tightly grouped, is multiplication
    mul_ = group1 & ~symbol('*') & group2 > Mul
    div_ = group1 & ~symbol('/') & group2 > Div
    group2 += mul_ | div_ | group1
    
    # third layer, least tightly grouped, is addition
    add_ = group2 & ~symbol('+') & group3 > Add
    sub_ = group2 & ~symbol('-') & group3 > Sub
    group3 += add_ | sub_ | group2
    
    #comparison symbols
    NEQ=symbol("!") & symbol("=")
    EQ= symbol("=") & symbol("=")
    GT= symbol(">")
    GE= symbol(">") & symbol("=")
    LT= symbol("<")
    LE= symbol("<") & symbol("&")
    
    #syntactical symbols
    lparens = symbol('(')
    rparens = symbol(')')
    ifsym   = symbol('~') 
    lcurly = symbol('{')
    rcurly = symbol('}')
    
    #more syntax symbols
    SPACES = ~Star(Space())
    identifier = Token("[a-zA-Z_]+") #>variable_control
    EOL = symbol(';')
    
    #handles argument, karg lists
    comma  = ~symbol(',') 
    none   = Token('None')                        >> (lambda x: None)
    bool   = (Token('T') | Token('F'))   >> (lambda x: x == 'T')
    ident  = Token("[a-zA-Z]+\|[a-zA-Z]+[0-9]")[1:]
    allchars = Token(r"[a-zA-Z0-9]")[:]#\.,<>/\?;:'\]\[\{\}\|=\+-\(\)\*&\^%\$#@!~\\t\\r\\n ]") 
    
    str_   = (symbol('"') & allchars & symbol('"') | symbol("'") & allchars & symbol("'")) > str
    item   = str_ | number | none | bool | ident       
    #with Separator(~Regexp(r'\s*')):
    value2  = Delayed()
    list_  = ~symbol('[') & value2[:, comma] & ~symbol(']') > list
    tuple_ = ~symbol('(') & value2[:, comma] & ~symbol(')') > tuple
    value2 += list_ | tuple_ | item  
    arg    = value2                                  >> 'arg'
    #karg   = ((ident & ~symbol('=') & value2)            > tuple) >> 'karg'
    arg_expr   = (arg)[:, comma] & Eos()    > Node
    
    #recursion needed
    expr = Delayed()
    
    #boolean expressions
    bool_expr = Or(
        expr & ~symbol('&') & expr > AND,
        expr & ~symbol('?') & expr > OR
        )
        
    #handles other compares
    ot_expr = Or(
        bool_expr,
        expr & ~GT & expr > cGT,
        expr & ~GE & expr > cGE,
        expr & ~LT & expr > cLT,
        expr & ~LE & expr > cLE
        )
    #handles equality expressions
    eq_expr = Or(
        ot_expr,
        expr & ~EQ & expr > Eq,
        expr & ~NEQ & expr > NEq
        )
        
    #renames all the sub_expr types to be cond
    cond = eq_expr
    
    #function calls: func(a, b=10)
    funccall = ident & ~lparens / arg_expr / ~rparens
    
    #finally define expr
    expr += number | identifier | str_ | funccall | group3 | eq_expr  
    
    #assignment statement
    stmt = identifier & ~symbol('=') & expr & ~EOL > Assign

    return (group3, stmt, arg_expr)


class CommaTest(TestCase):
    
    def test_group3(self):
        (group3, _, _) = parser()
        ast = group3.parse('1+2*(3-4)+5/6+7')[0]
        assert str(ast) == '''Add
 +- 1.0
 `- Add
     +- Mul
     |   +- 2.0
     |   `- Sub
     |       +- 3.0
     |       `- 4.0
     `- Add
         +- Div
         |   +- 5.0
         |   `- 6.0
         `- 7.0''', str(ast)
         
    def test_stmt(self):
        (_, stmt, _) = parser()
        ast = stmt.parse("a=1+2*(3-4)+5/6+7;")[0]
        assert str(ast) == '''Assign
 +- 'a'
 `- Add
     +- 1.0
     `- Add
         +- Mul
         |   +- 2.0
         |   `- Sub
         |       +- 3.0
         |       `- 4.0
         `- Add
             +- Div
             |   +- 5.0
             |   `- 6.0
             `- 7.0''', str(ast)

    def test_arg_expr(self):
        (_, _, arg_expr) = parser()
        ast = arg_expr.parse("1,2")[0]
        assert str(ast) == '''Node
 +- arg 1.0
 `- arg 2.0''', str(ast)
    
##########################################
#test code
##########################################    
#ast = group3.parse('1+2*(3-4)+5/6+7')[0]
#print(ast)
#stmt.config.auto_memoize()
#ast= stmt.parse("a=1+2*(3-4)+5/6+7;")[0]
#print(ast)
#ast = stmt.parse("a=b<10;")[0]
#print(ast)
#arg_expr.config.no_full_first_match()
#
#ast = arg_expr.parse_all("1,2")
#print(list(ast))
#for i in ast:
#    print i
    