"""A pipe bridge supports both 32-bit MinGW and 64-bit Python on Windows."""
import ctypes as C,struct,subprocess
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
class Native:
    def __init__(self,path):self.p=subprocess.Popen([str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    def query(self,b,n):self.p.stdin.write(b);self.p.stdin.flush();r=self.p.stdout.read(n);assert len(r)==n;return r
    def test_reset(self):self.query(b'\0',1)
    def cs_crc(self,b,n):return struct.unpack('<H',self.query(b'\1'+struct.pack('<H',n)+b[:n],2))[0]
    def cs_frame(self,t,s,p,n,out):
        length=struct.unpack('<H',self.query(b'\2'+struct.pack('<BHH',t,s,n)+p[:n],2))[0];C.memmove(out,self.p.stdout.read(length),length);return length
    def test_step(self,x,ms,out,f):
        ret=self.query(b'\3'+struct.pack('<I',ms)+C.string_at(x,7),1)[0]
        if ret:C.memmove(out,self.p.stdout.read(448),448);C.memmove(f,self.p.stdout.read(24),24)
        return ret
    def test_receive(self,b,out,seq,n):
        ret=struct.unpack('<H',self.query(b'\4'+bytes([b]),2))[0]
        if ret:
            s,length=struct.unpack('<HH',self.p.stdout.read(4));C.cast(seq,C.POINTER(C.c_uint16))[0]=s;C.cast(n,C.POINTER(C.c_uint16))[0]=length;C.memmove(out,self.p.stdout.read(length),length)
        return ret
    def test_normalize(self,raw,base,out):C.memmove(out,self.query(b'\5'+C.string_at(raw,14)+C.string_at(base,14),7),7)
    def close(self):self.p.stdin.close();self.p.wait(timeout=3)
@pytest.fixture(scope='session')
def native():
    path=ROOT/'build/host_core.exe';result=subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-Ifirmware','firmware/wire.c','firmware/signal.c','tests/native_bridge.c','-o',str(path)],cwd=ROOT,capture_output=True,text=True)
    (ROOT/'build/host-compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    d=Native(path);yield d;d.close()
