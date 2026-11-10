import ctypes as C
import numpy as np
import pytest
from ml.data import Segmenter,Recorder
from ml.train import normalize,load,synthetic

def test_normalization(native):
    rng=np.random.default_rng(45)
    for _ in range(100):
        raw=rng.integers(0,65536,7,dtype=np.uint16);base=rng.integers(0,65536,7,dtype=np.uint16);out=np.zeros(7,np.uint8)
        native.test_normalize(C.c_void_p(raw.ctypes.data),C.c_void_p(base.ctypes.data),C.c_void_p(out.ctypes.data))
        assert np.array_equal(out,normalize(raw,base))

def test_segmentation_replay(native):
    x,y,g=synthetic(2);native.test_reset();host=Segmenter();windows=0;ms=0
    for window in x:
        # Gaps between labelled captures enforce release; host and C see identical samples.
        for row in np.vstack([np.zeros((20,7)),window,np.zeros((80,7))]):
            row=np.rint(row*127).astype(np.uint8);out=np.zeros((64,7),np.uint8);features=np.zeros(6,np.float32)
            ret=native.test_step(C.c_void_p(row.ctypes.data),ms,C.c_void_p(out.ctypes.data),C.c_void_p(features.ctypes.data));result=host.feed(row,ms);ms+=20
            assert bool(ret)==(result is not None)
            if ret:
                assert np.array_equal(out,result[0]);assert bool(ret==2)==result[1];assert np.isfinite(features).all();windows+=1
    assert windows>40

def test_recorder_provenance(tmp_path):
    rec=Recorder();rec.arm(2)
    rows=np.zeros((90,7),np.uint8);rows[10:15,4]=80
    for i,row in enumerate(rows):rec.sample(row,i*20,'replay')
    assert not rec.x
    rec=Recorder();rec.arm(2)
    for i,row in enumerate(rows):rec.sample(row,i*20)
    assert len(rec.x)==1 and rec.armed is None
    path=tmp_path/'recorded.npz';rec.save(path);x,y,g=load([path]);assert x.shape==(1,64,7) and y[0]==2
    np.savez(tmp_path/'fake.npz',source='synthetic')
    with pytest.raises(ValueError):load([tmp_path/'fake.npz'])

def test_gap_resets_and_overflow():
    s=Segmenter();s.feed([0,0,70,0,0,0,0],0)
    s.feed([0]*7,100);assert s.window is None
    s=Segmenter();result=None
    for t in range(56):result=s.feed([0,0,70,0,0,0,0],t*20)
    assert result[1] is True
    for t in range(56,150):assert s.feed([0,0,70,0,0,0,0],t*20) is None
