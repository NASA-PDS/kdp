#!/bin/bash

for i in `xmllint --xpath "//*[local-name()='file_name']" $1 | sed 's/<\/file_name>/\n/g' | awk -F'>' '{print $2}'`
do
  echo ${i}
done