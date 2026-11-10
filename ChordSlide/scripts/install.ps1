param([switch]$WithML)
$ErrorActionPreference='Continue'
$root=Split-Path $PSScriptRoot -Parent
Set-Location $root
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if($LASTEXITCODE){throw 'Dashboard dependency installation failed'}
if($WithML){
 & .\.venv\Scripts\python.exe -m pip install -r ml\requirements.txt
 if($LASTEXITCODE){throw 'ML dependency installation failed'}
}
