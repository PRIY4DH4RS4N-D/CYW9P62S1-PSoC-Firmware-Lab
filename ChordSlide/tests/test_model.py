import json
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
def test_int8_model_and_conversion():
    import tensorflow as tf
    from ml.train import quant_predict
    data=(ROOT/'models/chordslide_int8.tflite').read_bytes();i=tf.lite.Interpreter(model_content=data);i.allocate_tensors()
    assert i.get_input_details()[0]['dtype']==np.int8
    assert list(i.get_input_details()[0]['shape'])==[1,64,1,7]
    assert i.get_output_details()[0]['dtype']==np.int8
    d=np.load(ROOT/'models/parity_vectors.npz');p,_=quant_predict(i,d['x'].astype(np.float32)/127)
    assert np.max(np.abs(p-d['p']))==0
    assert np.allclose(p.sum(1),1,atol=.02)
    assert set(x['op_name'] for x in i._get_ops_details()) <= {'CONV_2D','AVERAGE_POOL_2D','RESHAPE','FULLY_CONNECTED','SOFTMAX','DELEGATE'}
    # All model tensors (other than shape constants) must be integer.
    assert all(d['dtype'] in (np.int8,np.int32) for d in i.get_tensor_details())
    report=json.loads((ROOT/'models/evaluation.json').read_text());assert report['source']=='SYNTHETIC SMOKE TEST ONLY'
    assert report['model_bytes']==len(data)

def test_hardware_parity():
    pytest.skip('HARDWARE NOT TESTED: serial enumeration found no ports; run ml.parity on an already-running board')


def test_generated_model_identity():
    import hashlib,re
    data=(ROOT/'models/chordslide_int8.tflite').read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    header=(ROOT/'firmware/model_data.h').read_text()
    assert digest in header and '#define CS_MODEL_TRAINED 0' in header
    source=(ROOT/'firmware/model_data.c').read_text()
    values=source.split('{',1)[1].split('}',1)[0]
    assert bytes(map(int,re.findall(r'\d+',values)))==data
    elf=ROOT/'build/artifacts/ChordSlide.elf'
    if elf.exists():assert data in elf.read_bytes() and digest.encode() in elf.read_bytes()
