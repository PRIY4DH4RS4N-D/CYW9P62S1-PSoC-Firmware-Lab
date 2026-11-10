import argparse,subprocess,sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--clean',action='store_true');a=p.parse_args()
    cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--onefile','--windowed','--name','ChordSlide','--distpath','build/dist','--workpath','build/pyinstaller','--specpath','build','--paths','.','--collect-data','pyqtgraph','--hidden-import','pyarrow','--hidden-import','pandas']
    if a.clean:cmd+=['--clean']
    for name in ['IPython','pytest','notebook','jupyterlab','bokeh','numba','cv2','sympy','dask','distributed','zmq','jedi','tensorflow','torch','scipy','matplotlib','PyQt5','PyQt6','tkinter']:cmd+=['--exclude-module',name]
    cmd+=['dashboard_launcher.py']
    with (ROOT/'build/dashboard-package.log').open('w',encoding='utf-8') as f:result=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if result.returncode:raise SystemExit('Packaging failed: build/dashboard-package.log')
    exe=ROOT/'build/dist/ChordSlide.exe';(ROOT/'build/exe-sha256.json').write_text(json.dumps({'file':exe.name,'bytes':exe.stat().st_size,'sha256':hashlib.sha256(exe.read_bytes()).hexdigest()},indent=2))
    print('Packaged:',exe)
if __name__=='__main__':main()
