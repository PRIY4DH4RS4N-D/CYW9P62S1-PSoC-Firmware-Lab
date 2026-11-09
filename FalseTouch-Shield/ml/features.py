"""Reference streaming segmentation. Float32 values match portable core.c."""
import numpy as np

class Segmenter:
    def __init__(self, threshold=60):
        self.threshold = threshold
        self.active = False

    def step(self, ms, values):
        values = [int(v) for v in values]
        if len(values) != 7 or any(v < 0 or v > 65535 for v in values):
            raise ValueError('seven uint16 differences required')
        total, peak = sum(values), max(values)
        width = sum(v >= self.threshold for v in values)
        if not self.active and not width:
            return
        if not self.active:
            self.active = True
            self.start = ms
            self.last = 0
            self.n = self.sum = self.peak = self.width = self.travel = self.quiet = 0
            self.previous = sum(i*v for i, v in enumerate(values))*100//total if total else 0
        if width:
            self.last, self.quiet = ms, 0
        else:
            self.quiet += 1
        pos = sum(i*v for i, v in enumerate(values))*100//total if total else self.previous
        self.travel += abs(pos-self.previous)
        self.previous = pos
        self.n += 1
        self.sum += total
        self.peak = max(self.peak, peak)
        self.width = max(self.width, width)
        if self.quiet < 3 and ((ms-self.start)&0xffffffff) < 5000:
            return
        self.active = False
        return np.array([((self.last-self.start)&0xffffffff)+10, self.peak, self.width, self.sum/self.n, self.travel, self.n], dtype=np.float32)

def baseline(f):
    return 3 if f[2] >= 3 else 2 if f[0] < 80 or f[1] < 100 else 1 if f[0] >= 650 else 0
