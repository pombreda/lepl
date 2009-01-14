#!/bin/bash

rm -fr doc/api
epydoc -v -o doc/api --html --graph=all --docformat=restructuredtext -v --exclude="_test" src/*
