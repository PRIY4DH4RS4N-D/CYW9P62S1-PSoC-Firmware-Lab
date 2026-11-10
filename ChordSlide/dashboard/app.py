"""ChordSlide desktop. Sensor data and inference originate on the MCU."""
import sys,json,struct,time
from pathlib import Path
from collections import deque
import numpy as np
from PySide6 import QtCore,QtGui,QtWidgets as W
import pyqtgraph as pg
import serial
from serial.tools import list_ports
from protocol import LABELS
from protocol.link import Link
from ml.data import Recorder,INSTRUCTIONS
ROOT=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[1]))
class SerialWorker(QtCore.QThread):
    frame=QtCore.Signal(object);status=QtCore.Signal(str)
    def __init__(self,port):super().__init__();self.portname=port;self.running=True;self.requests=deque();self.lock=__import__('threading').Lock()
    def command(self,kind,payload=b''):
        with self.lock:self.requests.append((kind,payload))
    def run(self):
        try:
            with serial.Serial(self.portname,115200,timeout=.01,write_timeout=.2) as port:
                link=Link(port);link.command(16);self.status.emit(f'Connected {self.portname} at 115200')
                while self.running:
                    with self.lock:requests=list(self.requests);self.requests.clear()
                    for kind,payload in requests:link.command(kind,payload)
                    frames,logs=link.poll()
                    for f in frames:self.frame.emit(f)
                    for log in logs:self.status.emit(log)
        except Exception as e:self.status.emit(f'Serial error: {e}')
        finally:self.status.emit('Disconnected')
    def stop(self):self.running=False;self.wait(2000)

class Dashboard(W.QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('ChordSlide | CapSense gesture studio');self.resize(1440,920)
        self.worker=None;self.recorder=Recorder();self.samples=deque(maxlen=150000);self.history=deque(maxlen=300);self.times=deque(maxlen=300);self.events=deque(maxlen=5000);self.latencies=deque(maxlen=5000);self.replay=None;self.replay_index=0;self.sample_seq=None;self.previous_ms=None
        self.setStyleSheet('QWidget {background:#111827;color:#e5edf8;font-size:13px;} QPushButton {background:#24344b;border:1px solid #3b526f;padding:9px;border-radius:5px;} QPushButton:hover {background:#2563eb;} QComboBox,QLineEdit,QSpinBox {background:#24344b;padding:6px;} QTabWidget::pane {border:1px solid #334155;} QTabBar::tab {padding:12px 22px;background:#1f2937;} QTabBar::tab:selected {background:#1d4ed8;} QPlainTextEdit,QListWidget {background:#0b1220;}')
        pg.setConfigOptions(antialias=True,background='#0b1220',foreground='#b9c7db')
        central=W.QWidget();self.setCentralWidget(central);layout=W.QVBoxLayout(central)
        title=W.QLabel('CHORDSLIDE   /   Gesture intelligence');title.setStyleSheet('font-size:26px;font-weight:700;color:#67e8f9');layout.addWidget(title)
        top=W.QHBoxLayout();self.ports=W.QComboBox();self.refresh_ports();top.addWidget(self.ports)
        self.button(top,'Refresh ports',self.refresh_ports);self.connect_button=self.button(top,'Connect',self.connect_port);self.button(top,'Ping',lambda:self.send(16));top.addStretch();self.connection=W.QLabel('Offline • hardware not tested');top.addWidget(self.connection);layout.addLayout(top)
        self.tabs=W.QTabWidget();layout.addWidget(self.tabs,1)
        live=W.QWidget();vl=W.QVBoxLayout(live);self.gesture=W.QLabel('Waiting for MCU predictions');self.gesture.setStyleSheet('font-size:28px;color:#a7f3d0');vl.addWidget(self.gesture)
        self.model_status=W.QLabel('Model status unknown');vl.addWidget(self.model_status)
        gl=W.QGridLayout();vl.addLayout(gl,1)
        self.wave=pg.PlotWidget(title='Normalized channels · requested 50 Hz');self.wave.setYRange(0,130);self.wave.addLegend();self.wave.setLabel('bottom','Board time','s');self.wave.setLabel('left','Normalized signal','0–127');gl.addWidget(self.wave,0,0)
        colors=['#f87171','#fbbf24','#34d399','#22d3ee','#60a5fa','#a78bfa','#f472b6'];names=['Button 0','Button 1']+[f'Slider {i}' for i in range(5)]
        self.curves=[self.wave.plot(pen=pg.mkPen(c,width=2),name=n) for c,n in zip(colors,names)]
        self.heat=pg.PlotWidget(title='Seven-channel history heatmap');self.image=pg.ImageItem(axisOrder='row-major');self.heat.addItem(self.image);self.image.setColorMap(pg.colormap.get('viridis'));self.heat.getAxis('left').setTicks([list(enumerate(names))]);gl.addWidget(self.heat,1,0)
        self.probs=pg.PlotWidget(title='MCU class probabilities');self.probs.setYRange(0,1);self.probs.getAxis('bottom').setTicks([list(enumerate(LABELS))]);self.probs.getAxis('bottom').setStyle(tickFont=QtGui.QFont('Segoe UI',8));self.bars=pg.BarGraphItem(x=np.arange(8),height=np.zeros(8),width=.7,brush='#38bdf8');self.probs.addItem(self.bars);gl.addWidget(self.probs,0,1)
        self.timeline=W.QListWidget();gl.addWidget(self.timeline,1,1);self.tabs.addTab(live,'Live studio')
        collection=W.QWidget();cl=W.QVBoxLayout(collection);cl.addWidget(W.QLabel('Guided physical data collection · collect every class in at least four independent sessions.'))
        self.labels=W.QComboBox();self.labels.addItems(LABELS);cl.addWidget(self.labels);self.instruction=W.QLabel(INSTRUCTIONS[0]);self.instruction.setWordWrap(True);cl.addWidget(self.instruction);self.labels.currentIndexChanged.connect(lambda i:self.instruction.setText(INSTRUCTIONS[i]))
        row=W.QHBoxLayout();self.button(row,'Arm next gesture',self.arm);self.button(row,'Save session NPZ',self.save_dataset);self.button(row,'New session',self.new_session);cl.addLayout(row);self.capture=W.QLabel('Connect a board, select a label, arm, then perform the gesture.');cl.addWidget(self.capture)
        self.counts=W.QLabel();cl.addWidget(self.counts);cl.addStretch();self.tabs.addTab(collection,'Collect dataset')
        analytics=W.QWidget();al=W.QVBoxLayout(analytics);self.eval_status=W.QLabel('Load training evaluation.json to inspect a session holdout.');al.addWidget(self.eval_status);self.button(al,'Load evaluation report',self.load_evaluation)
        ag=W.QHBoxLayout();self.matrix=pg.PlotWidget(title='Confusion matrix · true rows / predicted columns');self.matrix_image=pg.ImageItem(axisOrder='row-major');self.matrix.addItem(self.matrix_image);self.matrix_image.setColorMap(pg.colormap.get('viridis'));self.matrix.getAxis('left').setTicks([list(enumerate(LABELS))]);self.matrix.getAxis('bottom').setTicks([list(enumerate(LABELS))]);ag.addWidget(self.matrix)
        self.hist=pg.PlotWidget(title='MCU inference latency histogram');self.hist.setLabel('bottom','Latency','µs');self.histbar=pg.BarGraphItem(x=[0],height=[0],width=1,brush='#a78bfa');self.hist.addItem(self.histbar);ag.addWidget(self.hist);al.addLayout(ag);self.tabs.addTab(analytics,'Analytics')
        settings=W.QWidget();sl=W.QVBoxLayout(settings);self.threshold=W.QSpinBox();self.threshold.setRange(500,990);self.threshold.setValue(800);sl.addWidget(W.QLabel('Confidence threshold (permille)'));sl.addWidget(self.threshold);self.button(sl,'Apply on MCU',lambda:self.send(17,struct.pack('<H',self.threshold.value())))
        sl.addWidget(W.QLabel('Physical navigation: swipe = previous/next tab; tap = next tab; double tap = Live; long press = Collect; combinations = Analytics / Settings.\nUnknown predictions never navigate. Actions are confined to this dashboard.'))
        self.button(sl,'Replay normalized NPZ (synthetic or recorded)',self.load_replay);self.button(sl,'Export samples CSV / Parquet',self.export);sl.addStretch();self.tabs.addTab(settings,'Settings & replay')
        self.log=W.QPlainTextEdit();self.log.setReadOnly(True);self.log.setMaximumBlockCount(1000);self.log.setMaximumHeight(130);layout.addWidget(self.log)
        self.timer=QtCore.QTimer(self);self.timer.timeout.connect(self.redraw);self.timer.start(60)
        self.replay_timer=QtCore.QTimer(self);self.replay_timer.timeout.connect(self.replay_tick);self.replay_timer.setInterval(20)
        self.update_counts()
    def button(self,layout,text,fn):b=W.QPushButton(text);b.clicked.connect(fn);layout.addWidget(b);return b
    def refresh_ports(self):
        self.ports.clear();self.ports.addItems([p.device for p in list_ports.comports()])
    def log_message(self,s):self.log.appendPlainText(time.strftime('%H:%M:%S')+'  '+s)
    def connect_port(self):
        if self.worker:self.worker.stop();self.worker=None;self.connect_button.setText('Connect');return
        if not self.ports.currentText():self.log_message('No serial port selected');return
        self.replay_timer.stop();self.replay=None;self.recorder.segment=__import__('ml.data',fromlist=['Segmenter']).Segmenter();self.previous_ms=None
        self.worker=SerialWorker(self.ports.currentText());self.worker.frame.connect(self.handle);self.worker.status.connect(self.serial_status);self.worker.finished.connect(self.worker_finished);self.worker.start();self.connect_button.setText('Disconnect')
    def worker_finished(self):self.connect_button.setText('Connect');self.worker=None
    def serial_status(self,s):self.connection.setText(s);self.log_message(s)
    def send(self,k,p=b''):
        if self.worker:self.worker.command(k,p)
        else:self.log_message('Connect UART first')
    def handle(self,f):
        try:
            if f.kind==1:
                if len(f.payload)!=39:raise ValueError('sample length')
                v=struct.unpack('<I7H7H7B',f.payload);self.sample(v[0],v[15:],v[1:8],v[8:15],'physical_uart')
            elif f.kind==2:
                if len(f.payload)!=74:raise ValueError('prediction length')
                v=struct.unpack('<IIBBII8f6f',f.payload);self.prediction(v)
            elif f.kind==3:
                v=struct.unpack('<IIII5H',f.payload);self.model_status.setText(f'{"COLLECTED-DATA MODEL" if v[3] else "SYNTHETIC SMOKE MODEL — actions disabled"} | arena {v[2]} bytes | drops {v[1]} | stack free words {v[4:]}')
        except (ValueError,struct.error) as e:self.log_message(f'Protocol payload rejected: {e}')
    def sample(self,ms,x,raw,base,source):
        if self.previous_ms is not None and ((ms-self.previous_ms)&0xffffffff)>40:self.log_message('Sample timing gap: current capture reset')
        self.previous_ms=ms;self.times.append(ms/1000);self.history.append(x);self.samples.append(dict(ms=ms,source=source,**{f'raw{i}':raw[i] for i in range(7)},**{f'baseline{i}':base[i] for i in range(7)},**{f'x{i}':int(x[i]) for i in range(7)}))
        status=self.recorder.sample(x,ms,source)
        if status:self.capture.setText(status);self.update_counts();self.log_message(status)
    def prediction(self,v):
        eid,ms,pred,flags,us,drops=v[:6];p=np.array(v[6:14]);features=v[14:];pred=pred if pred in range(8) else 7
        self.bars.setOpts(height=p);self.latencies.append(us);conf=float(p.max());name=LABELS[pred]
        self.gesture.setText(f'{name.replace("_"," ").upper()}   {conf:.1%}');self.timeline.insertItem(0,f'{ms/1000:8.2f}s  {name}  {conf:.1%}  {us} µs'+('  SMOKE' if flags&2 else ''))
        if self.timeline.count()>500:self.timeline.takeItem(500)
        self.events.append(dict(id=eid,ms=ms,prediction=name,confidence=conf,latency_us=us,flags=flags,drops=drops,probabilities=p.tolist(),features=list(features)))
        if not flags and pred!=7:
            if pred in (0,1,2):self.tabs.setCurrentIndex((self.tabs.currentIndex()+(-1 if pred==0 else 1))%self.tabs.count())
            elif pred==3:self.tabs.setCurrentIndex(0)
            elif pred==4:self.tabs.setCurrentIndex(1)
            elif pred==5:self.tabs.setCurrentIndex(2)
            elif pred==6:self.tabs.setCurrentIndex(3)
    def redraw(self):
        if self.history:
            a=np.asarray(self.history)
            for i,c in enumerate(self.curves):c.setData(np.asarray(self.times),a[:,i])
            self.image.setImage(a.T,levels=(0,127))
        if self.latencies:
            h,e=np.histogram(self.latencies,bins=20);self.histbar.setOpts(x=(e[:-1]+e[1:])/2,height=h,width=np.diff(e)*.9)
    def arm(self):
        if not self.worker or self.replay_timer.isActive():self.log_message('Physical UART connection required to record');return
        self.recorder.arm(self.labels.currentIndex());self.capture.setText('ARMED · '+self.instruction.text())
    def update_counts(self):self.counts.setText('Session '+self.recorder.session+'\n'+' | '.join(f'{s}: {self.recorder.y.count(i)}' for i,s in enumerate(LABELS)))
    def new_session(self):
        if self.recorder.x:
            self.log_message('Save the current session before starting a new one; use Save session NPZ first.')
            if W.QMessageBox.question(self,'New session','Discard current in-memory windows?')!=W.QMessageBox.Yes:return
        self.recorder=Recorder();self.update_counts()
    def save_dataset(self):
        path,_=W.QFileDialog.getSaveFileName(self,'Save labelled session',f'chordslide-{self.recorder.session}.npz','NumPy dataset (*.npz)')
        if path:
            try:self.recorder.save(path);self.log_message(f'Saved physical windows: {path}')
            except Exception as e:self.log_message(str(e))
    def load_evaluation(self):
        path,_=W.QFileDialog.getOpenFileName(self,'Evaluation report',str(ROOT/'models'),'JSON (*.json)')
        if path:
            try:
                d=json.loads(Path(path).read_text());a=np.array(d['confusion_matrix']);assert a.shape==(8,8);self.matrix_image.setImage(a);self.eval_status.setText(d['source']+f" | INT8 macro F1 {d['int8']['macro avg']['f1-score']:.3f}")
            except Exception as e:self.log_message(f'Invalid report: {e}')
    def load_replay(self):
        if self.worker:self.log_message('Disconnect UART before replay');return
        path,_=W.QFileDialog.getOpenFileName(self,'Replay windows',str(ROOT/'models'),'NumPy dataset (*.npz)')
        if path:
            try:
                d=np.load(path,allow_pickle=False);x=d['x'];assert x.ndim==3 and x.shape[1:]==(64,7) and x.dtype==np.uint8 and x.max()<=127
                self.replay=x.reshape(-1,7);self.replay_index=0;self.previous_ms=None;self.recorder.armed=None;self.replay_timer.start();self.connection.setText('REPLAY · visualization only · no host inference');self.log_message(f'Replay source: {str(d["source"])}')
            except Exception as e:self.log_message(f'Invalid replay: {e}')
    def replay_tick(self):
        if self.replay_index>=len(self.replay):self.replay_timer.stop();return
        x=self.replay[self.replay_index];self.sample(self.replay_index*20,x,[0]*7,[0]*7,'replay');self.replay_index+=1
    def export(self):
        path,selected=W.QFileDialog.getSaveFileName(self,'Export sensor data','chordslide.csv','CSV (*.csv);;Parquet (*.parquet)')
        if path:
            try:
                import pandas as pd
                df=pd.DataFrame(self.samples)
                if path.endswith('.parquet'):df.to_parquet(path,index=False)
                else:df.to_csv(path,index=False)
                Path(path+'.events.json').write_text(json.dumps(list(self.events),indent=2));self.log_message('Export complete: '+path)
            except Exception as e:self.log_message(f'Export error: {e}')
    def closeEvent(self,e):
        if self.worker:self.worker.stop()
        self.replay_timer.stop();e.accept()
def main():
    test='--self-test' in sys.argv
    if test:__import__('os').environ['QT_QPA_PLATFORM']='offscreen'
    app=W.QApplication(sys.argv)
    if test:
        fontdir=Path(__import__('os').environ.get('WINDIR','C:/Windows'))/'Fonts'
        for font in ('segoeui.ttf','segoeuib.ttf','segoeuii.ttf'):
            if (fontdir/font).exists():QtGui.QFontDatabase.addApplicationFont(str(fontdir/font))
    app.setFont(QtGui.QFont('Segoe UI',10));window=Dashboard();window.show()
    if test:
        def verify():
            try:
                for t in range(80):window.sample(t*20,[0,0,0,0,80 if t in range(10,15) else 0,0,0],[100]*7,[100]*7,'replay')
                window.prediction([1,200,7,2,123,0]+[.01]*7+[.93]+[0]*6);window.redraw()
                output=Path(sys.argv[sys.argv.index('--self-test-report')+1]) if '--self-test-report' in sys.argv else Path('exe-self-test.json')
                import pandas as pd
                df=pd.DataFrame(window.samples);df.to_csv(str(output)+'.csv',index=False);df.to_parquet(str(output)+'.parquet',index=False)
                window.grab().save(str(output)+'.png')
                output.write_text(json.dumps({'status':'PASS','channels':len(window.curves),'samples':len(window.samples),'physical_records':len(window.recorder.x),'tabs':window.tabs.count(),'csv_parquet_export':True,'hardware':'NOT TESTED'}))
                window.close();app.exit(0)
            except Exception as e:
                Path('exe-self-test-error.txt').write_text(str(e));window.close();app.exit(1)
        QtCore.QTimer.singleShot(300,verify)
    sys.exit(app.exec())
if __name__=='__main__':main()
