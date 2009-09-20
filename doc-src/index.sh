#!/bin/bash

# replace 
#   ``foo()``
# with a link to foo
#   `foo() <api/redirect.html#lepl.foo>`_

sed -i -r 's/``(Delayed|Literal|Columns|And|Or|Any)\(\)``/`\1() <api\/redirect.html#lepl.matchers.\1>`_/g' *.rst
sed -i -r 's/``(Letter|Digit|Rexgexp|args|SkipTo|SignedFloat|Literal|Drop|Star|Space|Eos)\(\)``/`\1() <api\/redirect.html#lepl.functions.\1>`_/g' *.rst
sed -i -r 's/``(Node)\(\)``/`\1() <api\/redirect.html#lepl.node.\1>`_/g' *.rst
sed -i -r 's/``(Separator|SmartSeparator1)\(\)``/`\1() <api\/redirect.html#lepl.operators.\1>`_/g' *.rst
sed -i -r 's/``(TraceResults)\(\)``/`\1() <api\/redirect.html#lepl.trace.\1>`_/g' *.rst
sed -i -r 's/``(SmartSeparator2)\(\)``/`\1() <api\/redirect.html#lepl.contrib.matchers.\1>`_/g' *.rst
sed -i -r 's/``(Token)\(\)``/`\1() <api\/redirect.html#lepl.lexer.matchers.\1>`_/g' *.rst
sed -i -r 's/``(BitString|Int)\(\)``/`\1() <api\/redirect.html#lepl.bin.bits.\1>`_/g' *.rst
sed -i -r 's/``(Const|BEnd|LEnd)\(\)``/`\1() <api\/redirect.html#lepl.bin.matchers.\1>`_/g' *.rst
sed -i -r 's/``(Configuration)\(\)``/`\1() <api\/redirect.html#lepl.bin.config.\1>`_/g' *.rst
sed -i -r 's/``(DfaRegexp|NfaRegexp)\(\)``/`\1() <api\/redirect.html#lepl.regexp.matchers.\1>`_/g' *.rst
sed -i -r 's/``(Line|Block|BLine|ContinuedLineFactory|ContinuedBLineFactory|Extend|SOL|EOL)\(\)``/`\1() <api\/redirect.html#lepl.offside.matchers.\1>`_/g' *.rst
sed -i -r 's/``(Indent|Eol|BIndent)\(\)``/`\1() <api\/redirect.html#lepl.offside.lexer.\1>`_/g' *.rst
sed -i -r 's/``(LineAwareConfiguration|IndentConfiguration|OffsideConfiguration)\(\)``/`\1() <api\/redirect.html#lepl.offside.config.\1>`_/g' *.rst

# fix up old errors
#sed -i -e 's/redirect\/html/redirect.html/g' *.rst
#sed -i -r 's/matchers\.(AnyBut|Optional|Star|ZeroOrMore|Plus|OneOrMore|Map|Add|Substitute|Name|Eos|Identity|Newline|Space|Whitespace|Digit|Letter|Upper|Lower|Printable|Punctuation|UnsignedInteger|SignedInteger|Integer|UnsignedFloat|SignedFloat|SignedEFloat|Float|Word|String||Drop)/functions.\1/g' *.rst
sed -i -r 's/functions\.(And|Or|Literal|Columns)/matchers.\1/g' *.rst
#sed -i -r 's/lepl\.contrib\.functions\.SmartSeparator2/lepl.contrib.matchers.SmartSeparator2/g' *.rst
sed -i -r 's/lepl\.offside\.matchers\.(LineAwareConfiguration|IndentConfiguration|OffsideConfiguration)/lepl.offside.config.\1/g' *.rst
sed -i -r 's/lepl\.lexer\.matchers\.(Indent|Eol|BIndent)/lepl.offside.lexer.\1/g' *.rst


