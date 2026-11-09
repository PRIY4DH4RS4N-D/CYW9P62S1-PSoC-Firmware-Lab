"""Exercise the frozen application from an unrelated working directory."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--port'); args=parser.parse_args()
    exe=ROOT/'dist/CapSlide.exe'
    modes=[('disconnected',[]),('simulator',['--simulator'])]
    if args.port: modes.append(('hardware',['--port',args.port]))
    env=os.environ.copy(); env['QT_QPA_PLATFORM']='offscreen'
    env.pop('PYTHONPATH',None); env.pop('PYTHONHOME',None)
    for mode,flags in modes:
        output=ROOT/f'build/exe-{mode}-smoke.json'
        if output.exists(): output.unlink()
        with tempfile.TemporaryDirectory(prefix='CapSlide-exe-') as temp:
            subprocess.run([str(exe),*flags,'--smoke-test',str(output)],cwd=temp,env=env,check=True,timeout=90)
        report=json.loads(output.read_text())
        assert report['ok'] and report['frozen'], report
        if mode=='hardware': assert report['connection']=='Connected' and report['errors']==0, report
        print(mode,report)
    (ROOT/'build/exe-sha256.json').write_text(json.dumps({exe.name:hashlib.sha256(exe.read_bytes()).hexdigest()},indent=2))

if __name__=='__main__': main()
