import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import numpy as np
from PySide6 import QtWidgets
from dashboard.app import Dashboard

def test_dashboard_navigation_and_replay_guard():
    app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);w=Dashboard()
    w.sample(0,[0]*7,[100]*7,[100]*7,'replay');w.redraw();assert len(w.curves)==7
    w.prediction([1,100,1,2,123,0]+[.01,.9,.01,.01,.01,.01,.01,.04]+[0]*6)
    assert w.tabs.currentIndex()==0 # smoke cannot navigate
    w.prediction([2,200,1,0,120,0]+[.01,.9,.01,.01,.01,.01,.01,.04]+[0]*6)
    assert w.tabs.currentIndex()==1
    w.prediction([3,300,7,0,130,0]+[.01]*7+[.93]+[0]*6)
    assert w.tabs.currentIndex()==1
    w.recorder.arm(2)
    for t in range(90):w.sample(400+t*20,[0,0,0,0,80 if t in range(10,15) else 0,0,0],[0]*7,[0]*7,'replay')
    assert not w.recorder.x
    w.redraw();w.close();app.processEvents()
