param()
$ErrorActionPreference='Continue'
$root=Split-Path $PSScriptRoot -Parent
Set-Location $root
$exe=Join-Path $root 'build\dist\ChordSlide.exe'
$report=Join-Path $root 'build\exe-self-test.json'
$process=Start-Process -FilePath $exe -ArgumentList @('--self-test','--self-test-report',$report) -WindowStyle Hidden -PassThru
if(-not $process.WaitForExit(120000)){$process.Kill();throw 'EXE self-test timed out'}
if($process.ExitCode -ne 0){throw "EXE self-test failed: $($process.ExitCode)"}
if(-not (Test-Path -LiteralPath $report)){throw 'EXE did not produce its self-test report'}
Get-Content -LiteralPath $report
