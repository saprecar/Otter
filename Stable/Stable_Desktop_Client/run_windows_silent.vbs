' [AI-BLOCK: Windows Zero-Terminal Silent Launcher for Otter]
' Launches Otter Desktop UI using pythonw.exe with zero command prompt / console windows.

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objShell = CreateObject("WScript.Shell")
strDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strDir

' 1. Detect pythonw.exe (windowless python)
strPythonw = ""
If objFSO.FileExists(strDir & "\python\pythonw.exe") Then
    strPythonw = """" & strDir & "\python\pythonw.exe"""
ElseIf objFSO.FileExists(strDir & "\Stable\Stable_Desktop_Client\python\pythonw.exe") Then
    strPythonw = """" & strDir & "\Stable\Stable_Desktop_Client\python\pythonw.exe"""
Else
    strPythonw = "pythonw"
End If

' 2. Locate otter_app.py
strApp = ""
If objFSO.FileExists(strDir & "\Dev\desktop\otter_app.py") Then
    strApp = """" & strDir & "\Dev\desktop\otter_app.py"""
    objShell.CurrentDirectory = strDir & "\Dev\desktop"
ElseIf objFSO.FileExists(strDir & "\Stable\Stable_Desktop_Client\otter_app.py") Then
    strApp = """" & strDir & "\Stable\Stable_Desktop_Client\otter_app.py"""
    objShell.CurrentDirectory = strDir & "\Stable\Stable_Desktop_Client"
ElseIf objFSO.FileExists(strDir & "\otter_app.py") Then
    strApp = """" & strDir & "\otter_app.py"""
End If

If strApp = "" Then
    MsgBox "Could not locate otter_app.py in this directory.", 16, "Otter Launch Error"
    WScript.Quit 1
End If

' 0 = Hide console window completely, False = Do not wait for process
objShell.Run strPythonw & " " & strApp, 0, False
