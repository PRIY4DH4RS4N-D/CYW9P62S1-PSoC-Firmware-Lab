import json
import serial
from serial_manager import SerialLink
from event_parser import CONTROLS

def hello(seq=0):
    return json.dumps(dict(v=1,seq=seq,type='HELLO',device='CapSlide',controls=CONTROLS)).encode()+b'\n'

class Port:
    def __init__(self):
        self.data = b''
        self.closed = False
        self.fail = False
    def read(self, n):
        if self.fail: raise serial.SerialException('unplugged')
        data, self.data = self.data[:n], self.data[n:]
        return data
    def close(self): self.closed = True

def setup_link(factory=None):
    port, events, statuses, errors, now = Port(), [], [], [], [10.]
    link = SerialLink(events.append, statuses.append, errors.append,
                      factory=factory or (lambda *a, **k: port), clock=lambda: now[0])
    return link, port, events, statuses, errors, now

def test_disconnect_reconnect():
    link, port, events, statuses, errors, now = setup_link()
    link.select('COM99'); link.poll()
    port.data = hello()
    link.poll(); assert len(events) == 1
    port.fail = True; link.poll()
    assert link.stream is None and port.closed and errors == ['unplugged']
    port.fail = False; now[0] += .5; link.poll(); assert link.stream is None
    now[0] += .5; link.poll(); assert link.stream is port

def test_no_device_and_retry():
    def fail(*a, **k): raise serial.SerialException('missing')
    link, _, _, _, errors, now = setup_link(fail)
    link.poll(); assert errors == []
    link.select('COM99'); link.poll(); link.poll()
    assert len(errors) == 1
    now[0] += 1; link.poll(); assert len(errors) == 2

def test_timeout_invalid_and_sequence():
    link, port, events, statuses, errors, now = setup_link()
    link.select('COM99'); link.poll()
    port.data = b'bad\n'
    link.poll(); assert len(errors) == 1 and not events
    port.data = hello()+b''.join(json.dumps(dict(v=1, seq=n, type='RELEASE')).encode()+b'\n' for n in (1, 1, 3))
    link.poll()
    assert len(events) == 3 and 'Resynchronizing' in statuses
    now[0] += 2.1; link.poll(); assert link.stream is None

def test_port_change_discards_partial_frame():
    link, port, events, statuses, errors, now = setup_link()
    link.select('COM1'); link.poll(); port.data = b'{"v":1'
    link.poll(); link.select('COM2'); link.poll()
    port.data = hello()
    link.poll(); assert len(events) == 1 and not errors

def test_old_firmware_is_not_reported_connected():
    link,port,events,statuses,errors,now=setup_link()
    link.select('COM1'); link.poll()
    old=dict(v=1,seq=0,type='STATUS',b1=0,b2=0,position=-1,mode='X',tx_errors=0)
    port.data=json.dumps(old).encode()+b'\n'; link.poll()
    assert not events and 'Firmware update required' in statuses and len(errors)==1
    port.data=hello(1); link.poll()
    assert statuses[-1]=='Connected' and events[-1]['controls']==CONTROLS
