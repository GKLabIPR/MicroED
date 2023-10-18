#!/bin/bash

# list.sh by Takanori Nakane
# Usage:
# ./list.sh P1/not_blank | sort -rnk2 | tee RESO-P1-nb

# This generates a table of
# PATH RESOLUTION(CC1/2 > 0.3) UNIT_CELL COSYM's result
# e.g.
#
# 20230609_1245/P1 0.92     Unit cell: 5.336  6.4611  10.860  90.14  91.3  90.66 Best solution: P 1 2/m 1
# 20230612_0222/P1 1.26     Unit cell: 5.344  6.4788  10.84  90.00  90.20  90.02 Best solution: P 1 2/m 1

JOB=$1

for f in */$1/dials.scale.log; do
    DIR=`dirname $f | cut -d/ -f1,2`
    awk -v DIR=$DIR \
	 '/cc_ano/ {f=1; b=999; next}
         f==1 && $13 > 0.3 {b = $2;}
	 f==1 && $13 <= 0.3 {printf DIR" "b" "; ok = 1; exit}
	 END {if (ok != 1) printf "BAD"}' $f
    grep Unit $DIR/dials.integrate.log | sed -e s,\([0-9]*\),,g  -e 's/,/ /g' | tr -d '\n'
    echo -n " "
    grep "Best sol" $DIR/dials.symmetry.log | tr -d '\n'
    echo
done | grep -v BAD
