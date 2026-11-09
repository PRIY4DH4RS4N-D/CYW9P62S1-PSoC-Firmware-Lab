"""FalseTouch wire protocol, version 1. No hardware emulation."""
import struct
import time
from dataclasses import dataclass

def crc16(data):
    c = 0xffff
    for b in data:
        c ^= b << 8
        for _ in range(8):
            c = ((c << 1) ^ (0x1021 if c & 0x8000 else 0)) & 0xffff
    return c

def encode(kind, seq, payload=b''):
    if len(payload) > 128:
        raise ValueError('payload exceeds 128 bytes')
    body = struct.pack('<BBHH', 1, kind, seq, len(payload)) + payload
    return b'\xa5\x5a' + body + struct.pack('<H', crc16(body))

@dataclass
class Frame:
    kind: int
    seq: int
    payload: bytes

class Decoder:
    def __init__(self):
        self.buffer = bytearray()
        self.errors = 0
        self.last = 0

    def feed(self, data):
        now = time.monotonic()
        if self.buffer and now - self.last > .2:
            self.buffer.clear()
            self.errors += 1
        self.last = now
        self.buffer.extend(data)
        result = []
        while self.buffer:
            i = self.buffer.find(b'\xa5\x5a')
            if i < 0:
                self.buffer[:] = b'\xa5' if self.buffer[-1] == 0xa5 else b''
                break
            del self.buffer[:i]
            if len(self.buffer) < 8:
                break
            version, kind, seq, n = struct.unpack_from('<BBHH', self.buffer, 2)
            if version != 1 or n > 128:
                del self.buffer[0]
                self.errors += 1
                continue
            if len(self.buffer) < n + 10:
                break
            packet = bytes(self.buffer[:n+10])
            if crc16(packet[2:-2]) != struct.unpack_from('<H', packet, n+8)[0]:
                del self.buffer[0]
                self.errors += 1
                continue
            del self.buffer[:n+10]
            result.append(Frame(kind, seq, packet[8:-2]))
        return result

LABELS = ['TAP', 'HOLD', 'GRAZE', 'WIDE']
FEATURES = ['duration_ms', 'peak', 'max_width', 'mean_sum', 'travel', 'samples']

def unpack_sample(payload):
    if len(payload) != 18:
        raise ValueError('invalid sample size')
    return struct.unpack('<I7H', payload)

def unpack_event(payload):
    if len(payload) != 42:
        raise ValueError('invalid event size')
    v = struct.unpack('<II6fBBfI', payload)
    return dict(event_id=v[0], ms=v[1], features=list(v[2:8]), prediction=v[8], baseline=v[9], confidence=v[10], drops=v[11])
