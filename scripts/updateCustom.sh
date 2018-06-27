#!/bin/bash
set -eux

dir=$1

for f in `find custom/ -type f`
do
	b=`basename $f`
	if [ -f $dir/$b ]; then
		cat $dir/$b $f | sort -u > $f.2
		mv $f.2 $f
	fi
	#sort -u $f > $f.2
	#mv $f.2 $f
done

