$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force build | Out-Null
$ErrorActionPreference='Continue' # Windows PowerShell treats native stderr INFO lines as errors.
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onedir --name FalseTouch-Shield --distpath build/dist --workpath build/pyinstaller --exclude-module matplotlib --exclude-module sklearn --exclude-module scipy --exclude-module torch --exclude-module tensorflow --exclude-module IPython --exclude-module notebook --exclude-module jedi --exclude-module pytest --exclude-module numba --exclude-module llvmlite --exclude-module sympy dashboard_launcher.py *> build/pyinstaller.log
$packageExit=$LASTEXITCODE
$ErrorActionPreference='Stop'
if($packageExit){throw 'EXE packaging failed: see build/pyinstaller.log'}
Write-Host 'Executable: build/dist/FalseTouch-Shield/FalseTouch-Shield.exe (distribute the entire folder)'
