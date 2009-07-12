#!/bin/bash

RELEASE=`egrep "version=" setup.py | sed -e "s/.*'\(.*\)'.*/\\1/"`
VERSION=`echo $RELEASE | sed -e "s/.*?\([0-9]\.[0-9]\).*/\\1/"`

rm -fr test

mkdir test
virtualenv --python=python2.6 --no-site-packages test

cd test
source bin/activate

easy_install nose
easy_install ../dist/LEPL-$RELEASE.tar.gz
nosetests --log-config=../test.ini `find ../src -name "*.py" | grep _test`
