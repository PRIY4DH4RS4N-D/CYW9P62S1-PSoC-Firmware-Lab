from PySide6.QtCore import Qt, QVariantAnimation, QEasingCurve, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient
from PySide6.QtWidgets import QWidget

class AxisBadge(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.setFixedSize(196,44)
        self.mode='X'; self.blend=0.
        self.animation=QVariantAnimation(self); self.animation.setDuration(280)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.valueChanged.connect(self._value)

    def _value(self,value): self.blend=value; self.update()

    def set_mode(self,mode):
        if mode==self.mode: return
        self.mode=mode; self.animation.stop(); self.animation.setStartValue(self.blend)
        self.animation.setEndValue(1. if mode=='Y' else 0.); self.animation.start()

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor('#254961'),1)); p.setBrush(QColor('#0a1c30'))
        p.drawRoundedRect(QRectF(0,0,self.width()-1,self.height()-1),12,12)
        p.setPen(Qt.NoPen); p.setBrush(QColor('#195675'))
        p.drawRoundedRect(QRectF(4+self.blend*96,4,91,35),9,9)
        p.setFont(QFont('Segoe UI',8,QFont.DemiBold))
        for i,text in enumerate(('X  HORIZONTAL','Y  VERTICAL')):
            p.setPen(QColor('#8deeff') if (i==1)==(self.mode=='Y') else QColor('#63849d'))
            p.drawText(QRectF(i*96,0,98,44),Qt.AlignCenter,text)

class TouchVisual(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.setMinimumHeight(164)
        self.position=-1; self.b1=self.b2=0; self.x=self.y=0.; self.feedback='READY'

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w=self.width(); gap=6; pad=(w-4*gap)/5
        p.setFont(QFont('Segoe UI',9,QFont.DemiBold)); p.setPen(QColor('#88a6be'))
        p.drawText(0,13,'FIVE-SEGMENT CAPACITIVE SLIDER')
        for i in range(5):
            active=self.position>=0 and abs(self.position/25-i)<1.15
            p.setPen(QPen(QColor('#62e7ff' if active else '#27445c'),1))
            p.setBrush(QColor('#18556f' if active else '#11283c'))
            rect=QRectF(i*(pad+gap),24,pad,32); p.drawRoundedRect(rect,6,6)
            p.setPen(QColor('#b9f6ff' if active else '#52718c')); p.drawText(rect,Qt.AlignCenter,str(i+1))
        if self.position>=0:
            p.setPen(QPen(QColor('#78e8ff'),2)); x=2+self.position/100*(w-4)
            p.drawLine(int(x),60,int(x),66)
        for i,(text,down) in enumerate((('B1  AXIS',self.b1),('B2  SELECT',self.b2))):
            rect=QRectF(i*(w/2+3),77,w/2-5,29)
            p.setBrush(QColor('#186074' if down else '#10263a')); p.setPen(QPen(QColor('#50d8f6' if down else '#294258'),1))
            p.drawRoundedRect(rect,7,7); p.setPen(QColor('#a1ecfb' if down else '#92acc1')); p.drawText(rect,Qt.AlignCenter,text+(' ●' if down else ''))
        p.setFont(QFont('Consolas',10)); p.setPen(QColor('#d6eeff'))
        p.drawText(0,130,f'X {self.x:06.1f}     Y {self.y:06.1f}')
        p.setPen(QColor('#5fdcf4')); p.setFont(QFont('Segoe UI',9,QFont.DemiBold))
        p.drawText(0,154,self.feedback)
