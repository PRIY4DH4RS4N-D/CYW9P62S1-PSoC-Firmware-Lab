import math
from collections import deque
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

class Pointer(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.x = self.y = 200
        self.phase = 0
        self.down = False
        self.color = QColor('#52e4ff')
        self.trail=deque(maxlen=32)
        self.elapsed=0.
        self.ripple=0.
        self.axis='X'

    def advance(self,x,y,dt):
        self.elapsed+=dt
        if not self.trail or abs(x-self.x)+abs(y-self.y)>.5:
            self.trail.append((x,y,self.elapsed))
        while self.trail and self.elapsed-self.trail[0][2]>.4: self.trail.popleft()
        self.x,self.y=x,y
        self.ripple=max(0.,self.ripple-dt)
        self.update()

    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        for i in range(1,len(self.trail)):
            x0,y0,t0=self.trail[i-1]; x1,y1,t1=self.trail[i]
            color=QColor(self.color); color.setAlpha(int(130*max(0,1-(self.elapsed-t1)/.4)))
            p.setPen(QPen(color,2.5,Qt.SolidLine,Qt.RoundCap)); p.drawLine(QPointF(x0,y0),QPointF(x1,y1))
        center=QPointF(self.x, self.y)
        radius=15+2*math.sin(self.phase)
        glow=QColor(self.color); glow.setAlpha(35 if not self.down else 100)
        p.setPen(Qt.NoPen); p.setBrush(glow); p.drawEllipse(center, radius, radius)
        p.setPen(QPen(self.color,1.5)); p.setBrush(Qt.NoBrush); p.drawEllipse(center,6,6)
        p.setBrush(self.color); p.setPen(Qt.NoPen)
        p.drawPolygon(QPolygonF([center,center+QPointF(4,16),center+QPointF(8,10),center+QPointF(15,8)]))
        if self.ripple:
            color=QColor(self.color); color.setAlpha(int(180*self.ripple/.45))
            p.setPen(QPen(color,1.5)); p.setBrush(Qt.NoBrush)
            r=10+32*(1-self.ripple/.45); p.drawEllipse(center,r,r)
        p.setPen(self.color); p.drawText(center+QPointF(20,-10),self.axis)
