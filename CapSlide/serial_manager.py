"""Nonblocking serial transport with injectable clock/factory for fault tests."""
import threading
import time
import serial
from serial.tools import list_ports
from PySide6.QtCore import QObject, Signal
from event_parser import LineDecoder, ProtocolError, CONTROLS

class SerialLink:
    def __init__(self, event, status, error, factory=serial.Serial, clock=time.monotonic):
        self.on_event, self.on_status, self.on_error = event, status, error
        self.factory, self.clock = factory, clock
        self.port = None
        self.stream = None
        self.retry = 0
        self.last_rx = 0
        self.decoder = LineDecoder()
        self.last_seq = None
        self.ready = False
        self.incompatible = False

    def select(self, port):
        self.close()
        self.port, self.retry = port, 0

    def close(self):
        if self.stream:
            try:
                self.stream.close()
            except (OSError, serial.SerialException):
                pass
        self.stream = None
        self.last_seq = None
        self.ready = False
        self.incompatible = False
        self.decoder = LineDecoder()
        self.on_status('Disconnected')

    def poll(self):
        if not self.port:
            return
        now = self.clock()
        try:
            if self.stream is None:
                if now < self.retry:
                    return
                self.stream = self.factory(self.port, 115200, timeout=0, write_timeout=.1)
                self.last_rx = now
                self.on_status('UART open · awaiting CapSlide')
            for e in self.decoder.feed(self.stream.read(512)):
                if isinstance(e, ProtocolError):
                    self.on_error(str(e))
                    continue
                self.last_rx = now
                if e['type'] in ('HELLO','STATUS'):
                    if e.get('controls') != CONTROLS:
                        if not self.incompatible: self.on_error('Firmware update required: expected B1 axis toggle / B2 click')
                        self.incompatible, self.ready = True, False
                        self.on_status('Firmware update required')
                        continue
                    self.incompatible, self.ready = False, True
                if not self.ready: continue
                if e['type'] == 'HELLO':
                    self.last_seq = None
                    self.on_status('Device restart')
                if self.last_seq is not None:
                    delta = (e['seq'] - self.last_seq) & 0xffffffff
                    if delta == 0:
                        self.on_error('duplicate sequence')
                        continue
                    if delta != 1:
                        self.on_error('sequence gap or device restart')
                        self.on_status('Resynchronizing')
                self.last_seq = e['seq']
                self.on_status('Connected')
                self.on_event(e)
            if now - self.last_rx > 2:
                raise serial.SerialException('No valid CapSlide event for 2 seconds')
        except (OSError, serial.SerialException) as exc:
            self.on_error(str(exc))
            self.close()
            self.retry = now + 1

class SerialManager(QObject):
    event = Signal(dict)
    status = Signal(str)
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._selected = None
        self.link = SerialLink(self.event.emit, self.status.emit, self.error.emit)
        self.thread = threading.Thread(target=self._run, name='CapSlide UART', daemon=True)
        self.thread.start()

    @staticmethod
    def ports():
        return [(p.device, p.description) for p in list_ports.comports()]

    def select(self, port):
        with self._lock:
            self._selected = port

    def _run(self):
        while not self._stop.is_set():
            with self._lock:
                port = self._selected
            if port != self.link.port:
                self.link.select(port)
            self.link.poll()
            self._stop.wait(.01)
        self.link.close()

    def stop(self):
        self._stop.set()
        self.thread.join(3)
