# Automated data collection with SerialEM

This folder contains macros for automated MicroED data collection with SerialEM.

Some of the macros were originally written by Dr. Haruaki Yanagisawa at University of Tokyo.
Please cite his paper if you use them in your work:

- Hamada et al. "[Spiro-conjugated carbon/heteroatom-bridged p-phenylenevinylenes:
synthesis, properties, and microcrystal electron crystallographic analysis of racemic solid
solutions](https://doi.org/10.1246/bcsj.20200065)" Bulletin of the Chemical Society of Japan, 93.6 (2020)
- Lu et al. "[B/N-doped p-arylenevinylene chromophores: Synthesis, properties, and
microcrystal electron crystallographic study](https://doi.org/10.1021/jacs.0c10337)"
Journal of the American Chemical Society, 142.44 (2020)

## AutoHotKey macros

To controll the beam stop and Verlox, we use [AutoHotKey](https://www.autohotkey.com/).
Please install it to the computer running SerialEM and TEM User Interface.

Our SerialEM macro assumes the AutoHotKey runtime `AutoHotkeyU64.exe` and macros (`*.ahk`) are
located in `E:\SerialEM\ahk_scripts\`. If you place them somewhere else, please update the
`ahk_dir` variables in the SerialEM macro (there are several occurences).

NOTE: If you have a newer version of Advanced Scripting Interface, SerialEM might be
capable of recording movies from Ceta. In this case, you don't need Verlox.
Unfortunately we cannot test this.

Others (e.g. [CRmov](https://serialemscripts.nexperion.net/script/44)) have used a loop
in a SerialEM macro to capture frame by frame. In our test, this led to unpredictable
and highly variable gaps between frames. So we don't recommend this approach.

### Beam stop and Verlox control

`beam_stop_in.ahk` and `beam_stop_out.ahk` inserts and retracts the beam stop, respectively,
by clicking corresponding buttons on the TEM User Interface toolbar (TUI).

The sub-panels on TUI, especially those at bottom right, must be closed beforehand.
Otherwise these macros fail silently.

`start_velox_mov_rec.ahk` clicks the `Movie Record` button on the Verlox acquisition window.
The camera and recording parameters have to be set beforehand.

Depending on the TUI and Verlox version, you might have to update the button coordinates.

**CAREFULLY TEST THIS YOURSELF BEFORE YOUR EXPERIMENT!**
Failure to properly insert a beam stop can permanently damage your detector.
We take no responsibility.

### Ignore focusing errors

SerialEM's `eucentricity by focus` sometimes fails saying:

```
Error in Eucentricity By Focus: the last implied Z change of XX um was too
inconsistent with the previous change of YY um. 
The original Z has been restored.
```

I don't know why but this dialog box cannot be suppressed by `NoMessageBoxOnError`.
This error stalls automated data collection. When this happens in the midnight,
we lose many hours.

Our `ignore_focusing_errors.ahk` AutoHotKey script waits for the dialog box and closes it immediately.
To stop the script, right-click the AutoHotKey icon (the "H" icon) in the system tray.

Note that this only **IGNORES** the problem. This does **NOT** fix it!

The `Acquire at Items` proceeds with the original Z, which can be very off.
Use this as the last resort. 

## SerialEM macros

### Set up illumination conditions

We use the following illumination conditions:

- LM 115x, Spot 8, C2 97.5 % (i.e. spread to cover the detector), CA 150 um for grid montaging.
- SA 2600x, Spot 8, C2 64 % (i.e. spread to cover the detector), CA 50 um, microprobe, defocus 35 um for square montaging.  
  This is stored as low-dose mode "View".
- SA 5300x, Spot 11, C2 34.6 % (parallel), CA 50 um, nanoprobe.  
  This is stored as low-dose mode "Record". This gives ~ 0.05-0.065 e/Å2/sec (the flux is high after gun replacement).
- The same beam as above but DIFF 670 mm, stored as low-dose mode "Trial".

All conditions use gun lens 8. Note that the flux at gun lens 8 is about 40 % of that at gun lens 4.

We assume SerialEM has been set up and well calibrated.
Specifically, SerialEM must be able to draw montages at LM 115x and at the "View" condition and the
coordinate system at these two magnifications must be consistent.
`Rough eucentricity` and `Eucenticity by Focus` must work correctly.

At the beginning of every microscope session:

- Make sure the condenser apertures (150 um and 50 um) are centered.
- Make sure the beam is centered at "View" and "Rec" conditions.
- The direct beam is centered in the diffraction mode.

Note that electron microscopes have hysteresis.
When you switch from LM 115x, always cycle through View, Rec, Trial
*in this order* two times before adjusting the beam.

### Set up camera parameters

In SerialEM, use bin 2 and 1 (or 0.75) second exposure for the "View" and "Trial" conditions.

In Verlox, select `Ceta` and set the followings as the movie recording condition:
-  Readout area and size: `2048 x 2048`
-  Exposure time: `1 s`
-  Frame combining: `1 frame`
-  Series mode: `Continuous`
-  Disable shutter during imaging: `on`
-  Shutter: `Post-specimen`
-  Image correction: `Dark And Gain`
-  Blank beam when idle: `on`
-  Resume view after acquisition: `off`

Click [`Edit`]-[`Preferences`] menu item:
-  Set `Auto save path` to `Z:\path\to\data\raw` (make this folder beforehand).
-  Export all images and maps to 16-bit grayscale TIFF after acuqisition: `off`   
   (We save in the EMD format)
-  For `Filename`, select at least `Date` and `Time` to make sure file names are unique during data collection.

### Draw montages

1.  Switch the scope to the grid montage condition (LM 115x, CA 150 um) and load a grid.
2.  Run `Rough eucentricity`.
3.  From the [`Navigator`]-[`Montage`]-[`Montage Setup`] menu, set up a 4 x 4 montage and press `Start`.   
    We assume you saved the grid montage as `Z:\path\to\data\LMM.mrc` and the
    navigator as `Z:\path\to\data\nav.nav`.
4.  Activate the low-dose mode and switch to the "View" condition.
5.  Insert a 50 um condenser aperture and activate the low-dose mode.
6.  Move the stage to an empty square.  
    Bring down the flu-screen and cycle through View, Record, Trial modes twice *in this order*.  
    If the beam is off after cycling, center it. Bring up the flu-screen.
7.  Open the grid montage and add points at the center of interesting grid squares.
8.  Collapse items in the Navigator.
9.  Set the Acquire flag and set `New file at group`.
10. Select `Open file for Montaged images` and set the number of pieces to 3 x 3.
11. Run the [`Navigator`]-[`Acquire at Items`] menu command.   
    Select `Parameters for Mapping`, Primary Action `Acquire and save image or montage` and `Make Navigator map`.   
    Activate `Rough Eucentricity` `when moved > 400 um` as `Tasks before or after Primary`.   
    Activate `Run Script after Action`, `Chk_Dw_lvl`.
12. Click `Go`. One square takes about 90 seconds.
13. Save the navigator.

### Find good crystals

1.  Run `SetDirectory Z:\path\to\data` to set the working directory to the same place as the navigator.
2.  Open a square montage and add points on crystals.
3.  Collapse items in the Navigator.
4.  Set the Acquire flags.
5.  Go to the `Record` mode and then to the `Trial` mode.
6.  Insert the beam stop.
7.  Run the [`Navigator`]-[`Acquire at Items`] menu command.  
    Select `Parameters for Mapping`, Primary Action `Run script: SaveDiffSnap`.  
    Deactivate everything from `Tasks before or after Primary`.  
    Activate `Run Script after Action` `Chk_Dw_lvl`.
8.  Click `Go`.

This takes diffraction snapshots without rotation.
Images are saved as `Z:\path\to\data\screen-YYYYMMDD_HHMM_N.jpg`, where `N` is the navigator item ID.
One crystal takes about 10 seconds.

### Collect diffraction images

Edit variables in the `SimpleTilt3` macro.

`rotationSpeed = 0.0320` means 1 deg/sec.

`k = modulo $navi_idx 4` means that we use four patterns of start and stop angles depending on the
navigator item ID. The actual ranges are defined in the next `If` block:

```
k = modulo $navi_idx 4
#k = -1

If $k == 0
  angleStart = 45
  angleEnd = -20
ElseIf $k == 1
  angleStart = 35
  angleEnd = -30
ElseIf $k == 2
  angleStart = 25
  angleEnd = -40
ElseIf $k == 3
  angleStart = 15
  angleEnd = -50
ElseIf $k == -1
  angleStart = +33
  angleEnd = -30
Endif
```

In this case, when the item ID is divisible by 4 (i.e. k == 0), the rotation range is +45 to -20 deg.
When the remainder is 1, the range is +35 to -30 deg, and so on.
If you want to use the same range regardless of the item ID, uncomment the `k = -1` line.
The range will be +33 to -30 deg.

1.  Go through snapshots and set the Acquire flags on promising crystals. Save the navigator.
2.  Make sure the beam stop is retracted.
3.  Run the [`Navigator`]-[`Acquire at Items`] menu command.  
    Select `Parameters for Final Data`, Primary Action `Run script: SimpleTilt3`.  
    Activate `Eucentricity by Focus` `when moved > 30 um` and `Realign to Item` `Every item` as `Tasks before or after Primary`.  
    Activate `Run Script after Action` `Chk_Dw_lvl`.
4.  Click `Go`. Every crystal takes about 2 minutes.

This will record diffraction patterns in movies.
This also saves the real space image of the crystal as `Z:\path\to\data\thumb-YYYYMMDD_HHMM_N.jpg`,
where `N` is the navigator item ID.

During the data collection, **DO NOT TOUCH THE MOUSE**.
Manual mouse operation conflicts with AutoHotKey.
