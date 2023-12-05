# With help from Keitaro Yamashita

import h5py
import json
import pprint
import sys

if len(sys.argv) != 2 and len(sys.argv) != 3:
    sys.stderr.write("Usage: dials.python print_emd_header.py input.emd [frame]\n")
    sys.exit(-1)

filename = sys.argv[1]
frame = 0
if len(sys.argv) == 3:
    frame = int(sys.argv[2])

emd = h5py.File(filename, "r")
image_key = list(emd["/Data/Image"].keys())[0]
metadata = emd["/Data/Image/%s/Metadata" % image_key][:, frame].T
json_string = metadata.tostring().decode("utf-8").rstrip('\x00')
pprint.pprint(json.loads(json_string))
