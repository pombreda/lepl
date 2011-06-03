#!/bin/bash

pushd ~/projects/personal/www/lepl
svn update
svn remove --force *
svn commit -m "lepl"
popd
rsync -rv --exclude=".svn" --delete doc/ ~/projects/personal/www/lepl
pushd ~/projects/personal/www/lepl
svn add *
svn commit -m "lepl"
popd

