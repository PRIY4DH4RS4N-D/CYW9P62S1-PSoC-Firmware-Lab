import sys
import os
import json
import uuid
import struct
from datetime import datetime, timezone
from collections import deque
from pathlib import Path
import pandas as pd
import pyqtgraph as pg
from serial.tools import list_ports
from PySide6 import QtCore, QtGui, QtWidgets
from protocol import LABELS, FEATURES, unpack_sample, unpack_event
from dashboard.transport import SerialWorker

def label(n):
    return LABELS[n] if n in range(4) else 'UNTRAINED / UNKNOWN'

class Dashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FalseTouch-Shield | PSoC 6 Touch Intelligence')
        self.resize(1420, 920)
        self.worker = None
        self.samples, self.events = [], []
        self.history = deque(maxlen=800)
        self.accepted = self.rejected = self.unknown = self.disagree = 0
        self.session = str(uuid.uuid4())
        self.last_sequence = None
        self.sequence_gaps = 0
        self.recording = False
        self.record_path = None
        self.stream = None
        base = QtWidgets.QWidget()
        self.setCentralWidget(base)
        root = QtWidgets.QVBoxLayout(base)
        title = QtWidgets.QLabel('FalseTouch-Shield')
        title.setStyleSheet('font-size: 28px; font-weight: 700; color: #62d6be')
        root.addWidget(title)
        root.addWidget(QtWidgets.QLabel('Seven electrodes • temporal events • recorded-data ML • baseline comparison'))
        bar = QtWidgets.QHBoxLayout()
        self.ports = QtWidgets.QComboBox()
        self.ports.setEditable(True)
        refresh = QtWidgets.QPushButton('Refresh ports')
        refresh.clicked.connect(self.refresh)
        self.connect_button = QtWidgets.QPushButton('Connect')
        self.connect_button.clicked.connect(self.toggle_connection)
        self.threshold = QtWidgets.QSpinBox()
        self.threshold.setRange(10, 4000)
        self.threshold.setValue(60)
        apply = QtWidgets.QPushButton('Set threshold')
        apply.clicked.connect(lambda: self.command(0x11, struct.pack('<H', self.threshold.value())))
        calibration = QtWidgets.QPushButton('Calibrate (hands off)')
        calibration.clicked.connect(lambda: self.command(0x12))
        for w in (self.ports, refresh, self.connect_button, QtWidgets.QLabel('Activity threshold'), self.threshold, apply, calibration):
            bar.addWidget(w)
        root.addLayout(bar)
        self.status = QtWidgets.QLabel('Disconnected — no hardware data received')
        root.addWidget(self.status)
        self.metrics = QtWidgets.QLabel()
        self.prediction = QtWidgets.QLabel('ML: waiting for a physical touch event')
        self.prediction.setStyleSheet('font-size: 20px; padding: 10px; background: #213049')
        root.addWidget(self.prediction)
        root.addWidget(self.metrics)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.plot = pg.PlotWidget(title='Live CapSense differences — buttons 0–1, slider segments 0–4')
        self.plot.addLegend(offset=(8,8))
        self.plot.setLabel('left', 'Difference counts')
        self.plot.setLabel('bottom', 'Board time', units='s')
        self.plot.showGrid(x=True,y=True,alpha=.2)
        colors = ['#55d6be','#ef7198','#78a6ff','#eac66a','#ad90f5','#f59865','#8bd968']
        self.curves = [self.plot.plot(pen=pg.mkPen(c,width=2),name=f'{"Button" if i<2 else "Slider"} {i if i<2 else i-2}') for i,c in enumerate(colors)]
        splitter.addWidget(self.plot)
        self.timeline = pg.PlotWidget(title='Physical event timeline: ML class (unknown = 4)')
        self.timeline.setYRange(-.5,4.5)
        self.timeline.getAxis('left').setTicks([list(enumerate(LABELS+['UNKNOWN']))])
        self.timeline_points = self.timeline.plot(pen=None,symbol='o',symbolBrush='#62d6be')
        self.timeline.setYRange(-.5,4.5,padding=0)
        splitter.addWidget(self.timeline)
        self.table = QtWidgets.QTableWidget(0,8)
        self.table.setHorizontalHeaderLabels(['ID','Time (ms)','ML','Confidence','Baseline','Decision','Label','Drops'])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        splitter.addWidget(self.table)
        root.addWidget(splitter,1)
        footer = QtWidgets.QHBoxLayout()
        self.label_choice = QtWidgets.QComboBox()
        self.label_choice.addItems(LABELS)
        label_button = QtWidgets.QPushButton('Label selected event')
        label_button.clicked.connect(self.label_selected)
        self.record_button = QtWidgets.QPushButton('Start dataset recording')
        self.record_button.clicked.connect(self.toggle_recording)
        export = QtWidgets.QPushButton('Export CSV / Parquet')
        export.clicked.connect(self.export)
        for w in (self.record_button,self.label_choice,label_button,export):footer.addWidget(w)
        root.addLayout(footer)
        self.setStyleSheet('QWidget {background:#121c2b;color:#e3ebf8;font-size:13px} QPushButton,QComboBox,QSpinBox {background:#263950;padding:7px;border:1px solid #3f5674;border-radius:4px} QTableWidget {gridline-color:#304258;}')
        self.refresh()
        self.update_metrics()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.redraw)
        self.timer.start(50)

    def refresh(self):
        current = self.ports.currentText()
        self.ports.clear()
        self.ports.addItems([p.device for p in list_ports.comports()])
        if current:self.ports.setCurrentText(current)

    def toggle_connection(self):
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait(1500)
            self.connect_button.setText('Connect')
            return
        self.last_sequence = None
        self.worker = SerialWorker(self.ports.currentText())
        self.worker.frame.connect(self.on_frame)
        self.worker.status.connect(self.status.setText)
        self.worker.finished.connect(lambda:self.connect_button.setText('Connect'))
        self.worker.start()
        self.connect_button.setText('Disconnect')

    def command(self,kind,payload=b''):
        if not self.worker or not self.worker.isRunning():
            self.status.setText('Connect to a physical board first')
            return
        try:self.worker.command(kind,payload)
        except Exception as e:self.status.setText(str(e))

    def write_record(self,record):
        if self.recording:
            self.stream.write(json.dumps(record)+'\n')
            self.stream.flush()

    def on_frame(self,frame):
        if self.last_sequence is not None and frame.seq != (self.last_sequence+1)&65535:
            self.sequence_gaps += 1
        self.last_sequence = frame.seq
        try:
            if frame.kind==1:
                ms,*v=unpack_sample(frame.payload)
                self.history.append((ms/1000,*v))
                if self.recording:
                    row=dict(kind='sample',session=self.session,ms=ms,values=v,sequence=frame.seq)
                    self.samples.append(row)
                    self.write_record(row)
            elif frame.kind==2:
                event=unpack_event(frame.payload)
                event.update(kind='event',session=self.session,label=None,recorded=self.recording,sequence=frame.seq)
                event['record_path']=self.record_path
                self.events.append(event)
                self.write_record(event)
                p,b=event['prediction'],event['baseline']
                self.accepted += p in (0,1)
                self.rejected += p in (2,3)
                self.unknown += p==255
                self.disagree += p!=255 and (p<2)!=(b<2)
                self.prediction.setText(f'ML: {label(p)} | confidence {event["confidence"]:.1%} | baseline: {label(b)}')
                r=self.table.rowCount()
                self.table.insertRow(r)
                values=[event['event_id'],event['ms'],label(p),f'{event["confidence"]:.1%}',label(b),'Accepted' if p<2 else 'Rejected' if p<4 else 'Unknown','',event['drops']]
                for c,v in enumerate(values):self.table.setItem(r,c,QtWidgets.QTableWidgetItem(str(v)))
                self.table.scrollToBottom()
                self.update_metrics()
            elif frame.kind==3:
                ms,drops,fault,trained=struct.unpack('<IIIB',frame.payload)
                self.status.setText(f'Board live {ms/1000:.1f}s | ML {"trained" if trained else "UNTRAINED"} | device drops {drops} | fault {fault} | sequence gaps {self.sequence_gaps}')
        except (ValueError,struct.error) as error:self.status.setText(f'Protocol payload error: {error}')

    def redraw(self):
        if self.history:
            rows=list(self.history)
            for i,curve in enumerate(self.curves):curve.setData([r[0] for r in rows],[r[i+1] for r in rows])
        events=self.events[-500:]
        self.timeline_points.setData([e['ms']/1000 for e in events],[e['prediction'] if e['prediction']<4 else 4 for e in events])

    def update_metrics(self):
        self.metrics.setText(f'Accepted {self.accepted}    Rejected {self.rejected}    Unknown {self.unknown}    Baseline/ML decision disagreements {self.disagree}')

    def toggle_recording(self):
        if self.recording:
            self.recording=False
            self.stream.close()
            self.record_button.setText('Start dataset recording')
            return
        path,_=QtWidgets.QFileDialog.getSaveFileName(self,'Record physical dataset','touch-session.jsonl','JSON Lines (*.jsonl)')
        if not path:return
        try:
            self.stream=open(path,'a',encoding='utf-8')
            self.record_path=path
            self.session=str(uuid.uuid4())
            self.recording=True
            self.write_record(dict(kind='metadata',session=self.session,source='physical_uart',utc=datetime.now(timezone.utc).isoformat(),threshold=self.threshold.value(),feature_schema=1))
            self.record_button.setText('Stop recording')
        except OSError as e:self.status.setText(str(e))

    def label_selected(self):
        row=self.table.currentRow()
        if row<0:return
        event=self.events[row]
        if not event['recorded']:
            self.status.setText('This event was outside dataset recording; record a new event')
            return
        value=self.label_choice.currentText()
        event['label']=value
        self.table.item(row,6).setText(value)
        record=dict(kind='label',session=event['session'],event_id=event['event_id'],label=value)
        # Labels can be applied after Stop recording, using the last chosen file.
        try:
            with open(event['record_path'],'a',encoding='utf-8') as out:out.write(json.dumps(record)+'\n')
        except OSError as e:self.status.setText(str(e))

    def export(self):
        path,_=QtWidgets.QFileDialog.getSaveFileName(self,'Export event table','touch-events.csv','CSV (*.csv);;Parquet (*.parquet)')
        if not path:return
        rows=[]
        for e in self.events:
            r={k:v for k,v in e.items() if k!='features'}
            r.update(dict(zip(FEATURES,e['features'])))
            rows.append(r)
        try:
            df=pd.DataFrame(rows)
            if path.lower().endswith('.parquet'):df.to_parquet(path,index=False)
            else:df.to_csv(path,index=False)
            if self.samples:
                raw=pd.DataFrame([dict(session=s['session'],ms=s['ms'],**{f'ch{i}':v for i,v in enumerate(s['values'])}) for s in self.samples])
                raw.to_csv(str(Path(path).with_suffix(''))+'-samples.csv',index=False)
            self.status.setText(f'Exported {len(rows)} events')
        except Exception as e:self.status.setText(f'Export failed: {e}')

    def closeEvent(self,event):
        if self.worker:
            self.worker.requestInterruption()
            self.worker.wait(1500)
        if self.stream and not self.stream.closed:self.stream.close()
        event.accept()

def main():
    smoke='--self-test' in sys.argv
    if smoke:os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    app=QtWidgets.QApplication([sys.argv[0]] if smoke else sys.argv)
    # Explicitly register the system font so offscreen previews render on Windows too.
    font_path=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/'segoeui.ttf'
    if font_path.exists():
        font_id=QtGui.QFontDatabase.addApplicationFont(str(font_path))
        families=QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if families:app.setFont(QtGui.QFont(families[0],10))
    pg.setConfigOptions(antialias=True,background='#172337',foreground='#d6e4f5')
    window=Dashboard()
    window.show()
    if smoke:
        app.processEvents()
        destination=Path(sys.argv[sys.argv.index('--self-test')+1])
        report=dict(mode='offline GUI smoke; no hardware connection',curves=len(window.curves),events=len(window.events),frozen=bool(getattr(sys,'frozen',False)))
        destination.write_text(json.dumps(report,indent=2))
        window.grab().save(str(destination.with_suffix('.png')))
        window.close()
        return
    sys.exit(app.exec())

if __name__=='__main__':main()
