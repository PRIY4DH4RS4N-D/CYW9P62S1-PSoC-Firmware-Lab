"""Collect actual USB-UART samples and label completed events from the console."""
import argparse
import json
import queue
import threading
import time
import uuid
from datetime import datetime, timezone
import serial
from protocol import Decoder, encode, unpack_sample, unpack_event, LABELS

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    session=str(uuid.uuid4())
    commands=queue.Queue()
    def keyboard():
        while True:
            try:commands.put(input('Label: EVENT_ID TAP|HOLD|GRAZE|WIDE (or quit)> '))
            except EOFError:commands.put('quit');return
    threading.Thread(target=keyboard,daemon=True).start()
    with serial.Serial(a.port,115200,timeout=.05,write_timeout=.2) as uart,open(a.output,'a',encoding='utf-8') as out:
        def write(r):r['session']=session;out.write(json.dumps(r)+'\n');out.flush()
        write(dict(kind='metadata',source='physical_uart',feature_schema=1,utc=datetime.now(timezone.utc).isoformat()))
        uart.write(encode(0x10,0))
        decoder=Decoder()
        seen=set()
        last=time.monotonic()
        while True:
            for frame in decoder.feed(uart.read(max(1,uart.in_waiting))):
                last=time.monotonic()
                if frame.kind==1:
                    ms,*values=unpack_sample(frame.payload)
                    write(dict(kind='sample',ms=ms,values=values,sequence=frame.seq))
                elif frame.kind==2:
                    event=unpack_event(frame.payload)
                    seen.add(event['event_id'])
                    event.update(kind='event',sequence=frame.seq,label=None)
                    write(event)
                    print(f'Physical event {event["event_id"]}: {event["features"]}')
            try:
                cmd=commands.get_nowait().strip().split()
                if cmd==['quit']:break
                if len(cmd)==2 and int(cmd[0]) in seen and cmd[1].upper() in LABELS:
                    write(dict(kind='label',event_id=int(cmd[0]),label=cmd[1].upper()))
                else:print('Use an observed event ID and one of',LABELS)
            except queue.Empty:pass
            except ValueError:print('Invalid event ID')
            if time.monotonic()-last>3:
                print('No valid board data; check cable, firmware and port')
                last=time.monotonic()
if __name__=='__main__':main()
