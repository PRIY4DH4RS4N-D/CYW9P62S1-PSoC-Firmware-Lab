"""Strict CapSlide v1 NDJSON validation. No hardware or Qt dependency."""
import json

MAX_LINE = 256
CONTROLS = 'toggle-b1-click-b2'
class ProtocolError(ValueError):
    pass

def _integer(e, key, low, high):
    v = e.get(key)
    if type(v) is not int or not low <= v <= high:
        raise ProtocolError(f'{key} must be an integer in {low}..{high}')

def parse_event(line: bytes | str) -> dict:
    try:
        if len(line) > MAX_LINE:
            raise ProtocolError('message too long')
        e = json.loads(line)
        if not isinstance(e, dict):
            raise ProtocolError('expected object')
        _integer(e, 'v', 1, 1)
        _integer(e, 'seq', 0, 0xffffffff)
        kind = e.get('type')
        if kind not in ('MOVE', 'MODE', 'BUTTON', 'LEFT_CLICK', 'RIGHT_CLICK', 'RELEASE', 'STATUS', 'HELLO'):
            raise ProtocolError('unknown event type')
        if kind in ('MOVE', 'MODE', 'STATUS') and e.get('mode') not in ('X', 'Y'):
            raise ProtocolError('invalid axis')
        if kind == 'MOVE':
            _integer(e, 'position', 0, 100)
        if kind.endswith('_CLICK') or kind == 'BUTTON':
            _integer(e, 'state', 0, 1)
        if kind == 'BUTTON':
            _integer(e, 'button', 1, 2)
        if 'controls' in e and not isinstance(e['controls'], str):
            raise ProtocolError('controls must be a string')
        if kind == 'STATUS':
            for key in ('b1', 'b2'):
                _integer(e, key, 0, 1)
            _integer(e, 'position', -1, 100)
            _integer(e, 'tx_errors', 0, 0xffffffff)
        if kind == 'HELLO' and e.get('device') != 'CapSlide':
            raise ProtocolError('unexpected device')
        return e
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ProtocolError(str(exc)) from exc

class LineDecoder:
    def __init__(self):
        self.buffer = bytearray()
        self.discard = False

    def feed(self, data):
        """Yield validated events or ProtocolError; discard overlong frames fully."""
        for byte in data:
            if byte == 10:
                if not self.discard and self.buffer:
                    try:
                        yield parse_event(bytes(self.buffer))
                    except ProtocolError as exc:
                        yield exc
                self.buffer.clear()
                self.discard = False
            elif not self.discard:
                self.buffer.append(byte)
                if len(self.buffer) > MAX_LINE:
                    self.buffer.clear()
                    self.discard = True
                    yield ProtocolError('message too long')
