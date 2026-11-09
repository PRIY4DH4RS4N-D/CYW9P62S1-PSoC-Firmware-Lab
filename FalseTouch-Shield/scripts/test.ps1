$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force build | Out-Null
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
& .\.venv\Scripts\python.exe -m pytest -q *> build/host-tests.log
if($LASTEXITCODE){throw 'Host tests failed'}
& .\.venv\Scripts\python.exe -m ml.smoke *> build/ml-smoke.log
if($LASTEXITCODE){throw 'Synthetic smoke failed'}
& .\.venv\Scripts\python.exe -m ml.parity ml/synthetic_smoke *> build/ml-parity.log
if($LASTEXITCODE){throw 'Native C model parity failed'}
