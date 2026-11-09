from PySide6.QtCore import Qt, Signal, QPoint, QTimer
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

class MoveBar(QFrame):
    def __init__(self, window, title):
        super().__init__(window)
        self.window = window
        self.anchor = None
        self.setObjectName('titleBar')
        row = QHBoxLayout(self)
        label = QLabel('◈   ' + title)
        label.setAttribute(Qt.WA_TransparentForMouseEvents)
        row.addWidget(label); row.addStretch()
        for text, action in [('—', window.hide), ('□', window.toggle_maximize), ('×', window.close)]:
            button = QPushButton(text); button.setFixedSize(30, 26)
            button.clicked.connect(action); row.addWidget(button)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.window.maximized: return
            self.window.focused.emit()
            self.anchor = e.globalPosition().toPoint() - self.window.pos()
            e.accept()

    def mouseMoveEvent(self, e):
        if self.anchor is not None:
            p = e.globalPosition().toPoint() - self.anchor
            parent = self.window.parentWidget()
            self.window.move(max(0, min(p.x(), parent.width()-80)), max(0, min(p.y(), parent.height()-45)))

    def mouseReleaseEvent(self, e):
        self.anchor = None

    def mouseDoubleClickEvent(self,e):
        if e.button()==Qt.LeftButton: self.window.toggle_maximize()

class ResizeHandle(QLabel):
    def __init__(self, window):
        super().__init__('◢', window)
        self.window = window
        self.anchor = None
        self.setAlignment(Qt.AlignRight)
        self.setCursor(Qt.SizeFDiagCursor)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.window.maximized: return
            self.anchor = e.globalPosition().toPoint()
            self.size_start = self.window.size()

    def mouseMoveEvent(self, e):
        if self.anchor is not None:
            delta = e.globalPosition().toPoint() - self.anchor
            parent = self.window.parentWidget()
            self.window.resize(max(340, min(parent.width()-self.window.x(), self.size_start.width()+delta.x())),
                               max(260, min(parent.height()-self.window.y(), self.size_start.height()+delta.y())))

    def mouseReleaseEvent(self, e):
        self.anchor = None

class DeskWindow(QFrame):
    focused = Signal()
    closed = Signal()
    def __init__(self, title, content, parent):
        super().__init__(parent)
        self.setObjectName('deskWindow')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMinimumSize(340, 260)
        self.maximized=False
        self.restore_geometry=None
        layout = QVBoxLayout(self); layout.setContentsMargins(1, 1, 1, 1); layout.setSpacing(0)
        self.bar = MoveBar(self, title)
        layout.addWidget(self.bar)
        layout.addWidget(content, 1)
        layout.addWidget(ResizeHandle(self))
        self.resize(530, 440)

    def toggle_maximize(self):
        if not self.maximized:
            self.restore_geometry=self.geometry()
            self.setGeometry(self.parentWidget().rect())
            QTimer.singleShot(0,self.fit_maximized)
        elif self.restore_geometry is not None:
            self.setGeometry(self.restore_geometry)
            parent=self.parentWidget()
            self.resize(min(self.width(),parent.width()),min(self.height(),parent.height()))
            self.move(max(0,min(self.x(),parent.width()-self.width())),max(0,min(self.y(),parent.height()-self.height())))
        self.maximized=not self.maximized

    def fit_maximized(self):
        if self.maximized:
            self.layout().activate()
            self.setGeometry(self.parentWidget().rect())

    def closeEvent(self, e):
        self.closed.emit()
        super().closeEvent(e)
