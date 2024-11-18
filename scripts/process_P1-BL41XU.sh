#!/bin/bash

# Processing script for small-wedge small-molecular datasets
# collected at SPring-8 BL41XU (probably also works for BL32XU and BL45XU but not tested).

# Because the Ewald sphere is more curved with X-ray than electrons,
# we have fewer Friedel pairs on a frame.
# For small-wedge datasets, this leads to a very low multiplicity and
# instability of scaling and resolution estimation when performed on individual crystals.

# Usage:
#    seq 0 64 | parallel -P8 --ungroup bash process_P1.sh multi01 {}
# or
#    for i in `seq 0 54`; do echo multi01 $i; done > LIST
#    for i in `seq 0 46`; do echo multi02 $i; done >> LIST
#    # ...
#    parallel --colsep ' ' -P10 --ungroup bash process_P1.sh {} < LIST
# Note that we need --colsep ' ' to split two arguments in a line.

# check this by:
#    h5dump -d /entry/instrument/detector/detectorSpecific/nimages multi_00_master.h5
NFRAME_PER_TRIGGER=100

BLOCKNO=$2 # 0-indexed
STARTFRAME=$(($NFRAME_PER_TRIGGER * $BLOCKNO + 1)) # DIALS expects 1-indexed
ENDFRAME=$(($NFRAME_PER_TRIGGER * ($BLOCKNO + 1))) # inclusive

JOBNAME=`printf %s-%03d ${1} ${2}`

if [ -e $JOBNAME/P1 ]; then
    echo $JOBNAME has been already processed
    exit
fi

mkdir -p $JOBNAME/P1
cd $JOBNAME/P1
rm -fr {optimised,indexed,refined,integrated,symmetrized,scaled}.{expt,refl}

dials.import ../../images/$1/*master.h5 mask=../../pixels.mask image_range=${STARTFRAME},${ENDFRAME} #fast_slow_beam_centre=2013,2077
dials.find_spots imported.expt nproc=12
#dials.search_beam_position imported.expt strong.refl
#dials.find_rotation_axis optimised.expt strong.refl # just for check

if [ ! -f optimised.expt ]; then
    cp imported.expt optimised.expt
fi
dials.index optimised.expt strong.refl detector.fix=distance hkl_tolerance=0.15 #index_assignment.method=local #space_group=P2 # unit_cell=5,10,20,90,90,90
if [ ! -f indexed.expt ]; then
    dials.index optimised.expt strong.refl detector.fix=distance hkl_tolerance=0.15 #indexing.method=fft1d index_assignment.method=local #space_group=P2 # unit_cell=5,10,20,90,90,90
fi
#if [ ! -f indexed.expt ]; then
#    dials.index imported.expt strong.refl detector.fix=distance indexing.method=real_space_grid_search #space_group=P2 # unit_cell=5,10,20,90,90,90 
#fi
if [ ! -f indexed.expt ]; then
    exit
fi
dials.refine indexed.expt indexed.refl scan_varying=False detector.fix=distance
dials.refine refined.expt refined.refl scan_varying=True detector.fix=distance

dials.integrate refined.expt refined.refl prediction.d_min=0.84 nproc=12 profile.gaussian_rs.min_spots.overall=25
if [ ! -f integrated.expt ]; then
    exit
fi
dials.check_indexing_symmetry integrated.{expt,refl} d_min=1.2 d_max=6 grid=2
dials.symmetry integrated.expt integrated.refl
#dials.scale integrated.expt integrated.refl d_min=0.9 json=scaled.json

dials.python ../../../MicroED/scripts/filter_blanks_fixed.py integrated.expt integrated.refl
if [ ! -f not_blank.expt ]; then
	    exit
fi

mkdir not_blank
cd not_blank

dials.scale ../not_blank.{expt,refl} d_min=0.85 json=scaled.json nbins=15

cd ..
