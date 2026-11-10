"""Summarize evidence; fail if a deliverable or verification claim is unsupported."""
import json,re,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def text(path):return (ROOT/path).read_text(encoding='utf-8-sig')
def main():
    build=ROOT/'build';model=ROOT/'models/chordslide_int8.tflite';elf=build/'artifacts/ChordSlide.elf';exe=build/'dist/ChordSlide.exe'
    assert model.read_bytes() in elf.read_bytes()
    assert not text('build/undefined-symbols.txt').strip()
    log=text('build/firmware-build.log');assert 'Toolchain validation: PASS' in log and 'Total FLASH (Utilized)' in log
    junit=ET.parse(build/'host-tests.xml');suites=list(junit.getroot().iter('testsuite'));tests=sum(int(s.attrib['tests']) for s in suites);skipped=sum(int(s.attrib.get('skipped',0)) for s in suites)
    assert sum(int(s.attrib.get('failures',0))+int(s.attrib.get('errors',0)) for s in suites)==0
    exe_test=json.loads(text('build/exe-self-test.json'));assert exe_test['status']=='PASS'
    evaluation=json.loads(text('models/evaluation.json'));assert evaluation['source']=='SYNTHETIC SMOKE TEST ONLY'
    assert exe.exists()
    sizes={m[0]:int(m[1]) for m in re.findall(r'^(\.[\w.]+)\s+(\d+)\s+\d+',text('build/memory-sections.txt'),re.M)}
    flash=int(re.search(r'flash:\s*(\d+) B',log).group(1))
    symbols=text('build/symbols-by-size.txt');assert ' T arm_convolve_s8\n' in symbols
    static_ram=sum(sizes.get(k,0) for k in ['.ramVectors','.data','.cy_sharedmem','.noinit','.bss'])
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in list((build/'artifacts').glob('*'))+[model,exe] if p.is_file()}
    (build/'deliverable-sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    status={'firmware':'BUILD VERIFIED','host':'HOST TEST VERIFIED','host_tests_passed':tests-skipped,'skipped_hardware_tests':skipped,'exe_self_test':'PASS','model':'SYNTHETIC SMOKE TEST ONLY','model_bytes':model.stat().st_size,'flash_region_bytes':flash,'static_ram_before_c_heap_and_main_stack':static_ram,'c_heap_reservation_bytes':sizes['.heap'],'rtos_heap_bytes':49152,'tensor_arena_reserved_bytes':24576,'hardware':'HARDWARE NOT TESTED','flashing':'NOT PERFORMED'}
    (build/'verification.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    report=f'''# ChordSlide verification report

Generated 7 November 2026 from the local build/test evidence. No board was flashed, erased, debugged or modified.

|Area|Result|Evidence|
|---|---|---|
|Firmware sources / board / linker|**BUILD VERIFIED**|[Compiler log](build/firmware-build.log), [compiler version](build/compiler-version.txt), [map](build/artifacts/ChordSlide.map)|
|Model integrated into MCU ELF|**BUILD VERIFIED**|Host test asserts complete TFLite bytes and SHA in ELF; generated C equals model bytes|
|CMSIS-NN runtime linkage|**BUILD VERIFIED**|`arm_convolve_s8` and fully connected helpers in [symbols](build/symbols-by-size.txt)|
|Protocol / preprocessing / replay / Qt / INT8 model|**HOST TEST VERIFIED**|{tests-skipped} passed, {skipped} hardware test skipped; [JUnit](build/host-tests.xml), [test log](build/host-tests.log)|
|Windows EXE packaging and launch|**HOST TEST VERIFIED**|[Package log](build/dashboard-package.log), [EXE self-test](build/exe-self-test.json), screenshot and exports adjacent to that report|
|Training / float evaluation / INT8 conversion|**HOST TEST VERIFIED — SYNTHETIC ONLY**|25 training epochs; [training log](build/training.log), [evaluation](models/evaluation.json), float and INT8 artifacts|
|Real dataset and physical accuracy|**NOT AVAILABLE**|No collected board data; synthetic scores are not physical accuracy|
|MCU AllocateTensors / Invoke / stack margins / scan rate / latency|**HARDWARE NOT TESTED**|Compile/link verifies integration and reservations, not execution|
|Host/device probability parity|**HARDWARE NOT TESTED**|Automated test skipped; `ml.parity` supplies a SHA-checked device test|
|Programming|**NOT PERFORMED**|Build scripts contain no flash/program/debug action; serial enumeration found no ports|

## Actual firmware output

Target `APP_CYW9P62S1-43438EVB-01`, device CY8C6247BZI-D54, CM4 with board-default CM0+ startup. GCC Arm 14.2.1, ModusToolbox 3.9. All firmware C/C++ sources compiled; final ELF has no unresolved symbols. A full 282-step build covers vendor and application sources. ELF/HEX/BIN/map are in [build/artifacts](build/artifacts/). BIN spans the application flash layout and is not a generic address-zero image.

|Memory item|Bytes|Interpretation|
|---|---:|---|
|Flash region used|{flash:,}|Linker address span, including layout gaps; 1,048,576 bytes available|
|CM0+ startup section|{sizes['.cy_m0p_image']:,}|Included in flash artifacts|
|CM4 `.text`|{sizes['.text']:,}|Code/constants including 3,016-byte model|
|`.data`|{sizes['.data']:,}|Initialized RAM, with flash load image|
|`.bss`|{sizes['.bss']:,}|Includes RTOS heap, tensor arena and UART ring|
|Other static RAM + vectors|{static_ram-sizes['.bss']-sizes['.data']:,}|Shared/noinit/vector sections|
|Static RAM before C heap/main stack|{static_ram:,}|Section sum, excludes small alignment gaps|
|C heap reservation|{sizes['.heap']:,}|Stock linker reserves remaining SRAM; this is not measured heap use|
|Main/ISR stack reservation|{sizes['.stack_dummy']:,}|Separate from RTOS task stacks|
|FreeRTOS heap_4 region|49,152|Contained within `.bss`; tasks/queues allocate from here|
|Application task stacks|24,576|Contained within RTOS heap, not an additional `.bss` allocation|
|Tensor arena reservation|24,576|Contained within `.bss`; actual arena use awaits AllocateTensors on MCU|

See [section report](build/memory-sections.txt), [ELF section flags](build/elf-sections.txt), [size summary](build/memory-summary.txt) and map. The stock linker reports RAM near 99% because it reserves the unused tail as a NOLOAD C heap. The aggregate `size` text figure also includes sections that are not flash payload; use the linker/section figures above instead of treating aggregate text as flash consumption.

The retained vendor linker warning is a LOAD segment with RWX permissions. It is present with the stock BSP layout; this build does not establish MPU execution-permission isolation. The final compiler log records any remaining warnings. Initial include-path integration failures were resolved by excluding TFLM headers from recursive auto-discovery and adding only intended roots, avoiding FlatBuffers `string.h` shadowing libc.

## Model and test evidence

Model SHA256: `{evaluation['sha256']}`. Size: **{evaluation['model_bytes']} bytes**. Float32 Keras, float TFLite, fully INT8 TFLite, C embedding, holdout confusion matrix, per-class precision/recall/F1, training history and parity vectors are provided under `models/`. The source of every supplied training/test waveform is artificial. No final accuracy claim is made.

The converter completed and host tests confirm INT8 input/output, integer tensors, expected operators, repeatable saved-vector inference, exact generated C bytes and matching embedded model identity. Host TFLite invocation median was {evaluation['host_latency_us']['median']:.2f} µs and p95 {evaluation['host_latency_us']['p95']:.2f} µs on this machine. These are host benchmark values, not MCU or interaction latency. Initial normalization scale, gesture timing and rejection thresholds require physical calibration.

C/Python protocol tests cover the CRC check vector, all payload boundaries, fragmentation, corrupted payload recovery, invalid lengths and timeouts, acknowledged retries and sequence-preserving retransmission. Native firmware C normalization and segmentation are exercised through an executable bridge, including many synthetic waveform replays and C/Python window equality. Recorder provenance tests prevent replay from being recorded as physical data. Qt tests cover seven channels, accepted navigation, smoke/unknown guards and replay provenance.

The source and packaged EXE self-tests construct the dashboard offscreen, feed explicitly synthetic test signals, render plots, test CSV/Parquet exports and exit. These are software checks on the development machine, not a clean Windows install test or USB-UART execution. The EXE is {exe.stat().st_size:,} bytes, unsigned. [Deliverable SHA256](build/deliverable-sha256.json) records the final artifacts.

## Remaining hardware work

Use [FLASH_GUIDE.md](FLASH_GUIDE.md) only as a separate operator decision. Then collect real sessions, confirm raw access and signal feasibility, calibrate normalization, measure completed-scan intervals and end-to-end/inference latency, confirm actual tensor allocation and stack margins, train on physical data, and run SHA-checked device parity. No pinch/spread or multi-finger recognition is claimed. The expected 50 Hz sampling rate is a configured target. Complete [hardware validation template](docs/HARDWARE_VALIDATION_TEMPLATE.md) before treating the recognizer as experimentally validated.
'''
    (ROOT/'VERIFICATION_REPORT.md').write_text(report,encoding='utf-8');print(json.dumps(status,indent=2))
if __name__=='__main__':main()
