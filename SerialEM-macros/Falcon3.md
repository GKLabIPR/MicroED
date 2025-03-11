# Automated data collection with SerialEM and Falcon 3

This document descibes changes needed to use Falcon3 for MicroED, instead of Ceta.
Please read [the instructions for Ceta](README.md) first.

Your Falcon 3 must be unlocked (i.e. its dose protector is disabled) to collect diffraction images.
This unlocking has to be done by a Thermo Fisher engineer and cannot be performed by a user.
Please discuss with your ThermoFisher contact person.

Because the counting mode requires an impractically low flux, we use the integration mode.
Verlox can capture Falcon 3 movies only in the counting mode,
so we use SeriaEM's `TiltDuringRecord` function instead of Verlox to record frames.

## AutoHotKey macros

We use [AutoHotKey](https://www.autohotkey.com/) to contorl the beam stop but not Verlox.
`start_velox_mov_rec.ahk` is no longer necessary.

### Ignore focusing errors

Same as Ceta.

## SerialEM setup

Use `SerialEM-macros-Falcon3.txt` instead of `SerialEM-macros.txt`.

### Illumination conditions

We use the following illumination conditions:

- LM 115x, Spot 8, C2 97.5 % (i.e. spread to cover the detector), CA 150 um for grid montaging.
  This is stored as non-low dose mode "View" and "Montage".
- SA 2600x, Spot 8, C2 64 % (i.e. spread to cover the detector), CA 50 um, microprobe, defocus 35 um for square montaging.  
  This is stored as low-dose mode "View".
- SA 5300x, Spot 11, C2 34.6 % (parallel), CA 50 um, nanoprobe.  
  This is stored as low-dose mode "Trial". This gives ~ 0.050-0.065 e/Å2/sec.
- The same beam as above but DIFF 670 mm, stored as low-dose mode "Record" and "Preview".

Note the differences from the Ceta setup:

- The "Montage" mode was introduced.
- The diffraction mode in Trial and the parallel imaging mode (SA 5300x) in Record were swapped.
- The diffraction mode was cloned into Preview.

This is because `TiltDuringRecord` uses the Record condition.
The Preview condition is used for diffraction snapshots.

The "Montage" mode was introduced for the whole grid montaging in the LM mode.
Otherwise, it will use the camera settings in the Record mode and records movies!

With this change, the routine for hysteresis removal is View, Trial, Record, not View, Record, Trial.

### Camera parameters (most complicated)

With Ceta, we used AutoHotKeys to "press" Verlox's record button from a SerialEM script.
The script pushed the record button right after it started the rotation and pushed the button again as soon as the rotation finished.
Therefore, we could freely change the rotation speed or the rotation range in SerialEM without explicitly calculating the exposure duraction.

On the other hand, we use the `TiltDuringRecord` command with Falcon 3.
The recording parameters have to be configured in the Camera Setup dialog box.
In addition, we have to set up fractionations.

Let's start with easy ones:

- View and Montage: Single image, 0.75 seconds
- Preview: Single image, 0.5 seconds 

For the Record mode, check `Save frames` and set the `Exposure time` to 51.0 seconds.
Click `Set Up Frames to Save` to open the "Frame Summing Selector" dialog box.
Change the `# of summed frames to save` to `146`.
This should give 146 fractions with 14 frames each.
This is suitable for 69 degrees rotation at the speed factor of 0.0419 (~ 1.247 deg/second).
You may try different combinations (e.g. 292 fractions with 7 frames each) but make sure all fractions contain the same number of frames.
Otherwise, deg/frame becomes non-uniform and causes processing issues.

For beam sensitive samples, we use the speed factor of 0.0640 (~ 1.906 deg/second).
In this case, we use an exposure of 33.01 seconds, divided into 9 frames / fraction, 147 fractions in total.

Click `Set File Options` to open the "Frame File Options" dialog box.
Enable `Base name` and set it "MicroED" (or whatever).
Also enable `Label of Navigator item` and `Numeric date (including year) and time at start of name`.
This results in file names like `2024-04-19_18.39.00_4_0.0419_MicroED_69.tif` (0.04199 is the rotation speed scale factor added by the script).

For all modes, select `Binning 2` (2048 x 2048 pixels), `Gain Normalized` and `Linear mode`. 

### Fractionation mystery

There is something weird about fractionation.
One frame is 0.025 sec (40 fps). 49 frames / 49 fractions give 1.225 sec but
50 frames / 50 fractions give 1.245, not 1.250 seconds.
This means the 50th frame is only 0.020 seconds.

100 frames / 100 fractions give 2.495 seconds and
149 frames / 149 fractions give 3.720 seconds as expected but
150 frames / 150 fractions are 3.74 second (i.e. the 150th frame is again only 0.020 seconds).

Similarly, the 251th, 351th and 451th frames are only 0.020 second, not 0.0250 seconds.
I guess this is related to CDS but don't know the exact rule.

### Record time mystery

Even more puzzlingly, the fraction time calculated as the total exposure time divided the number of fractions,
the value in the XML file and the time calculated based on 0.025 second/frame are not necessarily consistent.

- 51.0 sec / 146 fractions:  The division gives 0.34932 sec/frac and the XML says 0.34892 sec/frac (OK).
  But 14 frame/frac * 0.025 sec/frame = 0.350 sec/fra.
- 51.05 sec / 66 fractions: The division gives 0.77348 sec/frac but the XML says 0.7726 sec/frac.
  31 frame/frac * 0.025 sec/frame = 0.775 sec/frac.
- 45.06 sec / 288 fractions: The division gives 0.15646 sec/frac but the XML says 0.17446 sec/frac.
  7 frame/frac * 0.025 sec/frame = 0.1750 sec/frac.

I don't know what causes the difference and which one is the most accurate.
I tentatively use the value from the XML file.

### Impossible to set up camera parameters from a script

Because of the issues above, it is difficult to calculate a good exposure time in a SerialEM script that gives a uniform fraction time.
Even if we managed it, we would not be able to change the number of fractions from a script.

`SetExposure` changes only the total exposure duration, keeping the number of fractions the same.
`SetFrameTime` does not work with an error "Frame time cannot be set for the current camera type", perhaps because this is fixed to 0.025 second for Falcon 3. 
`GoToImagingState` is not useful here, because fractionation settings are not stored in a imaging state.

### Frame names and locations

Frames can be saved only to limited locations.
The folder specified in the `Set Folder` button in the Camera Setup dialog box is relative to a fixed place,
which is `Z:\TemScripting\BM-Falcon` in our scope.
The `LocalFalconFramePath` in the property file was ignored in our system.

By setting a property `SubdirsOkInFalcon3Save 1`,
one can specify subdirectories (e.g. `Grid1\raw` resulting in `Z:\TemScripting\BM-Falcon\Grid\raw`),
but this works only with the GUI.
The script command `SetFolderForFrames` still rejects subdirectories, saying "Only a single folder can be entered for this camera type".
This is probably a bug.

## SerialEM usage

### Load a grid

As soon as a grid is loaded, run `SetDirectory Z:\path\to\navs\SampleName` to change the working directory.
This is where crystal images and diffraction snapshots are saved.

Also run `SetFolderForFrames SampleName` to change the movie output path.
As explained above, this sets up the movies to be written to `Z:\TemScripting\BM-Falcon\SampleName`.

### Draw montages

Almost the same as with Ceta, but `Use Montage mapping, not Record parameters` in the grid montage.

### Find good crystals

Same as Ceta.

### Collect diffraction images

Use the `FalconTilt` macro, instead of `SimpleTilt3`.

**Apparently there are some lag (~ 3 seconds?) between the start of frame recording and goniometer rotation.**
When both are set to the same duraction, the last few frames record still images.
This means that the rotation finishes too early.

Because of this, we rotate a bit longer.
We record for 51.0 seconds but rotate 69 degrees, not 65 degrees, at a speed factor of 0.0419 (~ 1.24787 deg/sec).
This corresponds to 54.5, not 52.1, seconds of rotation.

Unfortunately, `TiltDuringRecord` unblanks the beam while the camera is recording *or* the goniometer is moving.
This was confirmed with extreme cases (5 second recording but 20 second rotation and vice versa).
This means that samples are irradiated longer than necessary.

Anyway, our rotation ranges are:

```
k = modulo $navi_idx 4

If $k == 0
  angleStart = 65
  angleEnd = -4
ElseIf $k == 2 # 39, -30
  angleStart = 39
  angleEnd = -30
ElseIf $k == 3 # 24, -45
  angleStart = 24
  angleEnd = -45
ElseIf $k == 1 # 4, -65
  angleStart = 4
  angleEnd = -65
ElseIf $k == -1
  angleStart = 35
  angleEnd = -38
Endif
```

We also have a high tilt mode for crystals with severe preferred orientations.
```
k = modulo $navi_idx 2

If $k == 0
  angleStart = 70
  angleEnd = 1
Else
  angleStart = -1
  angleEnd = -70
Endif
```

## Calibrations 

### Virtual camera distances

The nominal and real camera distances of our Talos Arctica with Falcon 3 are as follows.
These values were first calibrated on March 14, 2024 (values in parenthesis) and reconfirmed on March 7, 2025 after the scope PC upgrade.
Values were tested every 0.5 mm.

- D1050 ~ 978.0 (--) mm, max res ~ 0.86 Å
- D850 ~ 777.0 (777.5) mm, max res ~ 0.68 Å
- D670 ~ 615.5 (615.5) mm, max res ~ 0.54 Å
- D530 ~ 519.5 (520.5) mm, max res ~ 0.45 Å

These values were calibrated by BaZrO3 cubic crystals.
Unfortunately, the literature values are not very consistent:

- J. Materials Science [“Low-temperature thermophysical and crystallographic properties of BaZrO3 perovskite”](https://link.springer.com/article/10.1007/s10853-020-04453-5)  
  says 4.18983(1) Å at 150 K, 4.18878(1) Å at 75 K.
- Physics and Chemistry of Minerals [“Thermal expansion of SrZrO3 and BaZrO3 perovskites”](https://link.springer.com/article/10.1007/BF00200187)  
  says 4.1947 (4) Å at 200 K, 4.1900 (4) Å at 25 K.
 
The overall error is hopefully about 0.3 %.

### Rotation speed

The relationship between SerialEM's speed factor and the physical rotation speed was calibrated on March 9, 2024
by recording Ceta movies on Velox and checking metadata in EMD files.

On March 8, 2025, the rotation speeds were measured again (values in parenthesis).
Variations were up to 0.2 % (except 0.0640).

- 0.0096 ~ 0.28596 deg/sec
- 0.0192 ~ 0.57185 deg/sec (0.57063)
- 0.0256 ~ 0.76246 deg/sec
- 0.0320 ~ 0.95300 deg/sec (0.95229)
- 0.0419 ~ 1.24787 deg/sec (1.25018)
- 0.0480 ~ 1.42956 deg/sec (1.43211)
- 0.0530 ~ 1.57837 deg/sec (1.57944)
- 0.0640 ~ 1.90617 deg/sec (1.90516)

NOTE: for the speed factor 0.0640, the initial test on Mar 8, 2025 gave 1.29305 deg/sec over 20 seconds,
whose difference from the earlier calibration is larger than the others.
When measured again with a larger rotation range (44 seconds), the value (1.90516) became more consistent.
