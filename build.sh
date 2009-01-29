#!/bin/bash

rm -fr doc

#sphinx-build -b doctest doc-src/ doc/manual
sphinx-build -b html doc-src/ doc

#epydoc -v -o doc/api --html --graph=all --docformat=restructuredtext -v --exclude="_test"  --exclude="_example" --debug src/*
epydoc -v -o doc/api --html --docformat=restructuredtext -v --exclude="_test"  --exclude="_example" --debug src/*

