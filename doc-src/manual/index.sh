#!/bin/bash

# replace 
#   ``foo()``
# with a link to foo
#   `foo() <api/redirect.html#lepl.foo>`_

#sed -i -r 's/``(Delayed|Literal|Columns|And|Or|Any|OperatorMatcher)\(\)``/`\1() <api\/redirect.html#lepl.matchers.\1>`_/g' *.rst
#sed -i -r 's/``(Letter|Digit|Rexgexp|args|SkipTo|SignedFloat|Literal|Drop|Star|Space|Eos)\(\)``/`\1() <api\/redirect.html#lepl.functions.\1>`_/g' *.rst
#sed -i -r 's/``(Node)\(\)``/`\1() <api\/redirect.html#lepl.node.\1>`_/g' *.rst
#sed -i -r 's/``(Separator|SmartSeparator1)\(\)``/`\1() <api\/redirect.html#lepl.operators.\1>`_/g' *.rst
#sed -i -r 's/``(TraceResults)\(\)``/`\1() <api\/redirect.html#lepl.trace.\1>`_/g' *.rst
#sed -i -r 's/``(SmartSeparator2)\(\)``/`\1() <api\/redirect.html#lepl.contrib.matchers.\1>`_/g' *.rst
#sed -i -r 's/``(Token)\(\)``/`\1() <api\/redirect.html#lepl.lexer.matchers.\1>`_/g' *.rst
#sed -i -r 's/``(BitString|Int)\(\)``/`\1() <api\/redirect.html#lepl.bin.bits.\1>`_/g' *.rst
#sed -i -r 's/``(Const|BEnd|LEnd)\(\)``/`\1() <api\/redirect.html#lepl.bin.matchers.\1>`_/g' *.rst
#sed -i -r 's/``(Configuration)\(\)``/`\1() <api\/redirect.html#lepl.config.\1>`_/g' *.rst
#sed -i -r 's/``(DfaRegexp|NfaRegexp)\(\)``/`\1() <api\/redirect.html#lepl.regexp.matchers.\1>`_/g' *.rst
#sed -i -r 's/``(Line|Block|BLine|ContinuedLineFactory|ContinuedBLineFactory|Extend|SOL|EOL)\(\)``/`\1() <api\/redirect.html#lepl.offside.matchers.\1>`_/g' *.rst
#sed -i -r 's/``(Indent|Eol|BIndent)\(\)``/`\1() <api\/redirect.html#lepl.offside.lexer.\1>`_/g' *.rst
#sed -i -r 's/``(LineAwareConfiguration|IndentConfiguration|OffsideConfiguration)\(\)``/`\1() <api\/redirect.html#lepl.offside.config.\1>`_/g' *.rst

# fix up old errors
#sed -i -e 's/redirect\/html/redirect.html/g' *.rst
#sed -i -r 's/matchers\.(AnyBut|Optional|Star|ZeroOrMore|Plus|OneOrMore|Map|Add|Substitute|Name|Eos|Identity|Newline|Space|Whitespace|Digit|Letter|Upper|Lower|Printable|Punctuation|UnsignedInteger|SignedInteger|Integer|UnsignedFloat|SignedFloat|SignedEFloat|Float|Word|String||Drop)/functions.\1/g' *.rst
#sed -i -r 's/functions\.(And|Or|Literal|Columns|Lookahead|Commit|Delayed|Empty|Eof|First|Regexp|Trace)/matchers.\1/g' *.rst
#sed -i -r 's/lepl\.contrib\.functions\.SmartSeparator2/lepl.contrib.matchers.SmartSeparator2/g' *.rst
#sed -i -r 's/lepl\.offside\.matchers\.(LineAwareConfiguration|IndentConfiguration|OffsideConfiguration)/lepl.offside.config.\1/g' *.rst
#sed -i -r 's/lepl\.bin\.config\.(Configuration)/lepl.config.\1/g' *.rst
#sed -i -r 's/lepl\.lexer\.matchers\.(Indent|Eol|BIndent)/lepl.offside.lexer.\1/g' *.rst


sed -i -r 's/LEPL/Lepl/g' *.rst


# lepl 4 fixes
sed -i -r 's/lepl\.(Word|Integer)/lepl.matchers.derived.\1/g' *.rst
sed -i -r 's/lepl\.(And|Or)/lepl.matchers.combine.\1/g' *.rst
sed -i -r 's/lepl\.(functions|matchers)\.(SignedFloat|Drop|Space|Star|Optional|Letter|Digit|args|Eos|Apply|KApply|Add|AnyBut|Columns|Eos|Float|Identity|Integer|Lower|Map|Name|Newline|OneOrMore|Plus|Printable|Punctuation|SignedEFloat|SignedFloat|SignedInteger|SkipTo|String|Substitute|UnsignedFloat|UnsignedInteger|Upper|Whitespace|Word|ZeroOrMore|Repeat)/lepl.matchers.derived.\2/g' *.rst
sed -i -r 's/lepl\.matchers\.(And|Or|First)/lepl.matchers.combine.\1/g' *.rst
sed -i -r 's/lepl\.(functions|matchers)\.(Literal|Regexp|Delayed|Lookahead|Empty|Eof)/lepl.matchers.core.\2/g' *.rst
sed -i -r 's/lepl\.matchers\.(Commit|Trace)/lepl.matchers.monitor.\1/g' *.rst
sed -i -r 's/lepl\.match\.(Commit|Trace)/lepl.matchers.monitor.\1/g' *.rst
sed -i -r 's/lepl\.memo\.(LMemo|RMemo)/lepl.matchers.memo.\1/g' *.rst
sed -i -r 's/lepl\.operators\.([A-Za-z]+)/lepl.matchers.operators.\1/g' *.rst
sed -i -r 's/lepl\.lexer\.functions\.(Token)/lepl.lexer.matchers.\1/g' *.rst
sed -i -r 's/lepl\.node\.(Node|make_dict)/lepl.support.node.\1/g' *.rst
sed -i -r 's/lepl\.node\.(Error|throw|make_error)/lepl.matchers.error.\1/g' *.rst

# lepl 4 direct
sed -i -r 's/``(SignedFloat|Drop|Space|Star|Optional|Letter|Digit|args|Eos|Word|Integer|Apply|KApply|Add|AnyBut|Columns|Eos|Float|Identity|Integer|Lower|Map|Name|Newline|OneOrMore|Plus|Printable|Punctuation|SignedEFloat|SignedFloat|SignedInteger|SkipTo|String|Substitute|UnsignedFloat|UnsignedInteger|Upper|Whitespace|Word|ZeroOrMore|Repeat)(\([^\)]*\))``/`\1\2 <api\/redirect.html#lepl.matchers.derived.\1>`_/g' *.rst
sed -i -r 's/``(And|Or|First)(\([^\)]*\))``/`\1\2 <api\/redirect.html#lepl.matchers.combine.\1>`_/g' *.rst
sed -i -r 's/``(Literal|Regexp|Delayed|Lookahead|Empty|Eof)(\([^\)]*\))``/`\1\2 <api\/redirect.html#lepl.matchers.core.\1>`_/g' *.rst
sed -i -r 's/``(LMemo|RMemo)(\([^\)]*\))``/`\1\2 <api\/redirect.html#lepl.matchers.memo.\1>`_/g' *.rst
sed -i -r 's/``(DroppedSpace|Separator)(\([^\)]*\))``/`\1\2 <api\/redirect.html#lepl.matchers.operators.\1>`_/g' *.rst
sed -i -r 's/``(OperatorMatcher)(\([^\)]*\))``/`\1\2 <api\/redirect.html#lepl.matchers.support.\1>`_/g' *.rst
sed -i -r 's/``(Error|make_error|raise_error)(\([^\)]*\))``/`\1\2 <api\/redirect.html#lepl.matchers.error.\1>`_/g' *.rst
sed -i -r 's/``(Token)(\([^\)]*\))``/`\1\2 <api\/redirect.html#lepl.lexer.matchers.\1>`_/g' *.rst
sed -i -r 's/``(Node|make_dict|node_throw)\(\)``/`\1() <api\/redirect.html#lepl.support.node.\1>`_/g' *.rst
sed -i -r 's/``(List|sexpr_fold|sexpr_flatten|sexpr_to_tree|sexpr_throw)\(\)``/`\1() <api\/redirect.html#lepl.support.list.\1>`_/g' *.rst
sed -i -r 's/``(ConstructorGraphNode)\(\)``/`\1() <api\/redirect.html#lepl.support.graph.\1>`_/g' *.rst
sed -i -r 's/``(.config\.)([^\. ]+)(\([^\)]*\))``/`\1\2\3 <api\/redirect.html#lepl.core.config.ConfigBuilder.\2>`_/g' *.rst
sed -i -r 's/``(matcher\.)([^\. ]+)\(\)``/`\1\2() <api\/redirect.html#lepl.core.config.ParserMixin.\2>`_/g' *.rst
sed -i -r 's/``(rightmost)\(\)``/`\1() <api\/redirect.html#lepl.offside.matchers.\1>`_/g' *.rst
sed -i -r 's/``(make_str_parser)\(\)``/`\1() <api\/redirect.html#lepl.regexp.str.\1>`_/g' *.rst
