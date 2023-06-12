# repack_emd.py by Takanori Nakane

# Verlox's EMD file is in the HDF5 container but uncompressed.
# Typical MicroED data can be compressed to less than 50 % of the original size.
# Unfortunately, compression by the `h5repack` command is very slow due to
# inefficient access pattern, as discussed in https://forum.hdfgroup.org/t/speeding-up-h5repack/1145.
# This script reads data in a more efficient way and compresses about 40 times faster!

import h5py
import numpy as np
import os
import sys
import zlib

compression_level = 4

if len(sys.argv) != 3:
    print("Usage: dials.python repack_emd.py input.h5 output.h5")
    sys.exit(-1)

src_filename = sys.argv[1]
dst_filename = sys.argv[2]
tmp_filename = dst_filename + ".tmp"

if (os.path.exists(dst_filename)):
    print("The output file %s already exists. Exiting..." % dst_filename)
    sys.exit(0)
if (os.path.exists(tmp_filename)):
    os.remove(tmp_filename)

fin = h5py.File(src_filename, "r")
fout = h5py.File(tmp_filename, "w")

def compress_by_frames(src, dst):
    nframes = src.shape[-1]
    other_dims = src.shape[0:-1]
    print(src.name, src.shape, nframes, other_dims)

    # We can use src.name, which contains the FULL path.
    # Group.create_dataset accepts a full path, which is relative to the file root,
    # not the group root.
    dst_dataset = dst.create_dataset(src.name, src.shape, chunks=(*other_dims, 1),
                                     compression="gzip", shuffle=True, dtype=src.dtype)
    for (name, attr) in src.attrs:
        dst_dataset.attrs[name] = attr

    for i in range(nframes):
        my_chunk = src[..., i].view(dtype=np.uint8)
        itemsize = src.dtype.itemsize

        shuffled = my_chunk.reshape((-1, itemsize)).transpose().reshape(-1)
        compressed = zlib.compress(shuffled.tobytes(), compression_level)
        dst_dataset.id.write_direct_chunk(offsets=(*((0, ) * len(other_dims)), i), data=compressed, filter_mask=0)

def doit(src, dst):
    for (name, src_child) in src.items():
        if src_child.__class__ is h5py.Dataset:
            if name in ["Data", "Metadata"]:
                compress_by_frames(src_child, dst)
            else:
                # This needs h5py >= 3.0.
                # See https://github.com/h5py/h5py/issues/1005.
                src.copy(src_child, dst)
        else:
            dst.create_group(name)
            doit(src_child, dst[name])

doit(fin, fout)

fin.close()
fout.close()

os.rename(tmp_filename, dst_filename)
