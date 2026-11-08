"""Verify built artifacts and write a reviewable release record. Never accesses a probe."""
import hashlib, json, re, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
build=ROOT/'build'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
subprocess.run([sys.executable,str(ROOT/'scripts/verify_bsp.py')],check=True)
manifest=json.loads((build/'artifact-sha256.json').read_text())
for name,digest in manifest.items():
    if sha(build/'artifacts'/name)!=digest: raise SystemExit(f'Artifact hash mismatch: {name}')
if (build/'undefined-symbols.txt').read_text().strip(): raise SystemExit('Unresolved ELF symbols')
log=(build/'firmware-build.log').read_text()
if 'Build complete' not in log or 'error:' in log: raise SystemExit('Build did not complete successfully')
sources=list((ROOT/'firmware').glob('*.c'))+list((ROOT/'firmware').glob('*.h'))+[ROOT/'firmware/Makefile']
elf_path=build/'artifacts/TouchRGB.elf'
if max(p.stat().st_mtime for p in sources)>elf_path.stat().st_mtime:
    raise SystemExit('Firmware sources are newer than the ELF; rebuild first')
elf=elf_path.read_bytes()
assert elf[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<H',elf,18)[0]==40, 'Expected ARM ELF32 little endian'
entry=struct.unpack_from('<I',elf,24)[0]
assert entry&1 and 0x10002000<=entry<0x10100000, 'Unexpected CM4 entry address'
memory={}; base=0; eof=False
for line in (build/'artifacts/TouchRGB.hex').read_text().splitlines():
    assert line.startswith(':') and not eof, 'Malformed HEX record order'
    record=bytes.fromhex(line[1:]); n=record[0]; address=int.from_bytes(record[1:3],'big'); kind=record[3]
    assert len(record)==n+5 and sum(record)%256==0, 'Bad HEX checksum/length'
    data=record[4:4+n]
    if kind==4: base=int.from_bytes(data,'big')<<16
    elif kind==2: base=int.from_bytes(data,'big')<<4
    elif kind==1: eof=True
    elif kind==0:
        for i,value in enumerate(data):
            a=base+address+i
            assert a not in memory or memory[a]==value, 'Conflicting HEX records'
            memory[a]=value
assert eof and memory and min(memory)==0x10000000 and max(memory)<0x10100000, 'Unexpected flash address range'
binary=(build/'artifacts/TouchRGB.bin').read_bytes()
first_address=min(memory)
assert all(binary[a-first_address]==v for a,v in memory.items()), 'BIN/HEX mismatch'
flash=int(re.search(r'Total FLASH \(Utilized\)\s*:\s*([\d,]+)',log)[1].replace(',',''))
assert len(memory)==flash, 'HEX data count differs from linker flash report'
assert 'ALL SOFTWARE TESTS PASSED' in (build/'software-tests.log').read_text()
assert 'PASS: PWM' in (build/'software-tests.log').read_text()
record={
 'board':'CYW9P62S1-43438EVB-01','device':'CY8C6247BZI-D54',
 'artifacts':manifest,'firmware_sources':{str(p.relative_to(ROOT)):sha(p) for p in sources},
 'compiler':(build/'compiler-version.txt').read_text().splitlines()[0],
 'flash_bytes':flash,'hex_min_address':hex(min(memory)),'hex_max_address':hex(max(memory)),
 'cm4_entry':hex(entry),'checks':['BSP snapshot','artifact hashes','no unresolved symbols','ARM ELF header','HEX checksum/address/length','BIN matches HEX','source freshness','software test log'],
 'warnings':[line.strip() for line in log.splitlines() if 'warning:' in line],
 'physical_tested':False,'programmed':False
}
(build/'verification.json').write_text(json.dumps(record,indent=2))
print(f'PASS: release verified; {flash} flash bytes; {len(sources)} firmware source/config files recorded. Physical hardware not tested.')
