"""Build a single-file Windows executable with only the required Qt modules."""
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    (ROOT/'build').mkdir(exist_ok=True)
    command=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--windowed',
             '--name','CapSlide','--add-data','assets;assets',
             '--exclude-module','PySide6.QtWebEngineCore','--exclude-module','PySide6.QtWebEngineWidgets',
             '--exclude-module','PySide6.QtQml','--exclude-module','PySide6.QtQuick',
             '--exclude-module','numpy','--exclude-module','pytest','main.py']
    with (ROOT/'build/pyinstaller.log').open('w',encoding='utf-8') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    print(ROOT/'dist/CapSlide.exe')

if __name__=='__main__': main()
