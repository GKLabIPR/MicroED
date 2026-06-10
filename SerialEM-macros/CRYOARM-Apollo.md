# Automated data collection with SerialEM and Apollo on JEOL CRYO ARM

## SerialEM setup

### Illumination conditions

To be written.

### SerialEM bugs

To be written.

- Image offset bug
- AlignToNavItem bug

### Camera parameters (most complicated)

## SerialEM usage

To be written.

## Calibrations 

### Virtual camera distances

The nominal and real camera distances of our CRYO ARM200 with Apollo are as follows.
These values were first calibrated on June 7th, 2026 (values in parenthesis).
Values were tested every 0.5 mm.

- D500 ~ 548.0 mm, max res ~ 0.82 Å @ edge
- D400 ~ 437.5 mm, max res ~ 0.66 Å @ edge
- D300 ~ 335.5 mm, max res ~ 0.51 Å @ edge
- D250 ~ 278.5 mm, max res ~ 0.43 Å @ edge 

These values were calibrated by BaZrO3 cubic crystals.
Unfortunately, the literature values are not very consistent:

- J. Materials Science [“Low-temperature thermophysical and crystallographic properties of BaZrO3 perovskite”](https://link.springer.com/article/10.1007/s10853-020-04453-5)  
  says 4.18983(1) Å at 150 K, 4.18878(1) Å at 75 K.
- Physics and Chemistry of Minerals [“Thermal expansion of SrZrO3 and BaZrO3 perovskites”](https://link.springer.com/article/10.1007/BF00200187)  
  says 4.1947 (4) Å at 200 K, 4.1900 (4) Å at 25 K.
 
The overall error is hopefully about 0.5 %.

### Rotation axis

The rotation axis is parallel to the beam stop and ~ (-0.9603,0.2790,0) as determined on June 3th, 2026 (`dials.find_rotation_axis` on Hojo's sample).
Note that there is some rotation between the flu screen and the Apollo camera.

### Pixel size

The pixel size of Apollo is 8 um.
After 2x binning to 2K x 2K, it is 16 um.

Note that in SerialEM, no binning means super-resolution (8K x 8K).
To get a 2K x 2K images, select 4x binning.
