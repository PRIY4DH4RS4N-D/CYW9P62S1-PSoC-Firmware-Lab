import math
import time
import json
from collections import deque
from pathlib import Path
import shiboken6
from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QDateTime, QEvent, QSize, QStandardPaths
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient, QFont, QMouseEvent
from PySide6.QtWidgets import (QApplication, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QSlider, QTextEdit, QScrollArea)
from app_manager import AppManager, APPS
from widgets.pointer import Pointer
from touch_engine import TouchEngine, GestureSimulator
from serial_manager import SerialManager
from widgets.telemetry import AxisBadge, TouchVisual
from widgets.icons import app_icon

class Canvas(QWidget):
    def __init__(self):
        super().__init__(); self.phase=0.; self.axis='X'; self.accent=QColor('#5ce1fc')
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        gradient=QLinearGradient(0,0,self.width(),self.height())
        gradient.setColorAt(0,QColor('#11243a')); gradient.setColorAt(1,QColor('#070e1d'))
        p.fillRect(self.rect(),gradient)
        p.setPen(QPen(QColor('#142a40'),1))
        for x in range(0,self.width(),48): p.drawLine(x,0,x,self.height())
        for y in range(0,self.height(),48): p.drawLine(0,y,self.width(),y)
        cx,cy=int(self.width()*.66),int(self.height()*.47)
        for radius in (130,185,240):
            p.setPen(QPen(QColor('#1c4058'),1)); p.drawEllipse(QPoint(cx,cy),radius,radius)
        p.setPen(QPen(self.accent,2))
        p.drawArc(cx-185,cy-185,370,370,int(self.phase*12)%5760,380)
        p.setPen(QPen(QColor('#27627f'),2))
        p.drawArc(cx-240,cy-240,480,480,-int(self.phase*8)%5760,600)
        p.setPen(QColor('#5ce1fc')); p.setFont(QFont('Segoe UI',11,QFont.DemiBold))
        p.drawText(210,100,'W O R K S P A C E   /   0 1')
        p.setPen(QColor('#e3f4ff')); p.setFont(QFont('Segoe UI',28,QFont.Light))
        p.drawText(210,165,'Your workspace.')
        p.drawText(210,220,'At your fingertips.')
        p.setPen(QColor('#86a4bf')); p.setFont(QFont('Segoe UI',12))
        p.drawText(212,265,'Tap B1 to switch axes. Press B2 to select.')
        p.drawText(212,292,'Hold B2 and slide to drag your workspace.')
        p.setPen(self.accent); p.setFont(QFont('Segoe UI',12,QFont.DemiBold))
        p.drawText(212,340,f'{self.axis} AXIS  /  '+('HORIZONTAL CONTROL' if self.axis=='X' else 'VERTICAL CONTROL'))
        p.setPen(QColor('#47637f')); p.setFont(QFont('Segoe UI',10))
        p.drawText(24,self.height()-28,'PSOC 6  /  CAPACITIVE CONTROL  /  LOCAL WORKSPACE')

class VirtualMouse:
    def __init__(self, root):
        self.root = root
        self.targets = {}
        self.buttons = Qt.NoButton
        self.hovered=None

    def target(self):
        point=QPoint(round(self.root.engine.x),round(self.root.engine.y))
        return self.root.childAt(point) or self.root

    def send(self, widget, kind, button=Qt.NoButton):
        if not shiboken6.isValid(widget): return
        root_point=QPoint(round(self.root.engine.x),round(self.root.engine.y))
        screen=self.root.mapToGlobal(root_point)
        local=widget.mapFromGlobal(screen)
        event=QMouseEvent(kind,QPointF(local),QPointF(screen),button,self.buttons,Qt.NoModifier)
        QApplication.sendEvent(widget,event)

    def edge(self, name, down):
        button=Qt.LeftButton if name=='left' else Qt.RightButton
        if down:
            widget=self.target()
            self.root.manager.focus_at(widget)
            self.targets[name]=widget
            self.buttons |= button
            self.send(widget,QEvent.MouseButtonPress,button)
        else:
            widget=self.targets.pop(name,None)
            self.buttons &= ~button
            if widget is not None: self.send(widget,QEvent.MouseButtonRelease,button)
            if name=='right': self.root.show_context(QPoint(round(self.root.engine.x),round(self.root.engine.y)))

    def move(self):
        widget=self.targets.get('left') or self.target()
        if widget is not self.hovered:
            for target,value in ((self.hovered,False),(widget,True)):
                if target is not None and shiboken6.isValid(target):
                    target.setProperty('touchHover',value)
                    target.style().unpolish(target); target.style().polish(target); target.update()
            self.hovered=widget
        self.send(widget,QEvent.MouseMove)

    def cancel(self):
        # Cancel actions on disconnect: release outside target so buttons don't click.
        old=self.root.engine.x,self.root.engine.y
        self.root.engine.x=self.root.engine.y=-1000
        for name in list(self.targets):
            button=Qt.LeftButton if name=='left' else Qt.RightButton
            widget=self.targets.pop(name)
            self.buttons &= ~button
            self.send(widget,QEvent.MouseButtonRelease,button)
        self.root.engine.x,self.root.engine.y=old

class MiniDesk(QWidget):
    def __init__(self, simulator=False, port=None, record_path=None):
        super().__init__()
        self.setObjectName('root'); self.setWindowTitle('CapSlide · Mini Desk')
        self.resize(1440,900); self.setMinimumSize(1120,740)
        theme=Path(__file__).parent/'assets/theme.qss'
        self.setStyleSheet(theme.read_text(encoding='utf-8'))
        self.engine=TouchEngine(); self.sim=GestureSimulator()
        self.settings_path=Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))/'pointer-settings.json'
        self.theme_name='Cyan'
        self.load_settings()
        self.simulator=simulator; self.sim_b=[False,False]
        self.count=self.errors=0; self.position=-1; self.b1=self.b2=0
        self.device_errors=0
        self.feedback='READY · B1 AXIS / B2 SELECT'
        self.dragging=False; self.press_origin=None
        self.fps=60.; self.event_rate=0.; self.event_times=deque(maxlen=1000)
        self.last_hud=0.
        self.connection='Simulator' if simulator else 'Disconnected'
        self.last='Waiting for touch'; self.port=port; self.ports=[]
        self.started=time.monotonic(); self.last_tick=self.started
        self.record_file=None
        if record_path:
            path=Path(record_path); path.parent.mkdir(parents=True,exist_ok=True)
            self.record_file=path.open('w',encoding='utf-8',buffering=1)
        outer=QVBoxLayout(self); outer.setContentsMargins(16,12,16,12); outer.setSpacing(12)
        header=QFrame(); header.setObjectName('header'); row=QHBoxLayout(header)
        brand=QLabel('CAPSLIDE'); brand.setObjectName('brand'); row.addWidget(brand)
        subtitle=QLabel('MINI DESK    /    TOUCH YOUR WORKSPACE'); subtitle.setObjectName('muted'); row.addWidget(subtitle)
        row.addStretch(); self.connection_label=QLabel(self.connection); row.addWidget(self.connection_label)
        self.axis_badge=AxisBadge(); row.addWidget(self.axis_badge)
        self.date=QLabel(); self.date.setObjectName('muted'); row.addWidget(self.date); outer.addWidget(header)
        center=QHBoxLayout(); outer.addLayout(center,1)
        self.canvas=Canvas(); center.addWidget(self.canvas,1)
        icons=QVBoxLayout(); icons.setContentsMargins(20,24,0,0)
        for name,symbol in APPS.items():
            b=QPushButton(name); b.setIcon(app_icon(name)); b.setIconSize(QSize(34,34)); b.setObjectName('desktopIcon'); b.setFixedWidth(174)
            b.setCheckable(True); b.clicked.connect(lambda checked=False,n=name:self.manager.launch(n))
            icons.addWidget(b)
        icons.addStretch()
        canvas_layout=QHBoxLayout(self.canvas); canvas_layout.addLayout(icons); canvas_layout.addStretch()
        monitor=QFrame(); monitor.setObjectName('monitor'); monitor.setFixedWidth(300)
        panel=QVBoxLayout(monitor); panel.setContentsMargins(18,20,18,16); panel.setSpacing(12)
        title=QLabel('CONTROL DECK'); title.setObjectName('section'); panel.addWidget(title)
        small=QLabel('LIVE INPUT / TWO-AXIS NAVIGATION'); small.setObjectName('muted'); panel.addWidget(small)
        self.port_button=QPushButton('Select COM port'); self.port_button.clicked.connect(self.cycle_port); panel.addWidget(self.port_button)
        refresh=QPushButton('Refresh ports'); refresh.clicked.connect(self.refresh_ports)
        self.sim_button=QPushButton('Simulator: ON' if simulator else 'Simulator: OFF')
        self.sim_button.clicked.connect(self.toggle_sim)
        control_row=QHBoxLayout(); control_row.addWidget(refresh); control_row.addWidget(self.sim_button); panel.addLayout(control_row)
        self.touch_visual=TouchVisual(); panel.addWidget(self.touch_visual)
        self.telemetry=QLabel(); self.telemetry.setWordWrap(True); self.telemetry.setObjectName('muted'); panel.addWidget(self.telemetry)
        self.progress=QProgressBar(); self.progress.setRange(0,100); self.progress.setTextVisible(False); panel.addWidget(self.progress)
        label=QLabel('EVENT STREAM'); label.setObjectName('section'); panel.addWidget(label)
        self.log=QTextEdit(); self.log.setReadOnly(True); self.log.setMinimumHeight(90); self.log.setMaximumHeight(120); self.log.document().setMaximumBlockCount(80); panel.addWidget(self.log,1)
        self.sim_controls=QWidget(); sim_layout=QVBoxLayout(self.sim_controls); sim_layout.setContentsMargins(0,0,0,0)
        sim_layout.addWidget(QLabel('SIMULATOR · physical touch model'))
        buttons=QHBoxLayout(); sim_layout.addLayout(buttons)
        for i in range(2):
            b=QPushButton('B1 Axis' if i==0 else 'B2 Select'); b.pressed.connect(lambda i=i:self.set_sim_button(i,True)); b.released.connect(lambda i=i:self.set_sim_button(i,False)); buttons.addWidget(b)
        self.slider=QSlider(Qt.Horizontal); self.slider.setRange(0,100); self.slider.setValue(50); sim_layout.addWidget(self.slider)
        self.touch_toggle=QPushButton('Slider touch'); self.touch_toggle.setCheckable(True); sim_layout.addWidget(self.touch_toggle)
        sim_layout.addWidget(QLabel('F6: axis toggle · F7: click / hold\n← / →: slide · Space: slider touch'))
        panel.addWidget(self.sim_controls); self.sim_controls.setVisible(simulator)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); scroll.setFixedWidth(316); scroll.setWidget(monitor)
        monitor.setFixedWidth(296); center.addWidget(scroll)
        taskbar=QFrame(); taskbar.setObjectName('taskbar'); task=QHBoxLayout(taskbar)
        launcher=QPushButton('◈   Launch'); launcher.clicked.connect(lambda:self.show_context(QPoint(20,self.height()-300))); task.addWidget(launcher)
        self.task_apps=QHBoxLayout(); task.addLayout(self.task_apps); task.addStretch()
        self.axis_label=QLabel('X  /  IDLE'); task.addWidget(self.axis_label)
        self.clock=QLabel(); self.clock.setObjectName('taskClock'); task.addWidget(self.clock); outer.addWidget(taskbar)
        self.pointer=Pointer(self); self.pointer.show()
        self.manager=AppManager(self); self.mouse=VirtualMouse(self)
        self.set_accent(self.theme_name,persist=False)
        self.context=QFrame(self); self.context.setObjectName('context'); self.context.hide()
        menu=QVBoxLayout(self.context)
        for name in APPS:
            b=QPushButton(APPS[name]+'  '+name)
            b.clicked.connect(lambda checked=False,n=name:(self.context.hide(),self.manager.launch(n))); menu.addWidget(b)
        close=QPushButton('Dismiss'); close.clicked.connect(self.context.hide); menu.addWidget(close)
        self.port_menu=QFrame(self); self.port_menu.setObjectName('context'); self.port_menu.hide()
        self.port_menu_layout=QVBoxLayout(self.port_menu)
        self.serial=SerialManager(self); self.serial.event.connect(self.receive); self.serial.error.connect(self.comm_error); self.serial.status.connect(self.serial_status)
        if port and not simulator: self.serial.select(port)
        self.refresh_ports()
        self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(16)
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, watched, event):
        if isinstance(watched,QWidget) and self.isAncestorOf(watched):
            if event.type()==QEvent.MouseButtonPress:
                self.manager.focus_at(watched)
                if self.context.isVisible() and watched is not self.context and not self.context.isAncestorOf(watched):
                    self.context.hide()
            if self.simulator and event.type() in (QEvent.KeyPress,QEvent.KeyRelease) and event.key() in (Qt.Key_F6,Qt.Key_F7):
                if not event.isAutoRepeat(): self.sim_b[0 if event.key()==Qt.Key_F6 else 1]=event.type()==QEvent.KeyPress
                return True
        return super().eventFilter(watched,event)

    def load_settings(self):
        try:
            saved=json.loads(self.settings_path.read_text(encoding='utf-8'))
            self.engine.configure(**{k:saved[k] for k in ('speed','smoothing','sensitivity','edge') if k in saved})
            if saved.get('theme') in ('Cyan','Blue','Mint'): self.theme_name=saved['theme']
        except (OSError,ValueError,TypeError): pass

    def save_settings(self):
        try:
            self.settings_path.parent.mkdir(parents=True,exist_ok=True)
            saved={key:getattr(self.engine,key) for key in ('speed','smoothing','sensitivity','edge')}
            saved['theme']=self.theme_name
            self.settings_path.write_text(json.dumps(saved,indent=2),encoding='utf-8')
        except OSError as exc: self.log.append('Settings: '+str(exc))

    def set_accent(self,name,persist=True):
        self.theme_name=name
        color={'Cyan':'#52e4ff','Blue':'#659dff','Mint':'#62ffbe'}[name]
        self.pointer.color=QColor(color); self.canvas.accent=QColor(color)
        theme=(Path(__file__).parent/'assets/theme.qss').read_text(encoding='utf-8')
        for original in ('#65e6ff','#62dff7','#5ce5ff','#4acbea','#60dcfa'): theme=theme.replace(original,color)
        self.setStyleSheet(theme)
        if persist: self.save_settings()

    def configure_pointer(self,key,value):
        self.engine.configure(**{key:value}); self.save_settings()

    def set_sim_button(self,i,state): self.sim_b[i]=state

    def refresh_ports(self):
        self.ports=self.serial.ports()
        self.port_button.setText(self.port or ('Select COM port' if self.ports else 'No COM ports · refresh'))

    def cycle_port(self):
        self.refresh_ports()
        while self.port_menu_layout.count():
            item=self.port_menu_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for port,description in self.ports:
            b=QPushButton(port+'  /  '+description)
            b.clicked.connect(lambda checked=False,p=port:self.select_port(p)); self.port_menu_layout.addWidget(b)
        if not self.ports: self.port_menu_layout.addWidget(QLabel('No ports found. Connect KitProg3, then refresh.'))
        b=QPushButton('Disconnect'); b.clicked.connect(lambda:self.select_port(None)); self.port_menu_layout.addWidget(b)
        b=QPushButton('Dismiss'); b.clicked.connect(self.port_menu.hide); self.port_menu_layout.addWidget(b)
        self.port_menu.adjustSize(); point=self.port_button.mapTo(self,QPoint(0,self.port_button.height()+5))
        self.port_menu.move(min(point.x(),self.width()-self.port_menu.width()-16),point.y())
        self.port_menu.show(); self.port_menu.raise_(); self.pointer.raise_()

    def select_port(self,port):
        self.port_menu.hide(); self.mouse.cancel(); self.engine.reset(); self.port=port
        if self.simulator: self.toggle_sim()
        self.serial.select(port); self.port_button.setText(port or 'Select COM port')

    def toggle_sim(self):
        self.mouse.cancel(); self.engine.reset(); self.simulator=not self.simulator
        self.sim=GestureSimulator(); self.sim_b=[False,False]
        self.serial.select(None if self.simulator else self.port)
        self.connection='Simulator' if self.simulator else 'Disconnected'
        self.sim_controls.setVisible(self.simulator)
        self.sim_button.setText('Simulator: ON' if self.simulator else 'Simulator: OFF')

    def serial_status(self,status):
        if self.simulator: return
        if status!='Connected':
            self.mouse.cancel(); self.engine.reset(); self.b1=self.b2=0
            self.dragging=False; self.press_origin=None; self.feedback=status.upper()
        self.connection=status

    def comm_error(self,message):
        if self.simulator: return
        self.errors+=1; self.log.append('UART: '+message)

    def receive(self,event):
        # Ignore stale queued UART events after switching to simulation.
        if not self.simulator:
            self.process_event(event)
            if self.record_file:
                self.record_file.write(json.dumps(dict(received_s=time.monotonic()-self.started,event=event,
                    x=self.engine.x,y=self.engine.y,target_x=self.engine.tx,target_y=self.engine.ty))+'\n')

    def process_event(self,e):
        self.count+=1; self.last=e['type']
        self.event_times.append(time.monotonic())
        if e['type'] in ('MOVE','STATUS'): self.position=e['position']
        elif e['type']=='RELEASE': self.position=-1
        if e['type']=='LEFT_CLICK': self.b2=e['state']
        if e['type']=='BUTTON':
            if e['button']==1: self.b1=e['state']
            else: self.b2=e['state']
        if e['type']=='STATUS':
            self.b1,self.b2=e['b1'],e['b2']
            self.device_errors=e['tx_errors']
        action=self.engine.apply(e,self.width(),self.height())
        if action:
            self.mouse.edge(*action)
            if action[0]=='left':
                if action[1]:
                    self.press_origin=(self.engine.x,self.engine.y); self.dragging=False
                    self.feedback='B2 DOWN · HOLD TO DRAG'
                else:
                    self.feedback='DRAG RELEASED' if self.dragging else 'LEFT CLICK · RELEASED'
                    self.press_origin=None; self.dragging=False
                self.pointer.ripple=.45
        if e['type']=='MODE': self.feedback='AXIS SWITCHED TO '+e['mode']+' · SLIDE TO MOVE'
        if e['type']=='RELEASE': self.feedback='SLIDER RELEASED'+(' · B2 HELD' if self.engine.left else '')
        self.axis_badge.set_mode(self.engine.mode)
        summary=e['type']+'  '+str({k:v for k,v in e.items() if k not in ('v','seq','type')})
        self.log.append(summary)

    def monitor_text(self):
        return (f'LINK   {self.connection}\nPORT   {self.port or "—"}\n\n'
                f'SLIDER   {self.position if self.position>=0 else "released"}\n'
                f'AXIS   {self.engine.mode}    B1  {self.b1}    B2  {self.b2}\n\n'
                f'COORDINATES   {self.engine.x:.1f}, {self.engine.y:.1f}\n'
                f'LAST   {self.last}\nEVENTS   {self.count:,}   RATE   {self.event_rate:.0f}/s\n'
                f'UI FPS   {self.fps:.0f}\nCOMM ERRORS   {self.errors}   DEVICE TX   {self.device_errors}')

    def tick(self):
        now=time.monotonic(); frame_dt=now-self.last_tick; dt=min(.1,frame_dt); self.last_tick=now
        if self.simulator:
            ms=int((now-self.started)*1000)
            pos=self.slider.value() if self.touch_toggle.isChecked() else -1
            for e in self.sim.sample(ms,*self.sim_b,pos): self.process_event(e)
            self.b1,self.b2=map(int,self.sim.stable)
        old=(self.engine.x,self.engine.y)
        self.engine.step(dt,self.width(),self.height())
        if old!=(self.engine.x,self.engine.y): self.mouse.move()
        if self.engine.left and self.press_origin and math.hypot(self.engine.x-self.press_origin[0],self.engine.y-self.press_origin[1])>5:
            self.dragging=True; self.feedback='DRAGGING · HOLD B2'
        self.pointer.advance(self.engine.x,self.engine.y,dt)
        self.pointer.phase=now*4; self.pointer.down=self.engine.left
        self.pointer.axis=self.engine.mode
        self.pointer.update(); self.pointer.raise_()
        self.canvas.phase=now; self.canvas.axis=self.engine.mode; self.canvas.update()
        if frame_dt>0: self.fps=.95*self.fps+.05/frame_dt
        while self.event_times and now-self.event_times[0]>1: self.event_times.popleft()
        self.event_rate=len(self.event_times)
        if now-self.last_hud>.1:
            self.last_hud=now
            self.telemetry.setText(f'{self.count:,} EVENTS   /   {self.event_rate:.0f} PER SEC   /   {self.fps:.0f} FPS\nPC ERRORS {self.errors}   /   DEVICE TX {self.device_errors}')
            self.progress.setValue(max(0,self.position))
            self.touch_visual.position=self.position; self.touch_visual.b1=self.b1; self.touch_visual.b2=self.b2
            self.touch_visual.x,self.touch_visual.y=self.engine.x,self.engine.y
            self.touch_visual.feedback='PICKUP · MOVE SLIDER TOWARD POINTER' if self.engine.pickup else self.feedback
            self.touch_visual.update(); self.axis_badge.set_mode(self.engine.mode)
            self.connection_label.setText('●  '+self.connection)
            self.clock.setText(QDateTime.currentDateTime().toString('HH:mm:ss'))
            self.date.setText(QDateTime.currentDateTime().toString('ddd  dd MMM'))
        self.axis_label.setText(self.engine.mode+'  /  '+('TOUCH ACTIVE' if self.engine.active else 'IDLE'))

    def show_context(self,point):
        self.context.adjustSize()
        self.context.move(max(0,min(point.x(),self.width()-self.context.width())),max(0,min(point.y(),self.height()-self.context.height())))
        self.context.show(); self.context.raise_(); self.pointer.raise_()

    def contextMenuEvent(self,event): self.show_context(event.pos())

    def resizeEvent(self,event):
        if hasattr(self,'pointer'): self.pointer.setGeometry(self.rect())
        if hasattr(self,'manager'): QTimer.singleShot(0,self.fit_windows)
        super().resizeEvent(event)

    def fit_windows(self):
        for window in self.manager.windows.values():
            if window.maximized: window.setGeometry(self.canvas.rect())
            else:
                window.resize(min(window.width(),self.canvas.width()),min(window.height(),self.canvas.height()))
                window.move(max(0,min(window.x(),self.canvas.width()-window.width())),max(0,min(window.y(),self.canvas.height()-window.height())))

    def keyPressEvent(self,event):
        if self.simulator and not event.isAutoRepeat():
            if event.key() in (Qt.Key_F6,Qt.Key_F7): self.sim_b[0 if event.key()==Qt.Key_F6 else 1]=True; return
            if event.key()==Qt.Key_Space: self.touch_toggle.toggle(); return
        if self.simulator and event.key() in (Qt.Key_Left,Qt.Key_Right):
            self.slider.setValue(self.slider.value()+(2 if event.key()==Qt.Key_Right else -2)); return
        super().keyPressEvent(event)

    def keyReleaseEvent(self,event):
        if self.simulator and not event.isAutoRepeat() and event.key() in (Qt.Key_F6,Qt.Key_F7):
            self.sim_b[0 if event.key()==Qt.Key_F6 else 1]=False; return
        super().keyReleaseEvent(event)

    def closeEvent(self,event):
        QApplication.instance().removeEventFilter(self)
        self.timer.stop(); self.mouse.cancel(); self.serial.stop()
        if self.record_file: self.record_file.close(); self.record_file=None
        super().closeEvent(event)
