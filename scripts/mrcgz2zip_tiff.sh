#!/bin/sh

if [ "$#" -ne 1 ]; then
	echo "Usage: mrc2zip_tiff input"
	exit
fi

inp=$1
jobname=`basename $inp`
out=${jobname}.tif

if [ -f "$out" ]; then
	echo "Output file $out already exists."
	exit
fi

tmpdir=/dev/shm/${jobname}
rm -fr $tmpdir
mkdir -p $tmpdir

for f in `find $inp -type f -name "*.mrc.gz"`; do
	echo $f
	name=`basename $f`
	name=${name%.gz}
	gzip -dck $f > ${tmpdir}/${name}
done

newstack `find $tmpdir -type f -name "*.mrc" | sort` ${tmpdir}/concat.mrcs
mrc2tif -s -c zip -T 512,512 ${tmpdir}/concat.mrcs ${tmpdir}/concat.tif
mv ${tmpdir}/concat.tif $out

rm -fr $tmpdir
