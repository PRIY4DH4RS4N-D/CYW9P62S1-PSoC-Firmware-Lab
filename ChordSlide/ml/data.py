"""Window recorder uses the same fixed-window and normalization contract as firmware."""
from collections import deque
from pathlib import Path
import uuid
import numpy as np
from protocol import LABELS
INSTRUCTIONS=[
 'Move one finger from slider segment 4 to segment 0 in 250-450 ms; release.',
 'Move one finger from slider segment 0 to segment 4 in 250-450 ms; release.',
 'Touch the slider centre for 80-160 ms; release.',
 'Tap the slider centre twice, with a 180-280 ms gap; release.',
 'Hold the slider centre for 700-850 ms; release before one second.',
 'Swipe right, release slider, then touch CapSense button 0 within 200 ms.',
 'Swipe right, release slider, then touch CapSense button 1 within 200 ms.',
 'Record accidental brushes, broad touches and other unsupported motions.']
class Segmenter:
    def __init__(self):self.ring=deque(maxlen=8);self.window=None;self.wait=False;self.last=None;self.start=0
    def feed(self,x,ms):
        x=np.asarray(x,dtype=np.uint8)
        if x.shape!=(7,) or np.any(x>127):raise ValueError('expected seven normalized values 0..127')
        if self.last is not None and (ms-self.last)&0xffffffff>40:self.ring.clear();self.window=None;self.wait=False
        self.last=ms;peak=int(x.max())
        if self.wait:
            if peak<10:self.wait=False
            return None
        if self.window is None and peak>=15:
            self.window=[np.zeros(7,dtype=np.uint8)]*(8-len(self.ring))+list(self.ring);self.start=ms
        if self.window is not None:
            self.window.append(x.copy())
            if len(self.window)==64:
                result=np.asarray(self.window);self.window=None;self.wait=peak>=10;self.ring.clear();return result,peak>=15,self.start
        else:self.ring.append(x.copy())
        return None
class Recorder:
    def __init__(self):self.session=str(uuid.uuid4());self.x=[];self.y=[];self.groups=[];self.timestamps=[];self.armed=None;self.segment=Segmenter()
    def arm(self,label):
        if label not in range(8):raise ValueError('label')
        self.armed=label;self.segment=Segmenter()
    def sample(self,x,ms,source='physical_uart'):
        w=self.segment.feed(x,ms)
        if w is None or self.armed is None:return None
        window,truncated,start=w
        if source!='physical_uart':return 'Ignored: replay is not physical training data'
        if truncated:return 'Rejected: gesture still active at window end; release and retry'
        self.x.append(window);self.y.append(self.armed);self.groups.append(self.session);self.timestamps.append(start);self.armed=None
        return f'Captured {LABELS[self.y[-1]]}; {len(self.x)} windows in this session'
    def save(self,path):
        if not self.x:raise ValueError('No physical windows recorded')
        np.savez_compressed(path,x=np.array(self.x,dtype=np.uint8),y=np.array(self.y,dtype=np.int32),groups=np.array(self.groups),timestamps=np.array(self.timestamps,dtype=np.uint32),source='physical_uart',labels=np.array(LABELS))
