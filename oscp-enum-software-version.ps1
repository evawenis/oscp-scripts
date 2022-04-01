# The version displayed in "wmic product get name,vendor,version" (CLI) is different
# from one displayed in "Programs and Features" (GUI), so I wrote this script that displays
# the same version as in the latter in CLI.

# thanks
# https://superuser.com/questions/68611/get-list-of-installed-applications-from-windows-command-line

"HKLM:\Software", (%{If([Environment]::Is64BitProcess){"\WOW6432Node"}}), "\Microsoft\Windows\CurrentVersion\Uninstall" -Join "" | Get-ChildItem | Foreach-Object {Get-ItemProperty $_.PSPath} | Select-Object -Property DisplayName,Publisher,DisplayVersion