"""Offscreen UI integration checks. No physical connection or sensor data claimed."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest

def test_dashboard_constructs_offline():
    pytest.importorskip('PySide6.QtWidgets')
    from PySide6.QtWidgets import QApplication
    from dashboard.app import Dashboard
    app=QApplication.instance() or QApplication([])
    window=Dashboard()
    window.show()
    app.processEvents()
    assert len(window.curves)==7
    assert window.events==[] and window.accepted==0 and window.rejected==0
    assert window.worker is None
    assert 'Disconnected' in window.status.text()
    window.close()
    app.processEvents()

def test_csv_and_parquet_export_with_explicit_test_fixture(tmp_path,monkeypatch):
    pytest.importorskip('PySide6.QtWidgets')
    from PySide6.QtWidgets import QApplication,QFileDialog
    from dashboard.app import Dashboard
    import pandas as pd
    app=QApplication.instance() or QApplication([])
    window=Dashboard()
    # An artificial unit-test row, never a recorded training dataset or hardware event.
    window.events=[dict(event_id=1,ms=100,session='UNIT-TEST-ONLY',features=[100,200,1,150,0,10],prediction=255,baseline=0,confidence=0,label=None)]
    for extension in ('csv','parquet'):
        destination=tmp_path/f'unit-test.{extension}'
        monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,path=destination,**k:(str(path),''))
        window.export()
        frame=pd.read_csv(destination) if extension=='csv' else pd.read_parquet(destination)
        assert frame.iloc[0]['session']=='UNIT-TEST-ONLY'
        assert frame.iloc[0]['duration_ms']==100
        assert frame.iloc[0]['prediction']==255
    window.close()
    app.processEvents()
