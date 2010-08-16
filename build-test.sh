#!/bin/bash

RELEASE=`egrep "version=" setup.py | sed -e "s/.*'\(.*\)'.*/\\1/"`
VERSION=`echo $RELEASE | sed -e "s/.*?\([0-9]\.[0-9]\).*/\\1/"`

rm -fr test

mkdir test
virtualenv --python=python2.7 --no-site-packages test
#virtualenv --python=python2.6 --no-site-packages test
#virtualenv --python=python3.1 --no-site-packages test

cd test
source bin/activate

easy_install ../dist/LEPL-$RELEASE.tar.gz
#easy_install-3.1 ../dist/LEPL-$RELEASE.tar.gz

python -c 'from lepl._test import all; all()'
#python3.1 -c 'from lepl._test import all; all()'

