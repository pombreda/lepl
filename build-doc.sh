#!/bin/bash

RELEASE=`egrep "version=" setup.py | sed -e "s/.*'\(.*\)'.*/\\1/"`
VERSION=`echo $RELEASE | sed -e "s/[^.]*\([0-9]\.[0-9]\).*/\\1/"`

echo $RELEASE
echo $VERSION

sed -i -e "s/release = .*/release = '$RELEASE'/" doc-src/manual/conf.py
sed -i -e "s/version = .*/version = '$VERSION'/" doc-src/manual/conf.py

sed -i -e "s/__version__ = .*/__version__ = '$RELEASE'/" src/lepl/__init__.py

rm -fr doc

pushd doc-src/manual
./index.sh
popd

sphinx-build -b html doc-src/manual doc

# this is a bit of a hack, but people want to jump directly to the text
# so we skip the contents
#pushd doc
#sed -i -e 's/href="intro.html"/href="intro-1.html"/' index.html
#sed -i -e 's/A Tutorial for LEPL/Tutorial Contents/' intro-1.html
#popd

# parse-only necessary or we lose all decorated functions
epydoc -v -o doc/api --parse-only --html --graph=all --docformat=restructuredtext -v --exclude="_experiment" --exclude="_performance" --exclude="_example" --debug src/*

cp doc-src/example.txt doc
cp doc-src/index.html doc
cp doc-src/index.css doc
