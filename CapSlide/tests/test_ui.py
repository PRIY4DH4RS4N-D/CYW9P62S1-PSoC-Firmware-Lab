import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PySide6.QtCore import QPoint, Qt, QStandardPaths
from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QTextEdit
from PySide6.QtTest import QTest
from mini_desk import MiniDesk
from widgets.window import ResizeHandle
from app_manager import APPS, calculate

@pytest.fixture(scope='module')
def app():
    app=QApplication.instance() or QApplication([])
    QStandardPaths.setTestModeEnabled(True)
    yield app

@pytest.fixture
def desk(app,tmp_path,monkeypatch):
    monkeypatch.setattr(MiniDesk,'load_settings',lambda self:None)
    d=MiniDesk(simulator=True); d.show(); app.processEvents(); d.timer.stop()
    d.settings_path=tmp_path/'pointer-settings.json'
    yield d
    d.close(); app.processEvents()

def point_at(d, widget, point=None):
    d.engine.resize(d.width(),d.height())
    point=point or widget.rect().center()
    pos=widget.mapTo(d,point)
    d.engine.x=d.engine.tx=pos.x(); d.engine.y=d.engine.ty=pos.y()

def click(d, widget):
    point_at(d,widget)
    d.process_event(dict(type='LEFT_CLICK',state=1))
    d.process_event(dict(type='LEFT_CLICK',state=0))
    QApplication.processEvents()

def test_all_apps_and_virtual_calculator(desk):
    for name in APPS: desk.manager.launch(name)
    desk.manager.activate('Calculator')
    window=desk.manager.windows['Calculator']
    for key in ('7','+','8','='):
        click(desk,next(b for b in window.findChildren(QPushButton) if b.text()==key))
    assert window.findChild(QLineEdit).text()=='15'
    assert len(desk.manager.buttons)==5

def test_virtual_launch_drag_resize_minimize_close(desk):
    icon=next(b for b in desk.canvas.findChildren(QPushButton) if 'Calculator' in b.text())
    click(desk,icon)
    window=desk.manager.windows['Calculator']; old=window.pos()
    point_at(desk,window.bar,QPoint(50,15))
    desk.process_event(dict(type='LEFT_CLICK',state=1))
    desk.engine.x+=55; desk.engine.y+=35; desk.mouse.move()
    desk.process_event(dict(type='LEFT_CLICK',state=0))
    assert window.pos()==old+QPoint(55,35)
    old_size=window.size()
    point_at(desk,window.findChild(ResizeHandle))
    desk.process_event(dict(type='LEFT_CLICK',state=1))
    desk.engine.x+=30; desk.engine.y+=20; desk.mouse.move()
    desk.process_event(dict(type='LEFT_CLICK',state=0))
    assert window.width()==old_size.width()+30
    click(desk,next(b for b in window.bar.findChildren(QPushButton) if b.text()=='—'))
    assert window.isHidden()
    click(desk,desk.manager.buttons['Calculator']); assert window.isVisible()
    click(desk,next(b for b in window.bar.findChildren(QPushButton) if b.text()=='×'))
    assert 'Calculator' not in desk.manager.windows

def test_right_click_and_notes_touch_keyboard(desk):
    desk.engine.x=desk.engine.tx=600; desk.engine.y=desk.engine.ty=400
    desk.process_event(dict(type='RIGHT_CLICK',state=1))
    desk.process_event(dict(type='RIGHT_CLICK',state=0))
    assert desk.context.isVisible()
    click(desk,next(b for b in desk.context.findChildren(QPushButton) if 'Notes' in b.text()))
    window=desk.manager.windows['Notes']; editor=window.findChild(QTextEdit); editor.clear()
    for key in ('h','i','Space','q','⌫'):
        click(desk,next(b for b in window.findChildren(QPushButton) if b.text()==key))
    assert editor.toPlainText()=='hi '

def test_disconnect_cancels_press_without_click(desk):
    desk.simulator=False
    icon=next(b for b in desk.canvas.findChildren(QPushButton) if 'Calculator' in b.text())
    point_at(desk,icon); desk.process_event(dict(type='LEFT_CLICK',state=1))
    desk.serial_status('Disconnected')
    assert not desk.engine.left and not desk.manager.windows
    assert not desk.mouse.targets

def test_safe_calculator():
    assert calculate('(3+4)*2')==14
    with pytest.raises(ValueError): calculate('__import__("os")')

def test_maximize_restore_and_resize_dashboard(desk):
    window=desk.manager.launch('Calculator'); old=window.geometry()
    click(desk,next(b for b in window.bar.findChildren(QPushButton) if b.text()=='□'))
    assert window.maximized and window.geometry()==desk.canvas.rect()
    desk.resize(1200,780); QApplication.processEvents(); desk.fit_windows()
    assert window.geometry()==desk.canvas.rect()
    click(desk,next(b for b in window.bar.findChildren(QPushButton) if b.text()=='□'))
    assert not window.maximized

def test_settings_are_functional_and_saved(desk):
    from PySide6.QtWidgets import QSlider
    import json
    window=desk.manager.launch('Settings')
    window.findChild(QSlider,'setting_sensitivity').setValue(180)
    window.findChild(QSlider,'setting_speed').setValue(200)
    window.findChild(QSlider,'setting_smoothing').setValue(90)
    assert desk.engine.sensitivity==1.8 and desk.engine.speed==2 and desk.engine.smoothing==.09
    assert json.loads(desk.settings_path.read_text())['sensitivity']==1.8

def test_raw_touch_switches_axis_and_drags_window(desk):
    import json
    from event_parser import parse_event
    window=desk.manager.launch('Calculator')
    point_at(desk,window.bar,QPoint(60,15)); old=window.pos()
    desk.engine.reset()
    def sample(ms,b1,b2,p):
        for event in desk.sim.sample(ms,b1,b2,p):
            desk.process_event(parse_event(json.dumps(event)))
    sample(0,False,True,50); sample(30,False,True,50)
    assert desk.engine.left
    sample(60,False,True,75)
    for _ in range(30):
        desk.engine.step(.016,desk.width(),desk.height()); desk.mouse.move()
    assert window.x()>old.x()
    sample(100,True,True,75); sample(130,True,True,75)
    assert desk.engine.mode=='Y' and desk.axis_badge.mode=='Y' and desk.engine.left
    sample(160,False,True,75); sample(190,False,True,75)
    sample(220,False,True,100)
    for _ in range(30):
        desk.engine.step(.016,desk.width(),desk.height()); desk.mouse.move()
    assert window.y()>old.y()
    sample(260,False,False,-1); sample(290,False,False,-1)
    assert not desk.engine.left and not desk.mouse.targets
