# Optional: refresh the included local SDK from pinned ModusToolbox manifests.
param([string]$Tools='C:\Infineon\Tools\ModusToolbox\tools_3.9')
$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force build | Out-Null
$env:PATH="$Tools\modus-shell\bin;"+$env:PATH
& make -C firmware "CY_TOOLS_DIR=$($Tools.Replace('\','/'))" getlibs *> build/getlibs.log
if($LASTEXITCODE){throw 'Dependency restoration failed: see build/getlibs.log'}
