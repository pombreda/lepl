
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
# Portions created by the Initial Developer are Copyright (C) 2009-2011
# Andrew Cooke (andrew@acooke.org). All Rights Reserved.
#
# Contributor(s):
# - Luca Dall'Olio / luca.dallolio@gmail.com
# Portions created by the Contributors are Copyright (C) 2011
# The Contributors.  All Rights Reserved.
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

from lepl.matchers.core import Delayed, Any, Literal
from lepl.matchers.derived import Drop, Optional, ZeroOrMore, OneOrMore, \
    Apply, Digit, Name, Upper, Lower, Integer, Whitespace
from lepl.matchers.combine import And, Or
from lepl.lexer.matchers import Token
import string
from lepl.lexer.lines.matchers import LineEnd

# http://www.antlr.org/grammar/ANTLR/ANTLRv3.g

# Tokens
EOL = Drop(LineEnd()) # $
LITERAL_VALUE = Token(Any(string.letters + string.digits + string.punctuation.translate(None, "\"'\\")))
XDIGIT = Token('[0-9a-fA-F]')
INT = Token(Integer())
ESC = Token(Literal('\\')) & (Token(Literal('n')) | Token(Literal('r')) | Token(Literal('t')) | Token(Literal('b')) | Token(Literal('f')) | Token(Literal('"')) | Token(Literal("'")) | Token(Literal('\\')) | Token(Literal('>')) | (Token(Literal('u')) & XDIGIT & XDIGIT & XDIGIT & XDIGIT))
LITERAL_CHAR = ESC | LITERAL_VALUE
CHAR_LITERAL = Drop(Token(Literal("'"))) & LITERAL_CHAR & Drop(Token(Literal("'")))
STRING_LITERAL = Drop(Token(Literal('"'))) & (LITERAL_CHAR + ZeroOrMore(LITERAL_CHAR)) & Drop(Token(Literal('"')))
DOUBLE_QUOTE_STRING_LITERAL = Token(Literal('"')) & ZeroOrMore(LITERAL_CHAR) & Token(Literal('"'))
DOUBLE_ANGLE_STRING_LITERAL = Token(Literal('+=')) & ZeroOrMore(Token(Any())) & Token(Literal('>>'))
TOKEN_REF = Token(Upper()) + ZeroOrMore(Token(Lower()) | Token(Upper()) | Token(Literal('_')) | Token(Digit()))
RULE_REF = Token(Lower()) + ZeroOrMore(Token(Lower()) | Token(Lower()) | Token(Literal('_')) | Token(Digit()))
ACTION_ESC = (Drop(Token(Literal("\\"))) & Drop(Token(Literal("'")))) | Drop(Token(Literal('\\"'))) | Drop(Token(Literal('\\'))) & LITERAL_VALUE
ACTION_CHAR_LITERAL = Drop(Token(Literal("'"))) & (ACTION_ESC | LITERAL_VALUE) & Drop(Token(Literal("'")))
ACTION_STRING_LITERAL = Drop(Token(Literal('"'))) & ZeroOrMore(ACTION_ESC | LITERAL_VALUE) & Drop(Token(Literal('"')))
SRC = Drop(Token(Literal('src'))) & Name(ACTION_STRING_LITERAL, "file") & Name(INT, "line")
SL_COMMENT = Optional(Token(Literal('TODO SL_COMMENT TODO'))) #Drop(Token(Literal('//'))) & Drop(Token(Literal(' $ANTLR '))) & SRC | ZeroOrMore(AnyBut(EOL) & Word(Printable())) & EOL
ML_COMMENT = Optional(Token(Literal('TODO ML_COMMENT TODO'))) # don't know how to implement this...
WS = Drop(OneOrMore(Token(Whitespace())))
WS_LOOP = ZeroOrMore(SL_COMMENT | ML_COMMENT | WS)
NESTED_ARG_ACTION = Delayed()
NESTED_ARG_ACTION += Drop(Token(Literal('['))) & ZeroOrMore(NESTED_ARG_ACTION | ACTION_STRING_LITERAL | ACTION_CHAR_LITERAL) & Drop(Token(Literal(']')))
ARG_ACTION = NESTED_ARG_ACTION
NESTED_ACTION = Delayed()
NESTED_ACTION += Drop(Token(Literal('{'))) & ZeroOrMore(NESTED_ACTION | SL_COMMENT | ML_COMMENT | ACTION_STRING_LITERAL | ACTION_CHAR_LITERAL) & Drop(Token(Literal('}')))
ACTION = NESTED_ACTION & Optional(Token(Literal('?')))
SCOPE = Drop(Token(Literal('scope')))
OPTIONS = Drop(Token(Literal('options'))) & Drop(Token(Literal('{')))#& WS_LOOP & Drop(Token(Literal('{')))
TOKENS = Drop(Token(Literal('tokens'))) & Drop(Token(Literal('{')))#& WS_LOOP & Drop(Token(Literal('{')))
FRAGMENT = Token(Literal('fragment'))
TREE_BEGIN = Drop(Token(Literal('^(')))
ROOT = Drop(Token(Literal('^')))
BANG = Drop(Token(Literal('!')))
RANGE = Drop(Token(Literal('..')))
REWRITE = Drop(Token(Literal('->')))

# General Parser Definitions

id = TOKEN_REF | RULE_REF

# Grammar heading
optionValue = id | STRING_LITERAL | CHAR_LITERAL | INT | Name(Token(Literal('*')), 's')

option = Apply(Name(id, "id") & Drop(Token(Literal('='))) & Name(optionValue, "value"), dict)
optionsSpec = OPTIONS & Name(Apply(OneOrMore(option & Drop(Token(Literal(';')))), list), "options") & Drop(Token(Literal('}')))
tokenSpec = Apply(Name(TOKEN_REF, "token_ref") & (Drop(Token(Literal('='))) & Name(STRING_LITERAL | CHAR_LITERAL, "lit")), dict) & Drop(Token(Literal(';')))
tokensSpec = TOKENS & Name(Apply(OneOrMore(tokenSpec), list), "tokens") & Drop(Token(Literal('}')))
attrScope = Drop(Token(Literal('scope'))) & id & ACTION
grammarType = Token(Literal('lexer')) & Token(Literal('parser')) & Token(Literal('tree'))
actionScopeName = id | Name(Token(Literal('lexer')), "l") | Name(Token(Literal('parser')), "p")
action = Drop(Token(Literal('@'))) & Optional(actionScopeName & Drop(Token(Literal('::')))) & id & ACTION

grammarHeading = Optional(Name(ML_COMMENT, "ML_COMMENT")) & Optional(grammarType) & Drop(Token(Literal('grammar'))) & Name(id, "grammarName") & Drop(Token(Literal(';'))) & Optional(optionsSpec) & Optional(tokensSpec) & ZeroOrMore(attrScope) & ZeroOrMore(action)

modifier = Token(Literal('protected')) | Token(Literal('public')) | Token(Literal('private')) | Token(Literal('fragment'))
ruleAction = Drop(Token(Literal('@'))) & id & ACTION
throwsSpec = Drop(Token(Literal('throws'))) & id & ZeroOrMore(Drop(Token(Literal(','))) & id)
ruleScopeSpec = (Drop(Token(Literal('scope'))) & ACTION) | (Drop(Token(Literal('scope'))) & id & ZeroOrMore(Drop(Token(Literal(','))) & id) & Drop(Token(Literal(';')))) | (Drop(Token(Literal('scope'))) & ACTION & Drop(Token(Literal('scope'))) & id & ZeroOrMore(Drop(Token(Literal(','))) & id) & Drop(Token(Literal(';'))))
notTerminal = CHAR_LITERAL | TOKEN_REF | STRING_LITERAL
terminal = (CHAR_LITERAL | TOKEN_REF & Optional(ARG_ACTION) | STRING_LITERAL | Token(Literal('.'))) & Optional(Token(Literal('^')) | Token(Literal('!')))
block = Delayed()
notSet = Drop(Token(Literal('~'))) & (notTerminal | block)
range_ = Name(CHAR_LITERAL, "c1") & RANGE & Name(CHAR_LITERAL, "c2")
atom = Apply(range_ & Name(Optional(Token(Literal('^')) | Token(Literal('!'))), "op"), dict) | terminal | (notSet & Name(Optional(Token(Literal('^')) | Token(Literal('!'))), "op")) | (RULE_REF & Optional(Name(ARG_ACTION, "arg")) & Name(Optional(Token(Literal('^')) | Token(Literal('!'))), "op"))
element = Delayed()
treeSpec = Drop(Token(Literal('^('))) & element & OneOrMore(element) & Drop(Token(Literal(')')))
ebnf = Name(block, "block") & Optional(Name(Token(Literal('?')), "op") | Name(Token(Literal('*')), "op") | Name(Token(Literal('+')), "op") | Token(Literal('=>')))
ebnfSuffix = Token(Literal('?')) | Token(Literal('*')) | Token(Literal('&'))
elementNoOptionSpec = (Name(id, "result_name") & Name((Token(Literal('=')) | Token(Literal('&='))), "labelOp") & Name(atom, "atom") & Optional(ebnfSuffix)) | (Name(id, "result_name") & Name((Token(Literal('=')) | Token(Literal('&='))), "labelOp") & block & Optional(ebnfSuffix)) | Name(atom, "atom") & Optional(ebnfSuffix) | ebnf | ACTION | (treeSpec & Optional(ebnfSuffix)) # |   SEMPRED ( '=>' -> GATED_SEMPRED | -> SEMPRED )
element += Apply(elementNoOptionSpec, dict)
alternative = Apply(OneOrMore(element), list)
rewrite = Optional(Token(Literal('TODO REWRITE RULES TODO')))
block += Apply(Drop(Token(Literal('('))) & Optional(Optional(Name(optionsSpec, "opts")) & Drop(Token(Literal(':')))) & Name(alternative, 'a1') & rewrite & Name(Apply(ZeroOrMore(Drop(Token(Literal('|'))) & alternative & rewrite), list), "alternatives") & Drop(Token(Literal(')'))), dict)
altList = Name(alternative, 'a1') & rewrite & Name(Apply(ZeroOrMore(Drop(Token(Literal('|'))) & alternative & rewrite), list), "alternatives")
exceptionHandler = Drop(Token(Literal('catch'))) & ARG_ACTION & ACTION
finallyClause = Drop(Token(Literal('finally'))) & ACTION
exceptionGroup = (OneOrMore(exceptionHandler) & Optional(finallyClause)) | finallyClause

ruleHeading = Name(Optional(ML_COMMENT), "ruleComment") & Name(Optional(modifier), "modifier") & Name(id, "ruleName") & Optional(Token(Literal('!'))) & Optional(Name(ARG_ACTION, "arg")) & Optional(Drop(Token(Literal('returns'))) & Name(ARG_ACTION, "rt")) & Optional(throwsSpec) & Optional(optionsSpec) & Optional(ruleScopeSpec) & ZeroOrMore(ruleAction)
rule = Apply(ruleHeading & Drop(Token(Literal(':'))) & altList & Drop(Token(Literal(';'))) & Optional(exceptionGroup), dict)

grammarDef = Apply(grammarHeading & Name(Apply(OneOrMore(rule), list), "rules"), dict)

def grammar():
    return grammarDef

def __antlrAlternativesConverter(leplRules, antlrBlock):
    rule = None
    if 'alternatives' in antlrBlock and antlrBlock['alternatives'] != '' and len(antlrBlock['alternatives']) > 0:
        alternatives = []
        alternatives.append(__antlrAlternativeConverter(leplRules, antlrBlock['a1']))
        for alternative in antlrBlock['alternatives']:
            alternatives.append(__antlrAlternativeConverter(leplRules, alternative))
        rule = Name(Apply(Or(*alternatives), dict), "anonymous_or")
    elif 'a1' in antlrBlock and antlrBlock['a1'] != '':
        rule = __antlrAlternativeConverter(leplRules, antlrBlock['a1'])
    else:
        raise NotImplementedError('Not yet implemented')
    assert rule != None
    return rule

def __antlrAlternativeConverter(leplRules, antlrAlternative):
    elementList = []
    for element in antlrAlternative:
        rule = None
        if 'atom' in element and 'c1' in element['atom'] and element['atom']['c1'] != '':
            regex = r'[' + str(element['atom']['c1'][0]) + '-' + str(element['atom']['c2'][0] + ']')
            rule = Name(Token(regex), "anonymous_regex")
        elif 'block' in element and element['block'] != '':
            rule = __antlrAlternativesConverter(leplRules, element['block'])
        else:
            ruleRef = element['atom']
            assert ruleRef in leplRules
            rule = Name(leplRules[element['atom']], element['atom'])
        if 'op' in element and element['op'] != '':
            if element['op'] == '+':
                rule = Name(Apply(OneOrMore(rule), list), "anonymous_one_or_more")
            elif element['op'] == '*':
                rule = Name(Apply(ZeroOrMore(rule), list), "anonymous_zero_or_more")
            elif element['op'] == '?':
                rule = Name(Optional(rule), "anonymous_zero_or_one")
            else:
                raise NotImplementedError('rule operator not yet implemented : ' & element['op'])
        elementList.append(rule)
    if len(elementList) > 1:
        rule = Name(Apply(And(*elementList), dict), "anonymous_and")
    else:
        rule = elementList[0]
    assert rule != None
    return rule

def __antlrRuleConverter(leplRules, antlrRule):
    rule = None
    rule = __antlrAlternativesConverter(leplRules, antlrRule)
    assert rule != None
    Name(rule, antlrRule['ruleName'])
    return rule

def antlrConverter(antlrGrammarTree):
    leplRules = {}
    antlrTokens = {}
    for antlrToken in antlrGrammarTree[0]['tokens']:
        antlrTokens[antlrToken['token_ref']] = antlrToken['lit']
    for antlrTokenName, antlrToken in antlrTokens.items():
        leplRules[antlrTokenName] = Name(Token(Literal(antlrToken)), antlrTokenName)
    antlrRules = {}
    for antlrRule in antlrGrammarTree[0]['rules']:
        antlrRules[antlrRule['ruleName']] = antlrRule
        leplRules[antlrRule['ruleName']] = Delayed() # antlr is a top down grammar
    for antlrRuleName, antlrRule in antlrRules.items():
        leplRule = __antlrRuleConverter(leplRules, antlrRule)
        assert leplRule != None
        leplRules[antlrRuleName] += Name(leplRule, antlrRule['ruleName'])
    return leplRules

if __name__ == "__main__":

    text = """grammar SimpleCalc;

options {
    language = Python;
}

tokens {
    PLUS     = '+' ;
    MINUS    = '-' ;
    MULT    = '*' ;
    DIV    = '/' ;
}

expr    : term ( ( PLUS | MINUS )  term )* ;

term    : factor ( ( MULT | DIV ) factor )* ;

factor    : NUMBER ;

NUMBER    : (DIGIT)+ ;

fragment DIGIT    : '0'..'9' ;

"""

    antlrGrammarTree = grammar().parse(text)
    print antlrGrammarTree
    leplRules = antlrConverter(antlrGrammarTree)
    leplRule = leplRules["expr"]
    leplTree = leplRule.parse("2 - 5 * 42 + 7 / 25")
    print leplTree
