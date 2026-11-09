"""Interactive local applications; all touch input stays inside this process."""
import ast
import operator
from pathlib import Path
from PySide6.QtCore import Qt, QStandardPaths, QTimer, QSize, QPropertyAnimation
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QListWidget, QSlider, QScrollArea, QGraphicsOpacityEffect)
from widgets.window import DeskWindow
from widgets.icons import app_icon

APPS = {'Calculator': '＋', 'Notes': '≡', 'File Explorer': '▱', 'Settings': '⚙', 'System Monitor': '⌁'}

def calculate(expression):
    if len(expression) > 80:
        raise ValueError('Expression too long')
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        raise ValueError('Use arithmetic only')
    return visit(ast.parse(expression, mode='eval').body)

class AppManager:
    def __init__(self, desk):
        self.desk = desk
        self.windows = {}
        self.buttons = {}

    def launch(self, name):
        if name in self.windows:
            self.activate(name); return self.windows[name]
        window = DeskWindow(name, self.content(name), self.desk.canvas)
        self.windows[name] = window
        offset = (len(self.windows)-1)*24
        window.move(155+offset, 95+offset)
        window.resize(min(560, self.desk.canvas.width()-175), min(520, self.desk.canvas.height()-120))
        window.focused.connect(lambda: self.activate(name))
        window.closed.connect(lambda: self.remove(name))
        button = QPushButton(name); button.setIcon(app_icon(name)); button.setIconSize(QSize(22,22))
        button.setCheckable(True)
        button.clicked.connect(lambda: self.activate(name))
        self.desk.task_apps.addWidget(button)
        self.buttons[name] = button
        window.ensurePolished(); window.layout().activate()
        window.show(); self.activate(name)
        effect=QGraphicsOpacityEffect(window); window.setGraphicsEffect(effect)
        window.fade=QPropertyAnimation(effect,b'opacity',window)
        window.fade.setDuration(180); window.fade.setStartValue(.15); window.fade.setEndValue(1.)
        window.fade.finished.connect(lambda:window.setGraphicsEffect(None)); window.fade.start()
        return window

    def activate(self, name):
        window = self.windows[name]
        window.show(); window.raise_()
        for app, button in self.buttons.items():
            button.setChecked(app == name)
        self.desk.pointer.raise_()

    def focus_at(self, widget):
        while widget is not None:
            if isinstance(widget, DeskWindow):
                for name, window in self.windows.items():
                    if window is widget: self.activate(name); return
            widget = widget.parentWidget()

    def remove(self, name):
        self.windows.pop(name, None)
        button = self.buttons.pop(name, None)
        if button: button.deleteLater()

    def content(self, name):
        widget = QWidget(); layout = QVBoxLayout(widget)
        layout.setContentsMargins(18, 14, 18, 14)
        if name == 'Calculator':
            display = QLineEdit('0'); display.setObjectName('calcDisplay')
            layout.addWidget(display)
            grid = QGridLayout(); layout.addLayout(grid)
            def press(key):
                if key == 'C': display.setText('0')
                elif key == '⌫': display.setText(display.text()[:-1] or '0')
                elif key == '=':
                    try: display.setText(format(calculate(display.text()), '.12g'))
                    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError): display.setText('Error')
                else: display.setText((display.text() if display.text() not in ('0', 'Error') else '') + key)
            for i, key in enumerate(['C','(',')','⌫','7','8','9','/','4','5','6','*','1','2','3','-','0','.','=','+']):
                b = QPushButton(key); b.setMinimumHeight(44)
                b.clicked.connect(lambda checked=False, k=key: press(k)); grid.addWidget(b, i//4, i%4)
        elif name == 'Notes':
            path = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / 'notes.txt'
            editor = QTextEdit(); editor.setPlaceholderText('Capture a thought…')
            if path.exists():
                try: editor.setPlainText(path.read_text(encoding='utf-8'))
                except OSError: pass
            layout.addWidget(editor)
            feedback = QLabel('Saved locally on this PC. Touch keyboard below.')
            layout.addWidget(feedback)
            def save():
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(editor.toPlainText(), encoding='utf-8')
                    feedback.setText('Saved ✓')
                except OSError as e: feedback.setText(str(e))
            keyboard = QGridLayout(); layout.addLayout(keyboard)
            for row, letters in enumerate(('qwertyuiop','asdfghjkl','zxcvbnm')):
                for col, letter in enumerate(letters):
                    b = QPushButton(letter); b.setMinimumWidth(24)
                    b.clicked.connect(lambda checked=False, s=letter: editor.insertPlainText(s))
                    keyboard.addWidget(b, row, col)
            row = QHBoxLayout(); layout.addLayout(row)
            for label, action in [('Space',lambda: editor.insertPlainText(' ')),
                                  ('Enter',lambda: editor.insertPlainText('\n')),
                                  ('⌫',lambda: editor.textCursor().deletePreviousChar()), ('Save',save)]:
                b=QPushButton(label); b.clicked.connect(action); row.addWidget(b)
        elif name == 'File Explorer':
            location = QLabel('Mini Desk / Home'); layout.addWidget(location)
            files = QListWidget(); layout.addWidget(files)
            tree = {'Home':['Documents','Projects','Media'], 'Documents':['Welcome.txt','Touch mapping.txt'],
                    'Projects':['CapSlide'], 'Media':['Desktop palette'], 'CapSlide':['Firmware','Desktop app']}
            files.addItems(tree['Home'])
            preview = QLabel('Mock filesystem · select a folder to open it.'); preview.setWordWrap(True); layout.addWidget(preview)
            def open_item(item):
                name = item.text()
                if name in tree:
                    files.clear(); files.addItems(tree[name]); location.setText('Mini Desk / '+name)
                else:
                    samples={'Welcome.txt':'Welcome to Mini Desk.\nTap B1 to toggle the pointer axis. Use B2 to select or drag.',
                             'Touch mapping.txt':'B1: X/Y toggle\nB2: left down/up\nSlider: active axis\nLaunch: applications and context menu',
                             'Desktop palette':'MIDNIGHT NAVY  #070e1d\nCYAN  #52e4ff\nBLUE  #659dff\nMINT  #62ffbe',
                             'Firmware':'FreeRTOS sensing task / CapSense driver / NDJSON UART',
                             'Desktop app':'PySide6 workspace / local notes / in-app pointer'}
                    preview.setText(name+'\n\n'+samples.get(name,'CapSlide sample item.'))
            files.itemClicked.connect(open_item)
            home = QPushButton('↑ Home'); home.clicked.connect(lambda: (files.clear(), files.addItems(tree['Home']), location.setText('Mini Desk / Home')))
            layout.addWidget(home)
        elif name == 'Settings':
            widget.setObjectName('settingsContent')
            layout.addWidget(QLabel('WORKSPACE SETTINGS'))
            layout.addWidget(QLabel('Pointer response · saved on this PC'))
            for key,title,low,high,scale,unit in (
                ('speed','Maximum speed',25,800,100,'screens/s'),
                ('smoothing','Movement smoothing',0,250,1000,'s'),
                ('sensitivity','Slider sensitivity',30,300,100,'×'),
                ('edge','Endpoint snap zone',0,5,1,'%')):
                value=QLabel(); slider=QSlider(Qt.Horizontal); slider.setObjectName('setting_'+key)
                slider.setRange(low,high); slider.setValue(round(getattr(self.desk.engine,key)*scale))
                def change(v,k=key,s=scale,l=value,t=title,u=unit):
                    l.setText(f'{t}   {v/s:g} {u}'); self.desk.configure_pointer(k,v/s)
                value.setText(f'{title}   {slider.value()/scale:g} {unit}')
                slider.valueChanged.connect(change); layout.addWidget(value); layout.addWidget(slider)
            layout.addWidget(QLabel('Workspace accent'))
            for color in ('Cyan', 'Blue', 'Mint'):
                b=QPushButton(color); b.clicked.connect(lambda checked=False,c=color: self.desk.set_accent(c)); layout.addWidget(b)
            explanation=QLabel('B1: tap to toggle X / Y. B2: click or hold to drag.\nAxis changes anchor at the current pointer.\nAt a slider endpoint, move toward the pointer to pick up control.\nBoth endpoints remain reachable at every sensitivity.'); explanation.setWordWrap(True)
            layout.addWidget(explanation)
            layout.addStretch()
            scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(widget)
            scroll.viewport().setObjectName('settingsViewport')
            return scroll
        else:
            text = QLabel(); text.setWordWrap(True); layout.addWidget(text); layout.addStretch()
            def refresh(): text.setText(self.desk.monitor_text())
            timer=QTimer(widget); timer.timeout.connect(refresh); timer.start(250); refresh()
        return widget
