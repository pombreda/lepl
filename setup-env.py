#!/bin/bash

virtualenv -p /usr/bin/python2.7 env
source ./env/bin/activate
#pip install python-graph-core
#pip install python-graph-dot
#pip install pygraphviz
pip install pytest

virtualenv -p /usr/local/bin/python3.2 env3
source ./env3/bin/activate
#pip install python-graph-core
#pip install python-graph-dot
#pip install pygraphviz
pip install pytest



