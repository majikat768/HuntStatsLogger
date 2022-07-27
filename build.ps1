python -m venv .venv
./.venv/Scripts/activate
pip install -r requirements.txt
pyinstaller main.spec --noconfirm

$wd = ($pwd).Path
$MainPath = "$wd/dist/main/main.exe"
$ShortcutPath = "$wd/HuntStats.exe.lnk"
$WScriptShell = New-Object -ComObject ("WScript.Shell")
$shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$shortcut.WorkingDirectory = $wd
$shortcut.TargetPath = $MainPath
$shortcut.Save()