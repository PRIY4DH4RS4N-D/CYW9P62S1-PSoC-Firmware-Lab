param()
$ErrorActionPreference='Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)
& .\.venv\Scripts\python.exe -m pytest -q --junitxml=build\host-tests.xml *> build\host-tests.log
if($LASTEXITCODE){throw 'Host tests failed: build/host-tests.log'}
