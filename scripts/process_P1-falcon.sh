#!/bin/bash

# The list of files is created by:
#     find images/ -name "*MicroED_*.tif" | sort |tee LIST
# Then this script is executed in parallel:
#     parallel -P8 --ungroup bash process_P1.sh < LIST

JOBNAME=`basename $1 | cut -d_ -f 1,2,6 | sed -e s,.tif,,g`

if [ -e $JOBNAME/P1 ]; then
    echo $JOBNAME has been already processed
    exit
fi

mkdir -p $JOBNAME/P1
cd $JOBNAME/P1
rm -fr {optimised,indexed,refined,integrated,symmetrized,scaled}.{expt,refl} image.emd
ln -s ../../$1 image.tiff

dials.import image.tiff pixel_size=0.028,0.028 distance=615.5 fast_slow_beam_centre=999,1001 geometry.scan.oscillation=0,0.4354 geometry.beam.wavelength=0.025079 panel.gain=26 panel.trusted_range=-20,65535 panel.pedestal=-10 mask=../../pixels.mask goniometer.axis=0,1,0
dials.find_spots imported.expt gain=0.4 max_separation=4 nproc=12

#dials.search_beam_position imported.expt strong.refl
#dials.find_rotation_axis optimised.expt strong.refl # just for check

if [ ! -f optimised.expt ]; then
    cp imported.expt optimised.expt
fi
dials.index optimised.expt strong.refl detector.fix=distance hkl_tolerance=0.1 #space_group=P2 # unit_cell=5,10,20,90,90,90
if [ ! -f indexed.expt ]; then
    dials.index optimised.expt strong.refl detector.fix=distance hkl_tolerance=0.1 indexing.method=fft1d #space_group=P2 # unit_cell=5,10,20,90,90,90
fi
#if [ ! -f indexed.expt ]; then
#    dials.index imported.expt strong.refl detector.fix=distance indexing.method=real_space_grid_search #space_group=P2 # unit_cell=5,10,20,90,90,90 
#fi
if [ ! -f indexed.expt ]; then
    exit
fi
dials.refine indexed.expt indexed.refl scan_varying=False detector.fix=distance
dials.refine refined.expt refined.refl scan_varying=True detector.fix=distance

dials.integrate refined.expt refined.refl prediction.d_min=0.7 nproc=12 profile.gaussian_rs.min_spots.overall=25
if [ ! -f integrated.expt ]; then
    exit
fi
dials.check_indexing_symmetry integrated.{expt,refl} d_min=1.2 d_max=6 grid=2
dials.symmetry integrated.expt integrated.refl
#dials.scale integrated.expt integrated.refl d_min=0.9 json=scaled.json

dials.python ../../../scripts/filter_blanks_fixed.py integrated.expt integrated.refl
if [ ! -f not_blank.expt ]; then
    exit
fi

mkdir not_blank
cd not_blank

dials.scale ../not_blank.{expt,refl} d_min=0.75 json=scaled.json nbins=15

cd ..
