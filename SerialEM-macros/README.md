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

## Install AutoHotKey

To controll the beam stop and Verlox, we use [AutoHotKey](https://www.autohotkey.com/).
Please install it to the computer running SerialEM and TEM User Interface.

Our SerialEM macro assumes the AutoHotKey runtime `AutoHotkeyU64.exe` and macros (`*.ahk`) are
located in `E:\SerialEM\ahk_scripts\`. If you place them somewhere else, please update the
`ahk_dir` variables in the SerialEM macro (there are several occurences).

## Beam stop and Verlox control

`beam_stop_in.ahk` and `beam_stop_out.ahk` inserts and retracts the beam stop, respectively,
by clicking corresponding buttons on the TEM User Interface toolbar (TUI).

The sub-panels on TUI, especially those at bottom right, must be closed beforehand.
Otherwise these macros fail silently.

`start_velox_mov_rec.ahk` clicks the `Movie Record` button on the Verlox acquisition window.
The camera and recording parameters have to be set beforehand.

Depending on the TUI and Verlox version, you might have to update the button coordinates.

**CAREFULLY TEST YOURSELF BEFORE YOUR EXPERIMENT!**
Failure to properly insert a beam stop can permanently damage your detector.
We take no responsibility.

## Ignore focusing errors

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
