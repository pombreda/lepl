#!/bin/bash

killall empty
sleep 1

rm -f example.txt

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
while [ 1 ]; do
  empty -r -t 1 -i out.fifo >> example.txt 2> /dev/null
  if [ $? == 255 ]; then break; fi
done

echo >> example.txt
echo 'PAUSE' >> example.txt
echo -n 'CLEAR' >> example.txt

killall empty

mv example.txt doc-src
