"""Build only. This script has no programming, probe, erase or debug operation."""
import argparse,os,subprocess,shutil,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--tools',default='C:/Infineon/Tools/ModusToolbox/tools_3.9');p.add_argument('--compiler',default='C:/Infineon/Tools/mtb-gcc-arm-eabi/14.2.1/gcc');p.add_argument('--clean',action='store_true');a=p.parse_args()
    build=ROOT/'build';build.mkdir(exist_ok=True);tools=Path(a.tools);compiler=Path(a.compiler);env=os.environ.copy();env['PATH']=str(tools/'modus-shell/bin')+os.pathsep+env['PATH'];env['CY_TOOLS_PATHS']=tools.as_posix()
    cmd=[str(tools/'modus-shell/bin/make.exe'),'-C','firmware',f'CY_TOOLS_DIR={tools.as_posix()}',f'CY_COMPILER_GCC_ARM_DIR={compiler.as_posix()}','-j1']
    def run(cmd,name):
        with (build/name).open('w',encoding='utf-8') as f:result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        if result.returncode:raise SystemExit(f'Failed ({result.returncode}): build/{name}')
    run([str(compiler/'bin/arm-none-eabi-gcc.exe'),'--version'],'compiler-version.txt')
    if a.clean:run(cmd+['clean'],'firmware-clean.log')
    run(cmd+['build'],'firmware-build.log')
    src=ROOT/'firmware/build/APP_CYW9P62S1-43438EVB-01/Release';dest=build/'artifacts';dest.mkdir(exist_ok=True)
    for ext in ['elf','hex','map']:shutil.copy2(src/f'ChordSlide.{ext}',dest)
    run([str(compiler/'bin/arm-none-eabi-objcopy.exe'),'-O','binary',str(dest/'ChordSlide.elf'),str(dest/'ChordSlide.bin')],'objcopy.log')
    for tool,args,name in [('size',['-A'],'memory-sections.txt'),('size',[],'memory-summary.txt'),('nm',['-u'],'undefined-symbols.txt'),('nm',['-S','--size-sort'],'symbols-by-size.txt'),('objdump',['-h'],'elf-sections.txt')]:
        run([str(compiler/f'bin/arm-none-eabi-{tool}.exe')]+args+[str(dest/'ChordSlide.elf')],name)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir() if p.is_file()};(build/'artifact-sha256.json').write_text(json.dumps(hashes,indent=2))
    assert not (build/'undefined-symbols.txt').read_text().strip(),'ELF contains unresolved symbols'
    print('BUILD VERIFIED. No board was programmed. See build/firmware-build.log and memory reports.')
if __name__=='__main__':main()
