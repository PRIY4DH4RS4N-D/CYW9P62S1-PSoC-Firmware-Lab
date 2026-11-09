from pathlib import Path
import subprocess
import numpy as np
import pytest
from ml.parity import native_exe,ROOT
from ml.features import Segmenter,baseline
from protocol import encode,crc16

@pytest.fixture(scope='module')
def exe(tmp_path_factory):
    return native_exe(ROOT/'firmware/model.h',tmp_path_factory.mktemp('native'))

def run(exe,mode,text=''):
    return subprocess.run([str(exe),mode],input=text,text=True,capture_output=True,check=True).stdout

def test_shared_framing(exe):
    assert run(exe,'frame').strip()==encode(16,65535,b'\x01\x02\x03').hex()
    assert int(run(exe,'crc',' '.join(str(x) for x in b'123456789')))==crc16(b'123456789')

def test_c_decoder(exe):
    data=b'noise'+encode(16,1,b'x')+encode(17,2,b'\x3c\0')
    assert run(exe,'decode',' '.join(map(str,data))).splitlines()==['16 1 1','17 2 2']
    corrupt=bytearray(encode(16,5,b'abc'));corrupt[-1]^=1
    data=bytes(corrupt)+encode(16,6,b'abc')
    assert run(exe,'decode',' '.join(map(str,data))).strip()=='16 6 3'

def test_feature_parity(exe):
    rng=np.random.default_rng(91)
    data=[];ms=0
    for duration in [1,6,10,65,120,501]:
        for j in range(duration):
            data.append((ms,list(map(int,rng.integers(0,400,7)))));ms+=10
        for _ in range(5):data.append((ms,[0]*7));ms+=10
    s=Segmenter();expected=[]
    for ms,v in data:
        f=s.step(ms,v)
        if f is not None:expected.append(f)
    actual=run(exe,'features','\n'.join(' '.join(map(str,[ms,*v])) for ms,v in data))
    values=np.asarray([[float(v) for v in row.split()] for row in actual.splitlines()])
    np.testing.assert_allclose(values,expected,rtol=1e-6,atol=1e-5)

def test_idle_and_baseline(exe):
    assert run(exe,'features','0 0 0 0 0 0 0 0')==''
    assert [baseline(f) for f in [[100,200,1,0,0,0],[900,200,1,0,0,0],[30,200,1,0,0,0],[100,200,4,0,0,0]]]==[0,1,2,3]

def test_untrained_abstains(exe):
    if 'FT_MODEL_TRAINED 0' in (ROOT/'firmware/model.h').read_text():
        assert run(exe,'infer','100 300 1 200 10 13').strip()=='255 0'
