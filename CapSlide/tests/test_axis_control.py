"""Behavioral acceptance tests for the new button mapping and pointer pipeline."""
import json
import math
import pytest
from event_parser import parse_event, ProtocolError
from touch_engine import GestureSimulator, TouchEngine

def move(engine,mode,position,w=1001,h=701):
    e=parse_event(json.dumps(dict(v=1,seq=0,type='MOVE',mode=mode,position=position)))
    return engine.apply(e,w,h)

def test_b1_toggles_once_per_press_without_hold_requirement():
    sim=GestureSimulator()
    for cycle in range(100):
        ms=cycle*1000
        sim.sample(ms,True,False,-1)
        events=sim.sample(ms+30,True,False,-1)
        modes=[e['mode'] for e in events if e['type']=='MODE']
        assert modes==['Y' if cycle%2==0 else 'X']
        assert not any(e['type']=='LEFT_CLICK' for e in events)
        assert sim.sample(ms+900,True,False,-1)==[]
        sim.sample(ms+920,False,False,-1)
        assert [e['type'] for e in sim.sample(ms+950,False,False,-1)]==['BUTTON']

def test_bounce_cannot_repeat_toggle_or_click():
    sim=GestureSimulator(); events=[]
    for ms in range(0,100,10): events+=sim.sample(ms,ms%20==0,ms%20==0,-1)
    assert events==[]
    sim.sample(100,True,True,-1)
    events=sim.sample(130,True,True,50)
    assert [e['type'] for e in events]==['MODE','BUTTON','BUTTON','LEFT_CLICK','MOVE']
    assert sim.sample(900,True,True,50)==[]

@pytest.mark.parametrize('size',[(1120,740),(1440,900),(1920,1080),(800,600),(1,1)])
@pytest.mark.parametrize('axis',['X','Y'])
def test_all_five_positions_and_full_range(axis,size):
    engine=TouchEngine(); w,h=size
    engine.resize(w,h)
    if axis=='Y':
        move(engine,axis,50,w,h)  # anchor the switched axis
    fixed=engine.y if axis=='X' else engine.x
    targets=[]
    for p in (0,25,50,75,100):
        move(engine,axis,p,w,h)
        targets.append(engine.tx if axis=='X' else engine.ty)
        for _ in range(120): engine.step(1/60,w,h)
        actual=engine.x if axis=='X' else engine.y
        assert actual==pytest.approx(targets[-1],abs=.01)
        assert (engine.y if axis=='X' else engine.x)==pytest.approx(fixed)
    assert targets==sorted(targets)
    assert targets[0]==0 and targets[-1]==(w-1 if axis=='X' else h-1)

def test_axis_switch_anchors_without_jump_even_while_dragging():
    e=TouchEngine(); e.apply(dict(type='LEFT_CLICK',state=1),1001,701)
    move(e,'X',90); e.step(.03,1001,701)
    before=e.x,e.y
    e.apply(dict(type='MODE',mode='Y'),1001,701)
    move(e,'Y',90)
    for _ in range(10): e.step(.016,1001,701)
    assert (e.x,e.y)==before and e.left
    move(e,'Y',100); assert e.ty==700
    move(e,'Y',0); assert e.ty==0
    assert e.tx==before[0]

@pytest.mark.parametrize('edge',[0,100])
def test_axis_switch_at_endpoint_uses_pickup(edge):
    e=TouchEngine(); move(e,'Y',edge)
    assert e.pickup and e.ty==200
    move(e,'Y',50 if edge==0 else 25); assert not e.pickup
    move(e,'Y',0); assert e.ty==0
    move(e,'Y',100); assert e.ty==700

def test_status_uses_b2_not_b1_for_drag_release():
    e=TouchEngine(); e.apply(dict(type='LEFT_CLICK',state=1),900,700)
    assert e.apply(dict(type='STATUS',b1=0,b2=1,mode='Y',position=50),900,700) is None
    assert e.left
    assert e.apply(dict(type='STATUS',b1=1,b2=0,mode='Y',position=-1),900,700)==('left',False)
    assert not e.active

def test_normalized_resize_preserves_current_and_target_fraction():
    e=TouchEngine(); move(e,'X',75,1001,701); e.step(.1,1001,701)
    previous=e.x/1000,e.tx/1000,e.y/700
    e.resize(2001,1401)
    assert (e.x/2000,e.tx/2000,e.y/1400)==pytest.approx(previous)

@pytest.mark.parametrize('sensitivity',[.3,1.,3.])
def test_sensitivity_speed_smoothing_and_edges(sensitivity):
    e=TouchEngine(); e.configure(sensitivity=sensitivity,speed=.25,smoothing=0,edge=2)
    move(e,'X',100)
    old=e.x; e.step(.1,1001,701)
    assert e.x-old==pytest.approx(25)
    move(e,'X',1); assert e.tx==0
    move(e,'X',99); assert e.tx==1000
    with pytest.raises(ValueError): e.configure(sensitivity=float('nan'))

def test_long_duration_pipeline_and_repeated_switches():
    sim=GestureSimulator(); engine=TouchEngine(); switches=clicks=0
    # Ten minutes at the real firmware sample interval; no wall-clock sleeping.
    for ms in range(0,600000,10):
        b1=ms%2000<60; b2=100<=ms%3000<900
        position=int(50+50*math.sin(ms/1000))
        for raw in sim.sample(ms,b1,b2,position):
            event=parse_event(json.dumps(raw))
            switches+=event['type']=='MODE'
            clicks+=event['type']=='LEFT_CLICK' and event['state']==1
            engine.apply(event,1440,900)
        engine.step(.01,1440,900)
        assert 0<=engine.x<=1439 and 0<=engine.y<=899
    assert switches==300 and clicks==200

def test_button_event_validation():
    for button in (1,2):
        assert parse_event(json.dumps(dict(v=1,seq=0,type='BUTTON',button=button,state=1)))['button']==button
    with pytest.raises(ProtocolError): parse_event('{"v":1,"seq":0,"type":"BUTTON","button":3,"state":1}')

def test_debounce_tick_wrap():
    s=GestureSimulator()
    assert s.sample(0xfffffff0,True,False,-1)==[]
    assert s.sample(0x0000000e,True,False,-1)[0]['type']=='MODE'
