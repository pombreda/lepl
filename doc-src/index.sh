#!/bin/bash

# replace 
#   ``foo()``
# with a link to foo
#   `foo() <api/redirect.html#lepl.foo>`_

sed -i -r 's/``(SignedFloat|Literal|Drop|Star|Space)\(\)``/`\1() <api\/redirect.html#lepl.matchers.\1>`_/g' *.rst
sed -i -r 's/``(Separator)\(\)``/`\1() <api\/redirect.html#lepl.operators.\1>`_/g' *.rst
sed -i -r 's/``(BitString|Int)\(\)``/`\1() <api\/redirect.html#lepl.bin.bits.\1>`_/g' *.rst
sed -i -r 's/``(Const|BEnd|LEnd)\(\)``/`\1() <api\/redirect.html#lepl.bin.matchers.\1>`_/g' *.rst

# fix up old errors
#sed -i -e 's/redirect\/html/redirect.html/g' *.rst
