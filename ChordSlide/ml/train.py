"""Train/evaluate a temporal CNN. Real training requires session-separated physical data."""
import os
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL','2')
os.environ.setdefault('TF_NUM_INTEROP_THREADS','1')
os.environ.setdefault('TF_NUM_INTRAOP_THREADS','1')
import argparse,json,hashlib,time,shutil
from pathlib import Path
import numpy as np
from protocol import LABELS
ROOT=Path(__file__).resolve().parents[1]

def normalize(raw,baseline):
    return (np.clip(np.asarray(raw,dtype=np.int32)-np.asarray(baseline,dtype=np.int32),0,512)*127//512).astype(np.uint8)

def augment(x,rng):
    out=x.copy().astype(np.float32)
    for i in range(len(out)):
        out[i]=np.roll(out[i],int(rng.integers(-2,3)),axis=0)*rng.uniform(.8,1.2)+rng.normal(0,.015,out[i].shape)
    return np.clip(out,0,1)

def synthetic(n=80):
    """Artificial waveforms for pipeline checks ONLY; not sensor or accuracy evidence."""
    rng=np.random.default_rng(231);xs=[];ys=[];groups=[]
    for session in range(6):
      for label in range(8):
       for trial in range(n):
        x=np.zeros((64,7),np.float32);start=int(rng.integers(8,15));duration=int(rng.integers(12,22));amp=rng.uniform(.35,.9)
        if label in (0,1,5,6):
            for t in range(duration):
                pos=4*t/(duration-1);pos=4-pos if label==0 else pos
                x[start+t,2:]=amp*np.exp(-((np.arange(5)-pos)/.7)**2)
            if label in (5,6):x[start+duration:start+duration+8,label-5]=amp
        elif label==2:x[start:start+5,4]=amp
        elif label==3:x[start:start+5,4]=amp;x[start+15:start+20,4]=amp
        elif label==4:x[start:start+36,4]=amp
        else:
            if trial%3==0:x[:]=rng.uniform(0,.12,x.shape)
            elif trial%3==1:x[start:start+20,:]=rng.uniform(.2,.7,(20,7))
            else:x[start:start+2,2:]=amp
        x=np.clip(x+rng.normal(0,.012,x.shape),0,1);xs.append(x);ys.append(label);groups.append(f'synthetic-{session}')
    return np.asarray(xs),np.asarray(ys),np.asarray(groups)

def load(paths):
    xx=[];yy=[];gg=[]
    for path in paths:
        d=np.load(path,allow_pickle=False)
        if str(d['source'])!='physical_uart':raise ValueError(f'{path}: physical UART provenance required')
        x=d['x'];y=d['y'];g=d['groups']
        if x.shape[1:]!=(64,7) or x.dtype!=np.uint8 or np.any(x>127) or len(x)!=len(y) or len(y)!=len(g):raise ValueError('invalid dataset')
        xx.append(x.astype(np.float32)/127);yy.append(y);gg.append(g)
    if not xx:raise ValueError('Collect physical UART sessions before final training')
    return np.concatenate(xx),np.concatenate(yy),np.concatenate(gg)

def export(data,out,trained):
    h=hashlib.sha256(data).hexdigest()
    (out/'model_data.h').write_text('#pragma once\n#include <stdint.h>\n#define CS_MODEL_TRAINED '+str(int(trained))+'\n#define CS_MODEL_SHA256 "'+h+'"\n#ifdef __cplusplus\nextern "C" {\n#endif\nextern const unsigned char cs_model_data[];\nextern const unsigned int cs_model_size;\n#ifdef __cplusplus\n}\n#endif\n')
    (out/'model_data.c').write_text('#include "model_data.h"\n__attribute__((aligned(16))) const unsigned char cs_model_data[]={\n'+','.join(str(b) for b in data)+'\n};\nconst unsigned int cs_model_size=sizeof(cs_model_data);\n')

def quant_predict(interpreter,x):
    ins=interpreter.get_input_details()[0];outs=interpreter.get_output_details()[0];s,z=ins['quantization'];so,zo=outs['quantization'];results=[];lat=[]
    for row in x:
        q=np.clip(np.floor(row[...,None,:]/s+z+.5),-128,127).astype(np.int8)[None]
        interpreter.set_tensor(ins['index'],q);start=time.perf_counter_ns();interpreter.invoke();lat.append((time.perf_counter_ns()-start)/1000)
        results.append((interpreter.get_tensor(outs['index'])[0].astype(np.int32)-zo)*so)
    return np.asarray(results),lat

def run(x,y,g,out,smoke=False,epochs=20):
    import tensorflow as tf
    from sklearn.metrics import classification_report,confusion_matrix
    from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
    tf.keras.utils.set_random_seed(201);out.mkdir(parents=True,exist_ok=True)
    if len(set(g))<4 or set(y)!=set(range(8)):raise ValueError('Need >=4 independent sessions and all eight labels')
    sessions=sorted(set(g));test=np.isin(g,sessions[-1:]);val=np.isin(g,sessions[-2:-1]);train=~(test|val)
    for mask in (train,val,test):
        if set(y[mask])!=set(range(8)):raise ValueError('Each session split must contain all eight classes')
    inp=tf.keras.Input((64,1,7),name='window')
    v=tf.keras.layers.Conv2D(12,(5,1),strides=(2,1),activation='relu',name='temporal_conv')(inp)
    v=tf.keras.layers.AveragePooling2D((30,1))(v);v=tf.keras.layers.Flatten()(v)
    v=tf.keras.layers.Dense(8,activation='softmax')(v);m=tf.keras.Model(inp,v)
    m.compile(optimizer=tf.keras.optimizers.Adam(.008),loss='sparse_categorical_crossentropy',metrics=['accuracy'])
    rng=np.random.default_rng(42);xt=augment(x[train],rng)[...,None,:]
    hist=m.fit(xt,y[train],validation_data=(x[val][...,None,:],y[val]),epochs=epochs,batch_size=64,verbose=2)
    m.save(out/'float32.keras');floatp=m.predict(x[test][...,None,:],verbose=0)
    fn=tf.function(lambda z:m(z,training=False),input_signature=[tf.TensorSpec([1,64,1,7],tf.float32)])
    frozen=convert_variables_to_constants_v2(fn.get_concrete_function())
    def converter():return tf.lite.TFLiteConverter.from_concrete_functions([frozen])
    c=converter();(out/'float32.tflite').write_bytes(c.convert())
    c=converter();c.optimizations=[tf.lite.Optimize.DEFAULT]
    representative=x[train][:min(512,train.sum())]
    c.representative_dataset=lambda:([row[None,...,None,:].astype(np.float32)] for row in representative)
    c.target_spec.supported_ops=[tf.lite.OpsSet.TFLITE_BUILTINS_INT8];c.inference_input_type=tf.int8;c.inference_output_type=tf.int8
    data=c.convert();(out/'chordslide_int8.tflite').write_bytes(data);export(data,out,not smoke)
    it=tf.lite.Interpreter(model_content=data,num_threads=1);it.allocate_tensors();p,lat=quant_predict(it,x[test])
    vectors=np.rint(np.clip(x[test][:32],0,1)*127).astype(np.uint8)
    parity,_=quant_predict(it,vectors.astype(np.float32)/127)
    np.savez(out/'parity_vectors.npz',x=vectors,p=parity)
    report={'source':'SYNTHETIC SMOKE TEST ONLY' if smoke else 'physical UART; provenance operator asserted','labels':LABELS,'train_sessions':sessions[:-2],'validation_sessions':sessions[-2:-1],'test_sessions':sessions[-1:],'float32':classification_report(y[test],floatp.argmax(1),target_names=LABELS,output_dict=True,zero_division=0),'int8':classification_report(y[test],p.argmax(1),target_names=LABELS,output_dict=True,zero_division=0),'confusion_matrix':confusion_matrix(y[test],p.argmax(1)).tolist(),'int8_float_agreement':float(np.mean(p.argmax(1)==floatp.argmax(1))),'model_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'host_latency_us':{'median':float(np.median(lat)),'p95':float(np.percentile(lat,95))},'mcu_latency':'HARDWARE NOT TESTED','epochs':epochs}
    (out/'evaluation.json').write_text(json.dumps(report,indent=2));(out/'history.json').write_text(json.dumps(hist.history))
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay
    ConfusionMatrixDisplay(np.array(report['confusion_matrix']),display_labels=LABELS).plot(xticks_rotation=60);plt.title(report['source']);plt.tight_layout();plt.savefig(out/'confusion_matrix.png');plt.close()
    np.savez_compressed(out/'smoke_windows.npz',x=np.rint(x[test]*127).astype(np.uint8),y=y[test],groups=g[test],source='synthetic' if smoke else 'physical_uart')
    return report

def main():
    a=argparse.ArgumentParser();a.add_argument('datasets',nargs='*');a.add_argument('--smoke',action='store_true');a.add_argument('--epochs',type=int,default=25);a.add_argument('--output',type=Path,default=ROOT/'models');a.add_argument('--install',action='store_true');args=a.parse_args()
    x,y,g=synthetic(35) if args.smoke else load(args.datasets)
    report=run(x,y,g,args.output,args.smoke,args.epochs)
    if args.install:
        for f in ('model_data.h','model_data.c'):shutil.copy2(args.output/f,ROOT/'firmware'/f)
    print(json.dumps({'source':report['source'],'bytes':report['model_bytes']}))
if __name__=='__main__':main()
