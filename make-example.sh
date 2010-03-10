#!/bin/bash

cat > example.txt <<EOF
Python 3.1 (r31:73572, Oct 24 2009, 05:39:09)
[GCC 4.4.1 [gcc-4_4-branch revision 150839]] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>>
EOF
echo -n ">>> " >> example.txt

PYTHONPATH=src empty -f -i in.fifo -o out.fifo -p empty.pid -L empty.log python3
IFS=$'\n'

cat src/lepl/_example/web_script.py |
while read line
do
  while [ 1 ]; do
    empty -r -t 1 -i out.fifo >> example.txt 2> /dev/null
    if [ $? == 255 ]; then break; fi
  done
  echo $line | empty -s -o in.fifo
  echo $line >> example.txt
done

echo 'PAUSE' >> example.txt
echo -n 'CLEAR' >> example.txt

kill `cat empty.pid`

mv example.txt doc-src
