"""Compile exported model as native C and compare; --port additionally tests MCU."""
import argparse
import json
import subprocess
import tempfile
import shutil
import time
import struct
from pathlib import Path
import numpy as np
from protocol import encode, Decoder

ROOT=Path(__file__).resolve().parents[1]
def native_exe(model,folder):
    folder=Path(folder)
    shutil.copy2(ROOT/'tests/native.c',folder/'native.c')
    if Path(model).resolve() != (folder/'model.h').resolve():
        shutil.copy2(model,folder/'model.h')
    exe=folder/'parity.exe'
    subprocess.run(['gcc','-std=c99','-O2','-I'+str(folder),'-I'+str(ROOT/'firmware'),str(folder/'native.c'),str(ROOT/'firmware/core.c'),'-o',str(exe)],check=True,capture_output=True)
    return exe

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('artifacts',type=Path)
    p.add_argument('--port')
    a=p.parse_args()
    data=np.load(a.artifacts/'parity_vectors.npz')
    vectors=data['x']
    if a.port:
        import serial
        results=[]
        with serial.Serial(a.port,115200,timeout=.05) as uart:
            decoder=Decoder()
            for seq,row in enumerate(vectors):
                uart.write(encode(0x13,seq,struct.pack('<6f',*row)))
                deadline=time.monotonic()+2
                got=None
                while time.monotonic()<deadline and got is None:
                    for frame in decoder.feed(uart.read(max(1,uart.in_waiting))):
                        if frame.kind==4 and len(frame.payload)==7:
                            reply,pred,conf=struct.unpack('<HBf',frame.payload)
                            if reply==seq:got=(pred,conf)
                if got is None:raise TimeoutError(f'MCU inference timed out at {seq}')
                results.append(got)
        mode='MCU UART VERIFIED'
    else:
        with tempfile.TemporaryDirectory() as d:
            exe=native_exe(a.artifacts/'model.h',d)
            result=subprocess.run([str(exe)],input='\n'.join(' '.join(map(str,row)) for row in vectors),text=True,capture_output=True,check=True)
            results=[tuple(map(float,line.split())) for line in result.stdout.splitlines()]
        mode='NATIVE C HOST VERIFIED; MCU NOT TESTED'
    result=np.asarray(results)
    np.testing.assert_array_equal(result[:,0],data['pred'])
    np.testing.assert_allclose(result[:,1],data['confidence'],atol=1e-7,rtol=1e-6)
    report=dict(mode=mode,vectors=len(vectors),predictions_equal=True,confidence_tolerance=1e-7)
    (a.artifacts/('mcu_parity.json' if a.port else 'native_parity.json')).write_text(json.dumps(report,indent=2))
    print(report)
if __name__=='__main__':main()
