#!/bin/bash

rm -fr doc

#sphinx-build -b doctest doc-src/ doc/manual
sphinx-build -b html doc-src/ doc

#epydoc -v -o doc/api --html --graph=all --docformat=restructuredtext -v --exclude="_test"  --exclude="_example" --debug src/*
epydoc -v -o doc/api --html --docformat=restructuredtext -v --exclude="_test"  --exclude="_example" --debug src/*

tar cvfz doc/doc.tgz doc/*
zip -r doc/doc.zip doc -x \*.tgz

tar cvfz doc/src.tgz --exclude="_test" --exclude="_example" --exclude=".svn" --exclude="*.pyc" --exclude="LEPL*" src/*
zip -r doc/src.zip src/ -i \*.py -x \*/_test/\* -x \*/_example/\* -i COPYING\*
