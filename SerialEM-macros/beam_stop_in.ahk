; This presses the `Beam Stop In` button on the TUI toolbar.
; TUI's subpanels (at the bottom right) must be closed beforehand,
; otherwise this won't work.
;
; CAREFULLY TEST YOURSELF BEFORE YOUR EXPERIMENT!
; Failure to properly insert a beam stop can damage your detector.
;
; Originally written by Haruaki Yanagisawa, University of Tokyo.
; Modified by Takanori Nakane.

#NoEnv

SendMode Input
CoordMode, Mouse, Relative
WinActivate, TEM User Interface
sleep,500
MouseClick, L, 313, 56
