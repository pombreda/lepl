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
sed -i -r 's/lepl\.functions\.(SignedFloat|Drop|Space|Star|Optional|Letter|Digit|args|Eos)/lepl.matchers.derived.\1/g' *.rst
sed -i -r 's/lepl\.matchers\.(And|Or)/lepl.matchers.combine.\1/g' *.rst
sed -i -r 's/lepl\.matchers\.(Literal|Delayed)/lepl.matchers.core.\1/g' *.rst
sed -i -r 's/lepl\.operators\.([A-Za-z]+)/lepl.matchers.operators.\1/g' *.rst
sed -i -r 's/lepl\.lexer\.functions\.(Token)/lepl.lexer.matchers.\1/g' *.rst
sed -i -r 's/lepl\.node\.(Node|make_dict)/lepl.support.node.\1/g' *.rst

# lepl 4 direct
sed -i -r 's/``(SignedFloat|Drop|Space|Star|Optional|Letter|Digit|args|Eos|Word|Integer)\(\)``/`\1() <api\/redirect.html#lepl.matchers.derived.\1>`_/g' *.rst
sed -i -r 's/``(And|Or)\(\)``/`\1() <api\/redirect.html#lepl.matchers.combine.\1>`_/g' *.rst
sed -i -r 's/``(Literal|Regexp|Delayed)\(\)``/`\1() <api\/redirect.html#lepl.matchers.core.\1>`_/g' *.rst
sed -i -r 's/``(DroppedSpace|Separator)\(\)``/`\1() <api\/redirect.html#lepl.matchers.operators.\1>`_/g' *.rst
sed -i -r 's/``(Token)\(\)``/`\1() <api\/redirect.html#lepl.lexer.matchers.\1>`_/g' *.rst
sed -i -r 's/``(Node|make_dict)\(\)``/`\1() <api\/redirect.html#lepl.support.node.\1>`_/g' *.rst
sed -i -r 's/``(.config\.)([^\. ]+)(\([^\)]*\))``/`\1\2\3 <api\/redirect.html#lepl.core.config.ConfigBuilder.\2>`_/g' *.rst
sed -i -r 's/``(matcher\.)([^\. ]+)\(\)``/`\1\2() <api\/redirect.html#lepl.core.config.ParserMixin.\2>`_/g' *.rst
