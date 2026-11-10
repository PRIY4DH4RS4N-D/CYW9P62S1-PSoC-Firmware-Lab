"""Acknowledged serial commands; idempotent retries preserve sequence numbers."""
import struct,time
from protocol import encode,Decoder
class Link:
    def __init__(self,port):self.port=port;self.decoder=Decoder();self.seq=0;self.pending={};self.last_seq=None;self.lost=0
    def command(self,kind,payload=b''):
        seq=self.seq;self.seq=(seq+1)&65535;wire=encode(kind,seq,payload);self.port.write(wire);self.pending[seq]=[wire,time.monotonic(),1,kind];return seq
    def poll(self):
        frames=self.decoder.feed(self.port.read(self.port.in_waiting or 1));events=[]
        for f in frames:
            if self.last_seq is not None:
                gap=(f.seq-self.last_seq-1)&65535
                if gap:self.lost+=gap;events.append(f'RX sequence gap={gap} (loss or device restart)')
            self.last_seq=f.seq
            if f.kind==128:
                if len(f.payload)!=4:events.append('Malformed ACK');continue
                seq,kind,status=struct.unpack('<HBB',f.payload)
                p=self.pending.get(seq)
                if p is not None and kind==p[3]:del self.pending[seq];events.append(f'ACK seq={seq} command={kind} status={status}')
        now=time.monotonic()
        for seq,p in list(self.pending.items()):
            if now-p[1]>.6:
                if p[2]>=3:events.append(f'Timeout seq={seq} after 3 attempts');del self.pending[seq]
                else:self.port.write(p[0]);p[1]=now;p[2]+=1
        return frames,events
