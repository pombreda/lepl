#!/bin/bash

rm -fr doc

sphinx-build -b html doc-src/ doc

epydoc -v -o doc/api --html --graph=all --docformat=restructuredtext -v --exclude="_test" --exclude="_example" --exclude="_experiment" --exclude="_trampoline" --debug src/*

