import argparse
import json
import sys
import os
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from mini_desk import MiniDesk

def main():
    parser=argparse.ArgumentParser(description='CapSlide Mini Desk')
    parser.add_argument('--simulator',action='store_true')
    parser.add_argument('--port',help='KitProg3 COM port, e.g. COM5')
    parser.add_argument('--smoke-test',metavar='REPORT',help='Run packaged startup checks, write JSON, exit')
    parser.add_argument('--screenshot',metavar='PNG')
    parser.add_argument('--record-uart',metavar='NDJSON',help='Record validated live UART events and pointer targets')
    parser.add_argument('--run-seconds',type=float,help='Close automatically after a diagnostic session')
    args=parser.parse_args()
    app=QApplication(sys.argv[:1]); app.setApplicationName('CapSlide'); app.setOrganizationName('CapSlide')
    # The Windows offscreen platform doesn't enumerate system fonts itself.
    for filename in ('segoeui.ttf', 'segoeuil.ttf', 'seguisb.ttf', 'seguisym.ttf'):
        font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/filename
        if font.exists(): QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Segoe UI',10))
    desk=MiniDesk(args.simulator,args.port,args.record_uart); desk.show()
    if args.run_seconds:
        QTimer.singleShot(max(1,int(args.run_seconds*1000)),desk.close)
    if args.screenshot:
        QTimer.singleShot(900,lambda:desk.grab().save(args.screenshot))
    if args.smoke_test:
        def finish_smoke():
            try:
                from app_manager import APPS
                report=dict(ok=len(desk.manager.windows)==5,apps=list(desk.manager.windows),
                            frozen=bool(getattr(sys,'frozen',False)),connection=desk.connection,events=desk.count,
                            errors=desk.errors,device_tx_errors=desk.device_errors,port=desk.port)
                report['mode']=desk.engine.mode
                report['controls']='toggle-b1-click-b2'
                app.processEvents()
                if args.screenshot: desk.grab().save(args.screenshot)
                Path(args.smoke_test).write_text(json.dumps(report,indent=2),encoding='utf-8')
            finally:
                desk.close(); app.quit()
        def smoke():
            from app_manager import APPS
            for name in APPS: desk.manager.launch(name)
            # Hardware smoke reports actual UART counts; simulation exercises input.
            if args.simulator: desk.process_event(dict(v=1,seq=0,type='MOVE',position=62,mode='X'))
            QTimer.singleShot(300,finish_smoke)
        QTimer.singleShot(1200,smoke)
    return app.exec()

if __name__=='__main__':
    raise SystemExit(main())
