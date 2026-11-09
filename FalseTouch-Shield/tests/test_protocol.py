import random
import struct
import subprocess
from protocol import crc16,encode,Decoder,unpack_event,unpack_sample
import pytest

def test_crc_known_vector():
    assert crc16(b'123456789')==0x29b1

def test_all_fragment_sizes():
    data=encode(1,65535,bytes(range(128)))+encode(0x80,0,b'ack')
    for size in range(1,len(data)+1):
        d=Decoder();frames=[]
        for i in range(0,len(data),size):frames+=d.feed(data[i:i+size])
        assert [(f.kind,f.seq,f.payload) for f in frames]==[(1,65535,bytes(range(128))),(128,0,b'ack')]

def test_corruption_and_resync():
    good=encode(2,42,b'payload')
    for i in range(len(good)):
        bad=bytearray(good);bad[i]^=1
        d=Decoder();frames=d.feed(bytes(bad)+b'noise'+good+good)
        # A corrupt length may delay recovery until timeout; a next feed after timeout recovers.
        if len(frames)<2:
            d.last-=1
            frames=d.feed(good+good)
        assert [f.seq for f in frames][-2:]==[42,42]

def test_timeout():
    d=Decoder();d.feed(encode(1,1,b'abc')[:9]);d.last-=1
    assert d.feed(encode(1,2,b'xyz'))[0].seq==2

def test_bad_lengths():
    with pytest.raises(ValueError):encode(1,1,b'x'*129)
    d=Decoder();assert d.feed(b'\xa5\x5a\x01\x01\0\0\xff\xff'+encode(1,4))[0].seq==4
    with pytest.raises(ValueError):unpack_event(b'')
    with pytest.raises(ValueError):unpack_sample(b'')

def test_fuzz_bounded():
    d=Decoder();rng=random.Random(9)
    for _ in range(1000):
        d.feed(rng.randbytes(100))
        assert len(d.buffer)<=137

def test_event_wire_format():
    e=unpack_event(struct.pack('<II6fBBfI',1,20,1,2,3,4,5,6,255,2,0,9))
    assert e['prediction']==255 and e['drops']==9 and e['features']==[1,2,3,4,5,6]
