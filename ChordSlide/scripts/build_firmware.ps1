param([switch]$Clean,[string]$Tools='C:\Infineon\Tools\ModusToolbox\tools_3.9',[string]$Compiler='C:\Infineon\Tools\mtb-gcc-arm-eabi\14.2.1\gcc')
$ErrorActionPreference='Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)
$buildArgs=@('scripts/build_firmware.py','--tools',$Tools,'--compiler',$Compiler)
if($Clean){$buildArgs+='--clean'}
& python @buildArgs
if($LASTEXITCODE){throw 'Firmware build failed; inspect build/firmware-build.log'}
