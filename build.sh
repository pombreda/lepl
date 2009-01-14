#!/bin/bash

rm -fr doc/api
epydoc -v -o doc/api --html --graph=all --docformat=restructuredtext -v --exclude="_test"  --exclude="_example" src/*
rm -fr doc/manual
#sphinx-build -b doctest doc-src/ doc/manual
sphinx-build -b html doc-src/ doc/manual
