#!/bin/bash

RELEASE=`egrep "version=" setup.py | sed -e "s/.*'\(.*\)'.*/\\1/"`
VERSION=`echo $RELEASE | sed -e "s/.*?\([0-9]\.[0-9]\).*/\\1/"`

sed -i -e "s/release = .*/release = '$RELEASE'/" doc-src/conf.py
sed -i -e "s/version = .*/version = '$VERSION'/" doc-src/conf.py

sed -i -e "s/__version__ = .*/__version__ = '$RELEASE'/" src/lepl/__init__.py

rm -fr doc

sphinx-build -b html doc-src/ doc

epydoc -v -o doc/api --html --graph=all --docformat=restructuredtext -v --exclude="_test" --exclude="_example" --exclude="_experiment" --exclude="_trampoline" --exclude="_performance" --debug src/*

