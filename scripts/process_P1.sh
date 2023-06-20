#!/bin/bash

# The list of files is created by:
#     find images/ -name "*.emd" -size +50M | cut -d_ -f 3,4  |tee LIST
# Then this script is executed in parallel:
#     parallel -P8 --ungroup bash process_P1.sh < LIST

if [ -e $1/P1 ]; then
    echo $1 has been already processed
    exit
fi

mkdir -p $1/P1
cd $1/P1
rm -fr {optimised,indexed,refined,integrated,symmetrized,scaled}.{expt,refl} image.emd
if [ -f "../../images/Camera_Ceta_"*"$1_670_mm_0001.emd" ]; then
    ln -s "../../images/Camera_Ceta_"*"$1_670_mm_0001.emd" image.emd
else
    ln -s "../../images/Camera_Ceta_"*"$1_670_mm.emd" image.emd
fi

dials.import image.emd mask=../../pixels.mask panel.pedestal=-40 distance=618 fast_slow_beam_centre=1039,1007 # image_range=$2
dials.find_spots imported.expt gain=0.1 max_separation=4 nproc=4
#dials.search_beam_position imported.expt strong.refl
#dials.find_rotation_axis optimised.expt strong.refl # just for check

if [ ! -f optimised.expt ]; then
    cp imported.expt optimised.expt
fi
dials.index optimised.expt strong.refl detector.fix=distance #space_group=P2 # unit_cell=5,10,20,90,90,90
if [ ! -f indexed.expt ]; then
    dials.index optimised.expt strong.refl detector.fix=distance indexing.method=fft1d #space_group=P2 # unit_cell=5,10,20,90,90,90
fi
#if [ ! -f indexed.expt ]; then
#    dials.index imported.expt strong.refl detector.fix=distance indexing.method=real_space_grid_search #space_group=P2 # unit_cell=5,10,20,90,90,90 
#fi
if [ ! -f indexed.expt ]; then
    exit
fi
dials.refine indexed.expt indexed.refl scan_varying=False detector.fix=distance
dials.refine refined.expt refined.refl scan_varying=True detector.fix=distance

dials.integrate refined.expt refined.refl prediction.d_min=0.7 nproc=4  profile.gaussian_rs.min_spots.overall=25
if [ ! -f integrated.expt ]; then
    exit
fi
dials.check_indexing_symmetry integrated.{expt,refl} d_min=1.2 d_max=6 grid=2
dials.scale integrated.expt integrated.refl d_min=0.8 json=scaled.json

dials.python ../../../scripts/filter_blanks.py integrated.expt integrated.refl
if [ ! -f not_blank.expt ]; then
	    exit
fi
dials.cosym integrated.expt integrated.refl

mkdir not_blank
cd not_blank

dials.scale ../not_blank.{expt,refl} d_min=0.7 json=scaled.json

cd ..
