#!/bin/sh

if [ "$#" -ne 2 ]; then
	echo "Usage: mrc2zip_tiff input.mrc output.tif"
	exit
fi

if [ -f "$2" ]; then
	echo "Output file $2 already exists."
	exit
fi

# For some images, tiling improves the compression rate.
# It also enables parallelization within an image.
# The "-T 1024,1024" option does this.
# If the image dimension is not multiples of 1024,
# tweak these numbers.

mrc2tif -s -c zip -T 1024,1024 "$1" "$2.tmp"
mv "$2.tmp" "$2"
