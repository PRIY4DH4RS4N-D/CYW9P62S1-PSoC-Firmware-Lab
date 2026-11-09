param([switch]$Clean,[string]$Tools='C:\Infineon\Tools\ModusToolbox\tools_3.9',[string]$Compiler='C:\Infineon\Tools\mtb-gcc-arm-eabi\14.2.1\gcc')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
$env:PATH="$Tools\modus-shell\bin;"+$env:PATH
New-Item -ItemType Directory -Force build\artifacts | Out-Null
$argsBuild=@('-C','firmware',"CY_TOOLS_DIR=$($Tools.Replace('\','/'))","CY_COMPILER_GCC_ARM_DIR=$($Compiler.Replace('\','/'))",'-j1')
if($Clean){
 & make @argsBuild clean *> build/firmware-clean.log
 if($LASTEXITCODE){throw 'Firmware clean failed'}
}
& make @argsBuild build *> build/firmware-build.log
if($LASTEXITCODE){throw 'Firmware build failed: see build/firmware-build.log'}
$artifactRoot=Join-Path $projectRoot 'firmware\build\APP_CYW9P62S1-43438EVB-01\Release'
foreach($ext in @('elf','hex','map')){Copy-Item -LiteralPath "$artifactRoot\FalseTouch-Shield.$ext" -Destination build/artifacts -Force}
& "$Compiler\bin\arm-none-eabi-objcopy.exe" -O binary "$artifactRoot\FalseTouch-Shield.elf" build/artifacts/FalseTouch-Shield.bin
& "$Compiler\bin\arm-none-eabi-size.exe" -A "$artifactRoot\FalseTouch-Shield.elf" *> build/memory-sections.txt
& "$Compiler\bin\arm-none-eabi-nm.exe" -u "$artifactRoot\FalseTouch-Shield.elf" *> build/undefined-symbols.txt
if($LASTEXITCODE){throw 'Symbol inspection failed'}
Get-FileHash build/artifacts/* | Format-List | Out-File build/artifact-sha256.txt
Write-Host 'Firmware built. No programming or flashing was performed.'
