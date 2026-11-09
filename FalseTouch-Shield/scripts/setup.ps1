$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force build | Out-Null
python -m venv .venv
if ($LASTEXITCODE) { throw 'venv failed' }
$ErrorActionPreference='Continue'
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
$installExit=$LASTEXITCODE
$ErrorActionPreference='Stop'
if ($installExit) { throw 'Python dependency installation failed. Check build/pip logs and free disk space.' }
& .\.venv\Scripts\python.exe -m pip freeze | Set-Content build/python-environment.txt
