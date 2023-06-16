# Processing Scripts

This folder contains data processing scripts.

## Data layout

Our data layout is:

- data/PROJECT_NAME/
  - SerialEM navigator files
  - SerialEM montage files
  - crystal images
  - screening images (diffraction snap shots)
  - raw/ <--- Verlox writes uncompressed EMDs here
  - compressed/ <--- `repack_emd.py` writes compressed EMDs here

## Compression

Verlox's EMD file is in the HDF5 container but uncompressed.
Typical MicroED data can be compressed to less than 50 % of the original size.

Unfortunately, compression by the `h5repack` command is very slow due to　an
inefficient access pattern, as discussed [here](https://forum.hdfgroup.org/t/speeding-up-h5repack/1145).
Our `repack_emd.py` reads data in a more efficient way and compresses about 40 times faster.

On the on-the-fly processing node called `talos-otf`, which can access microscope's storage,
we run the following one-liner to compress Verlox EMD files.

```sh
while true; do find -name '*.emd*' -mmin +3 | parallel -P8 dials.python repack_emd.sh {} ../compressed/\`echo {} \| sed -e 's,\ ,_,g'\`; sleep 60; done&
```

This also replaces annoying whitespaces in the file name into underscores.
For example, `Camera Ceta 20230611 2324 670 mm.emd` becomes `Camera_Ceta_20230611_2324_670_mm.emd`.

`-mmin +3` is to prevent processing files being recorded.
But this might not be necessary, because Verlox locks files anyway.

## Transfer to our cluster

Further processing is performed on a cluster node.
A cluster node periodically runs `rsync` to copy images from the microscope storage.

```sh
while true; do rsync -avuP --exclude raw --exclude '*.tmp' talos-otf:/mnt/falcon/USER/PROJECT_NAME . ; sleep 90; done&
```

## Processing with DIALS

We make a separate work directory and make a symbolic link called `images` to the `compressed` folder.
For each crystal, we make a subdirectory, within which each processing trial has its own directory.
In this example, we have two trials, one called P1 (without known unit cell) and mP (with prior cell parameters
and a monoclinic constraint).

- work/PROJECT_NAME/
  - pixels.mask
  - process_P1.sh
  - process_mP.sh
  - images/ ---> a symbolic link to data/PROJECT_NAME/compressed
  - YYYYMMDD_HHMM/ ---> a crystal
    - P1/
    - mP/
  - YYYYMMDD_HHMM/ ---> another crystal
    - P1/
    - mP/

This is done by `process_P1.sh` and `process_mP.sh`. (TO BE DESCRIBED)

## dials.filter_blanks

Often crystals go out of the beam during rotation or die due to radiation damage.
Integrating empty frames leads to strange merging statistics including negative R factors.
`filter_blanks.py` removes such empty frames.

This script was originally written by Graeme Winter as a [pull request to DIALS](https://github.com/dials/dials/pull/2232),
but has never been merged. Takanori Nakane (hopefully) fixed bugs in frame indexing (see the above pull request for details).

## Summarizing the result

`list.sh` produces a nice table of processing results.

The table lists the path, resolution at which CC1/2 drops below 0.3, unit cell parameters (before cosym)
and symmetry suggested by `dials.cosym`.

```
20230609_1245/P1 0.92     Unit cell: 5.336  6.4611  10.860  90.14  91.3  90.66 Best solution: P 1 2/m 1
20230612_0222/P1 1.26     Unit cell: 5.344  6.4788  10.84  90.00  90.20  90.02 Best solution: P 1 2/m 1
...
```
