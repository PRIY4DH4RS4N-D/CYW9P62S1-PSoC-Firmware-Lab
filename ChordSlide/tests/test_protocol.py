import ctypes as C
import struct,random,time
import numpy as np
import pytest
from protocol import encode,Decoder,crc16
from protocol.link import Link

def test_crc_known(native):
    assert crc16(b'123456789')==0x29b1
    assert native.cs_crc(b'123456789',9)==0x29b1
@pytest.mark.parametrize('n',[0,1,128,448,512])
def test_wire_cross_language(native,n):
    p=bytes(random.Random(n).randrange(256) for _ in range(n));out=C.create_string_buffer(522)
    size=native.cs_frame(18,65535,p,n,out);expected=encode(18,65535,p)
    assert out.raw[:size]==expected
    d=Decoder();got=[]
    for b in expected:got+=d.feed(bytes([b]))
    assert len(got)==1 and got[0].payload==p
    native.test_reset();seq=C.c_uint16();length=C.c_uint16();result=0
    for b in b'garbage'+expected:result=native.test_receive(b,out,C.byref(seq),C.byref(length))
    assert result==19 and length.value==n and seq.value==65535 and out.raw[:n]==p

def test_corruption_resync(native):
    rng=random.Random(54);good=encode(16,123)
    for trial in range(100):
        frame=bytearray(encode(18,trial,bytes(rng.randrange(256) for _ in range(448))));i=rng.randrange(8,len(frame)-2);frame[i]^=1
        wire=bytes(frame)+good
        got=Decoder().feed(wire);assert len(got)==1 and got[0].seq==123
        native.test_reset();out=C.create_string_buffer(512);s=C.c_uint16();n=C.c_uint16();packets=[]
        for b in wire:
            v=native.test_receive(b,out,C.byref(s),C.byref(n))
            if v:packets.append(s.value)
        assert packets==[123]

def test_length_limit_timeout():
    with pytest.raises(ValueError):encode(1,0,b'x'*513)
    d=Decoder();d.feed(encode(1,0,b'abcdef')[:10]);d.last-=1;d.feed(b'');assert not d.buffer
    assert d.feed(encode(16,2))[0].seq==2
    invalid=b'\xa5\x5a'+struct.pack('<BBHH',1,18,0,513)
    assert Decoder().feed(invalid+encode(16,3))[0].seq==3
class Port:
    in_waiting=0
    def __init__(self):self.sent=[];self.incoming=b''
    def write(self,b):self.sent.append(b)
    def read(self,n):b=self.incoming;self.incoming=b'';return b

def test_ack_retry():
    p=Port();l=Link(p);s=l.command(17,struct.pack('<H',800));l.pending[s][1]-=1;l.poll();assert p.sent[0]==p.sent[1]
    p.incoming=encode(128,0,struct.pack('<HBB',s,17,0));l.poll();assert not l.pending
    s=l.command(16)
    for _ in range(3):
        if s in l.pending:l.pending[s][1]-=1
        frames,logs=l.poll()
    assert s not in l.pending and 'Timeout' in logs[0]
