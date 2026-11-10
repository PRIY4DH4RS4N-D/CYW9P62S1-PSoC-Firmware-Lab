"""Read-only audit of the final delivery; never opens a serial port."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    manifest=json.loads((ROOT/'build/deliverable-sha256.json').read_text())
    for path,digest in manifest.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    elf=(ROOT/'build/artifacts/ChordSlide.elf').read_bytes();assert elf[:4]==b'\x7fELF' and elf[4:6]==b'\x01\x01' and struct.unpack_from('<H',elf,18)[0]==40
    records=0;eof=False
    for line in (ROOT/'build/artifacts/ChordSlide.hex').read_text().splitlines():
        assert line.startswith(':');v=bytes.fromhex(line[1:]);assert len(v)==v[0]+5 and sum(v)%256==0;records+=1
        if v[3]==1:eof=True
    assert eof
    model=(ROOT/'models/chordslide_int8.tflite').read_bytes();assert model[4:8]==b'TFL3' and model in elf
    for prefix in ['dashboard-source-self-test','exe-self-test']:
        report=ROOT/f'build/{prefix}.json';assert json.loads(report.read_text())['status']=='PASS'
        for ext in ['png','csv','parquet']:assert Path(str(report)+'.'+ext).stat().st_size>0
    result={'status':'PASS','hashed_deliverables':len(manifest),'intel_hex_records':records,'elf':'ELF32 little-endian ARM','model_embedded':True,'source_and_exe_exports':True,'hardware':'NOT TESTED'}
    (ROOT/'build/delivery-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
