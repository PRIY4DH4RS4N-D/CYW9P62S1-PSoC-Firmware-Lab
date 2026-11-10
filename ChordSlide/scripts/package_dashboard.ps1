param([switch]$Clean)
$ErrorActionPreference='Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)
$packageArgs=@('scripts/package_dashboard.py')
if($Clean){$packageArgs+='--clean'}
& .\.venv\Scripts\python.exe @packageArgs
if($LASTEXITCODE){throw 'Packaging failed: build/dashboard-package.log'}
