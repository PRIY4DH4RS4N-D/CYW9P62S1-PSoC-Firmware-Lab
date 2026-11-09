import time
import queue
import struct
import serial
from PySide6.QtCore import QThread, Signal
from protocol import Decoder, encode

class SerialWorker(QThread):
    frame = Signal(object)
    status = Signal(str)
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.out = queue.Queue(maxsize=32)
        self.sequence = 0

    def command(self, kind, payload=b''):
        seq = self.sequence
        self.sequence = (seq+1)&65535
        self.out.put_nowait((kind, seq, payload))
        return seq

    def run(self):
        pending = {}
        decoder = Decoder()
        last_frame = time.monotonic()
        try:
            with serial.Serial(self.port, 115200, timeout=.02, write_timeout=.2) as uart:
                self.status.emit('UART open; waiting for board')
                self.command(0x10)
                while not self.isInterruptionRequested():
                    now = time.monotonic()
                    try:
                        kind, seq, payload = self.out.get_nowait()
                        packet = encode(kind, seq, payload)
                        uart.write(packet)
                        pending[seq] = now
                    except queue.Empty:
                        pass
                    for frame in decoder.feed(uart.read(max(1, uart.in_waiting))):
                        last_frame = now
                        if frame.kind == 0x80 and len(frame.payload) == 4:
                            seq, kind, status = struct.unpack('<HBB', frame.payload)
                            pending.pop(seq, None)
                            self.status.emit(f'Board ACK {seq}, command {kind:#x}, status {status}')
                        self.frame.emit(frame)
                    for seq in list(pending):
                        if now-pending[seq] > 2:
                            pending.pop(seq)
                            self.status.emit(f'Command {seq} timed out; outcome unknown')
                    if now-last_frame > 3:
                        self.status.emit('No valid board data for 3 seconds')
                        last_frame = now
        except (serial.SerialException, OSError, ValueError) as error:
            self.status.emit(f'Connection error: {error}')
        self.status.emit('Disconnected')
