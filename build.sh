#!/bin/bash

VERSION=`egrep version setup.py | sed -e "s/.*'\(.*\)'.*/\\1/"`

rm MANIFEST.in
find . -exec echo "exclude {}" \; | sed -e "s/\.\///" >> MANIFEST.in
for f in `ls -1 src/lepl/*.py`; 
do 
  echo "include $f" >> MANIFEST.in
done
for f in `ls -1 src/COPY*`; 
do 
  echo "include $f" >> MANIFEST.in
done
echo "include setup.py" >> MANIFEST.in

python setup.py sdist --formats=gztar,zip


rm -fr doc

sphinx-build -b html doc-src/ doc

epydoc -v -o doc/api --html --graph=all --docformat=restructuredtext -v --exclude="_test"  --exclude="_example" --debug src/*

rm -fr "LEPL-$VERSION"
mkdir "LEPL-$VERSION"
cp -r doc/* "LEPL-$VERSION/doc"
tar cvfz "doc/LEPL-$VERSION-doc.tar.gz" "LEPL-$VERSION"
zip -r "doc/LEPL-$VERSION-doc.zip" "LEPL-$VERSION" -x \*.tgz
rm -fr "LEPL-$VERSION"

cp "dist/LEPL-$VERSION.tar.gz" doc
cp "dist/LEPL-$VERSION.zip" doc

rsync -rv --exclude=".svn" --delete doc/ ~/projects/personal/www/lepl
