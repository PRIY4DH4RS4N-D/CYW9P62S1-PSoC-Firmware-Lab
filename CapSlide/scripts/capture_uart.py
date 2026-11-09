"""Operator-run read-only capture of an already programmed CapSlide device."""
import argparse
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import serial
from event_parser import LineDecoder, ProtocolError

def main():
    p=argparse.ArgumentParser(); p.add_argument('--port',required=True)
    p.add_argument('--seconds',type=float,default=15); p.add_argument('--output',default='build/uart-capture.json')
    args=p.parse_args(); events=[]; errors=[]; decoder=LineDecoder()
    with serial.Serial(args.port,115200,timeout=.1) as stream:
        deadline=time.monotonic()+args.seconds
        while time.monotonic()<deadline:
            for e in decoder.feed(stream.read(512)):
                if isinstance(e,ProtocolError): errors.append(str(e))
                else: events.append(e)
    dest=Path(args.output); dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(dict(port=args.port,events=events,errors=errors),indent=2),encoding='utf-8')
    print(f'{len(events)} valid events; {len(errors)} errors. Saved {dest}')
    return 0 if events and not errors else 1

if __name__=='__main__': raise SystemExit(main())
