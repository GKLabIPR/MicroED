# After this, do
# montage crystal-0*.png -tile 6x -geometry 256x256+0+0 test.png

import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

def rotate_around(axis, angle):
    """
Returns a rotation matrix around `axis` by `angle` radians.
A positive `angle` means a connter-clockwise rotation when looking towards the positive `axis`.
This is opposite to that of RELION!
    """
    axis = np.ravel(axis)
    x, y, z = axis / np.sqrt(np.sum(axis ** 2))

    s = np.sin(angle)
    c = np.cos(angle)
    cc = 1 - c

    R = np.zeros((3, 3))
    R[0, 0] =  c + x * x * cc
    R[0, 1] =  x * y * cc - z * s
    R[0, 2] =  x * z * cc + y * s
    R[1, 0] =  x * y * cc + z * s
    R[1, 1] =  c + y * y * cc
    R[1, 2] =  y * z * cc - x * s
    R[2, 0] =  x * z * cc - y * s
    R[2, 1] =  y * z * cc + x * s
    R[2, 2] =  c + z * z * cc

    return R

if len(sys.argv) != 2:
    sys.stderr.write("Usage: python real-space-axes.py indexed.expt\n")
    exit(-1)

j = json.load(open(sys.argv[1], "r"))

assert len(j["imageset"]) == len(j["crystal"])
n_cryst = len(j["imageset"])

for i in range(n_cryst):
    tiff_path = j["imageset"][i]["template"]

    tiff_path = Path(tiff_path).resolve()
    angle, _, _, tiff_idx = tiff_path.stem.split("_")[-4:] # 2025-11-29_12.57.07_24_0.0640_MicroED-D670_221.tif
    proj_dir = tiff_path.parent.parent
    candidates = list(proj_dir.glob(f"thumb-*_{tiff_idx}.jpg"))
    assert len(candidates) == 1
    thumbnail_path = candidates[0]
    print("Angle:", angle)
    print("Thumbnail:", thumbnail_path)

    crystal = j["crystal"][i]
    axes = np.zeros((3, 3))
    axes[:, 0] = [float(x) for x in crystal["real_space_a"]]
    axes[:, 1] = [float(x) for x in crystal["real_space_b"]]
    axes[:, 2] = [float(x) for x in crystal["real_space_c"]]
    angle = float(angle) / 180.0 * np.pi

    #print("Axes in columns:")
    #print(axes)

    rotation_axis = [float(x) for x in j["goniometer"][i]["rotation_axis"]]
    rotated_axes = rotate_around(rotation_axis, angle).dot(axes)

    #print("Axes in columns (at gonio 0)")
    #print(rotated_axes)

    lens = np.sqrt(np.sum(rotated_axes ** 2, axis=1))
    print("abc (after normalization) at gonio 0")
    print(rotated_axes / lens[:, np.newaxis])

    img = Image.open(thumbnail_path).convert("RGB")

    draw = ImageDraw.Draw(img)
    cx = img.size[0] // 2
    cy = img.size[1] // 2
    font = ImageFont.truetype(font="DejaVuSans.ttf", size=20)
    scale = 5

    draw.line((cx, cy, cx + int(rotated_axes[1, 0] * scale), cy + int(rotated_axes[2, 0] * scale)), fill="red", width=3)
    draw.text((cx + int(rotated_axes[1, 0] * scale), cy + int(rotated_axes[2, 0] * scale)), "a", fill="red", font=font)
    draw.line((cx, cy, cx + int(rotated_axes[1, 1] * scale), cy + int(rotated_axes[2, 1] * scale)), fill="blue", width=3)
    draw.text((cx + int(rotated_axes[1, 1] * scale), cy + int(rotated_axes[2, 1] * scale)), "b", fill="blue", font=font)
    draw.line((cx, cy, cx + int(rotated_axes[1, 2] * scale), cy + int(rotated_axes[2, 2] * scale)), fill="green", width=3)
    draw.text((cx + int(rotated_axes[1, 2] * scale), cy + int(rotated_axes[2, 2] * scale)), "c", fill="green", font=font)
    img.save("crystal-%03i.png" % i)
