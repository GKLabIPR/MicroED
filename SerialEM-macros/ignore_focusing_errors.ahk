; SerialEM's "eucentricity by focus" sometimes fails saying:
;   Error in Eucentricity By Focus: the last implied Z change of XX um was too
;   inconsistent with the previous change of YY um. The original Z has been restored
;
; I don't know why but this dialog box cannot be suppressed by `NoMessageBoxOnError`.
; This error stalls automated data collection. When this happens in the midnight,
; we lose many hours.
;
; This AutoHotKey script looks for the dialog box and closes it immediately.
; Note that this only IGNORES the problem. This does NOT fix it!
; The `Acquire at Items` proceeds with the original Z, which can be very off.
; Use this as the last resort.

#NoEnv
loop {
	if WinExist("Error ahk_class #32770 ahk_exe SerialEM.exe")
	{
		ControlGetText, DialogText, Static2
		FoundPos := InStr(DialogText, "Error in Eucentricity")

		if FoundPos > 0
		{
			; MsgBox, Found %DialogText%
			ControlClick Button1
		}	
	}
	Sleep 10000
}
