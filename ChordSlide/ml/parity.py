"""Compare INT8 host outputs to an already running MCU. This never flashes a board."""
import argparse,json,struct,time
from pathlib import Path
import numpy as np
import serial
from protocol.link import Link
from ml.train import quant_predict

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',required=True);p.add_argument('--models',type=Path,default=Path('models'));p.add_argument('--output',type=Path,default=Path('build/device-parity.json'));a=p.parse_args()
    import tensorflow as tf
    model=tf.lite.Interpreter(model_path=str(a.models/'chordslide_int8.tflite'),num_threads=1);model.allocate_tensors()
    d=np.load(a.models/'parity_vectors.npz');expected,_=quant_predict(model,d['x'].astype(np.float32)/127);errors=[];trained=None
    with serial.Serial(a.port,115200,timeout=.02,write_timeout=1) as port:
        link=Link(port);identity=None;seq=link.command(19);until=time.monotonic()+4
        while time.monotonic()<until:
            frames,logs=link.poll()
            for f in frames:
                if f.kind==5 and len(f.payload)==64:identity=f.payload.decode("ascii")
            if identity is not None and seq not in link.pending:break
        digest=__import__("hashlib").sha256((a.models/"chordslide_int8.tflite").read_bytes()).hexdigest()
        if identity!=digest:raise ValueError("MCU model SHA256 does not match host model")
        for x,host in zip(d['x'],expected):
            seq=link.command(18,x.tobytes());until=time.monotonic()+4;device=None
            while time.monotonic()<until:
                frames,logs=link.poll()
                for frame in frames:
                    if frame.kind==3 and len(frame.payload)==26:trained=struct.unpack_from('<I',frame.payload,12)[0]
                    if frame.kind==4 and len(frame.payload)==34:
                        request,*v=struct.unpack('<H8f',frame.payload)
                        if request==seq:device=np.array(v)
                if device is not None and seq not in link.pending:break
            if device is None:raise TimeoutError(f'No MCU parity response seq={seq}')
            errors.append(float(np.max(np.abs(host-device))))
    report={'status':'PASS' if max(errors)<=1/256+.00001 else 'FAIL','model_sha256':__import__('hashlib').sha256((a.models/'chordslide_int8.tflite').read_bytes()).hexdigest(),'vectors':len(errors),'max_probability_error':max(errors),'tolerance':1/256+.00001,'model_trained':trained,'note':'MCU SHA256 verified before probability comparison'}
    a.output.write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['status']=='PASS' else 1)
if __name__=='__main__':main()
