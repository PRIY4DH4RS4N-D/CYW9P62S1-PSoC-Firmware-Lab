import json
import random
import shutil
import subprocess
from pathlib import Path
import pytest
from event_parser import parse_event, ProtocolError, LineDecoder
from touch_engine import coordinate, TouchEngine, GestureSimulator

def wire(**kw):
    return json.dumps(dict(v=1, seq=0, type='MOVE', mode='X', position=62, **kw))

def test_valid():
    assert parse_event(wire())['position'] == 62

@pytest.mark.parametrize('data', ['{', '[]', 'null', '{}', '{"v":2}',
    '{"v":true,"seq":0,"type":"RELEASE"}',
    '{"v":1,"seq":0,"type":"MOVE","mode":"Z","position":50}',
    '{"v":1,"seq":0,"type":"MOVE","mode":"X","position":101}',
    '{"v":1,"seq":0,"type":"LEFT_CLICK","state":true}',
    '{"v":1,"seq":0,"type":"UNKNOWN"}', b'\xff', 'x'*257])
def test_invalid(data):
    with pytest.raises(ProtocolError):
        parse_event(data)

def test_framing():
    d = LineDecoder()
    assert list(d.feed(wire().encode()[:10])) == []
    assert list(d.feed(wire().encode()[10:] + b'\n'))[0]['type'] == 'MOVE'
    events = list(d.feed(b'x'*10000 + b'\n' + wire().encode() + b'\n'))
    assert len(events) == 2 and isinstance(events[0], ProtocolError)
    assert events[1]['position'] == 62 and not d.buffer

def test_coordinates():
    assert [coordinate(p, 1001) for p in (-10, 0, 50, 100, 200)] == [0, 0, 500, 1000, 1000]
    assert coordinate(50, 1) == 0

def test_engine_axes_and_release():
    e = TouchEngine()
    e.apply(parse_event(wire()), 1001, 701)
    assert e.tx == 620 and e.ty == 200
    e.apply(dict(type='MOVE', mode='Y', position=50), 1001, 701)
    assert (e.tx,e.ty)==(200,200)  # changing axis cancels old motion and anchors
    e.apply(dict(type='MOVE',mode='Y',position=100),1001,701)
    assert e.tx==200 and e.ty==700
    e.step(.02, 1001, 701)
    e.apply(dict(type='RELEASE'), 1001, 701)
    assert (e.tx, e.ty) == (e.x, e.y) and not e.active

def test_smoothing_is_time_based():
    a, b = TouchEngine(), TouchEngine()
    a.tx = b.tx = 900
    a.step(.1, 1000, 800)
    for _ in range(10):
        b.step(.01, 1000, 800)
    assert a.x == pytest.approx(b.x)
    assert 200 < a.x < 900

def test_button_state_and_lost_release():
    e = TouchEngine()
    assert e.apply(dict(type='LEFT_CLICK', state=1), 900, 700) == ('left', True)
    assert e.apply(dict(type='LEFT_CLICK', state=1), 900, 700) is None
    assert e.apply(dict(type='STATUS', mode='X', b1=1,b2=0), 900, 700) == ('left', False)
    e.reset()
    assert not e.left

def test_tap_hold_and_drag():
    g = GestureSimulator()
    assert g.sample(0, True, True, -1) == []
    assert g.sample(20, False, True, -1) == []  # B1 bounce rejected
    events=g.sample(30,False,True,-1)
    assert [(e['type'],e.get('state')) for e in events]==[('BUTTON',1),('LEFT_CLICK',1)]
    g.sample(100,False,False,-1)
    assert g.sample(130,False,False,-1)[-1]['state']==0
    g.sample(200,True,True,20)
    events=g.sample(230,True,True,40)
    assert [e['type'] for e in events]==['MODE','BUTTON','BUTTON','LEFT_CLICK','MOVE']
    assert events[0]['mode']=='Y' and events[-1]['mode']=='Y'
    events=g.sample(580,True,True,80)
    assert [e['type'] for e in events]==['MOVE']  # holds don't toggle again
    g.sample(600,False,False,-1)
    events=g.sample(630,False,False,-1)
    assert [e['type'] for e in events]==['BUTTON','BUTTON','LEFT_CLICK']
    assert events[-1]['state']==0 and g.vertical  # release retains axis

def test_actual_firmware_parity(tmp_path):
    root = Path(__file__).resolve().parents[1]
    compiler = shutil.which('gcc')
    assert compiler, 'Install host GCC to verify the actual firmware state machine'
    exe = tmp_path / 'gesture.exe'
    subprocess.run([compiler, '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', str(root/'firmware'),
        str(root/'firmware/gesture.c'), str(root/'tests/gesture_harness.c'), '-o', str(exe)], check=True)
    rng = random.Random(42)
    samples = [(ms, rng.random()<.7, rng.random()<.9, rng.choice([-1, 0, 25, 50, 100]))
               for ms in range(0, 30000, 10)]
    # Append long holds and deliberate transitions, including simultaneous input.
    samples += [(ms, ms < 31000, ms < 32000, 60 if ms<32500 else -1)
                for ms in range(30000, 33000, 10)]
    actual = subprocess.run([str(exe)], input=''.join('%d %d %d %d\n'%s for s in samples),
                            text=True, capture_output=True, check=True).stdout.splitlines()
    sim = GestureSimulator()
    expected = []
    for ms, b1, b2, pos in samples:
        for e in sim.sample(ms, b1, b2, pos):
            value = e.get('position', e.get('state', 0))
            mode = e.get('mode', 'Y' if sim.vertical else 'X')
            kind='BUTTON'+str(e['button']) if e['type']=='BUTTON' else e['type']
            expected.append(f"{kind} {value} {mode}")
    assert actual == expected
