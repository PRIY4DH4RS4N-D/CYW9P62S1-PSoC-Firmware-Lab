"""Resolution-independent icons drawn locally with Qt; no font glyph dependency."""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap

def app_icon(name, size=36):
    pix=QPixmap(size,size); pix.fill(Qt.transparent)
    p=QPainter(pix); p.setRenderHint(QPainter.Antialiasing); p.scale(size/36,size/36)
    colors={'Calculator':'#69dcff','Notes':'#9faaff','File Explorer':'#62dfc4','Settings':'#7db5ff','System Monitor':'#f4bf78'}
    color=QColor(colors.get(name,'#65e4ff'))
    fill=QColor(color); fill.setAlpha(23)
    p.setBrush(fill); p.setPen(Qt.NoPen); p.drawRoundedRect(QRectF(0,0,36,36),10,10)
    p.setPen(QPen(color,1.6,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin)); p.setBrush(Qt.NoBrush)
    if name=='Calculator':
        p.drawRoundedRect(QRectF(10,7,16,22),3,3); p.drawLine(13,13,23,13)
        for x in (14,21):
            for y in (19,24): p.drawPoint(x,y)
    elif name=='Notes':
        p.drawRoundedRect(QRectF(9,7,18,23),3,3)
        for y in (13,18,23): p.drawLine(13,y,23 if y!=23 else 20,y)
    elif name=='File Explorer':
        p.drawPolyline([QPointF(7,26),QPointF(7,11),QPointF(15,11),QPointF(18,15),QPointF(29,15),QPointF(29,27),QPointF(7,27)])
        p.drawLine(8,18,28,18)
    elif name=='Settings':
        p.drawEllipse(QRectF(12,12,12,12))
        for x,y,xx,yy in ((18,6,18,10),(18,26,18,30),(6,18,10,18),(26,18,30,18),(9,9,12,12),(24,24,27,27),(9,27,12,24),(24,12,27,9)):
            p.drawLine(x,y,xx,yy)
    else:
        p.drawRoundedRect(QRectF(6,8,24,19),3,3)
        p.drawPolyline([QPointF(8,20),QPointF(13,20),QPointF(16,13),QPointF(20,23),QPointF(23,17),QPointF(28,17)])
        p.drawLine(14,30,22,30)
    p.end(); return QIcon(pix)
