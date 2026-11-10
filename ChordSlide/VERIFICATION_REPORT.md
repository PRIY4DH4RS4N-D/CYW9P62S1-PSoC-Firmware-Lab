# ChordSlide verification report

Generated 7 November 2026 from the local build/test evidence. No board was flashed, erased, debugged or modified.

|Area|Result|Evidence|
|---|---|---|
|Firmware sources / board / linker|**BUILD VERIFIED**|[Compiler log](build/firmware-build.log), [compiler version](build/compiler-version.txt), [map](build/artifacts/ChordSlide.map)|
|Model integrated into MCU ELF|**BUILD VERIFIED**|Host test asserts complete TFLite bytes and SHA in ELF; generated C equals model bytes|
|CMSIS-NN runtime linkage|**BUILD VERIFIED**|`arm_convolve_s8` and fully connected helpers in [symbols](build/symbols-by-size.txt)|
|Protocol / preprocessing / replay / Qt / INT8 model|**HOST TEST VERIFIED**|16 passed, 1 hardware test skipped; [JUnit](build/host-tests.xml), [test log](build/host-tests.log)|
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
|Flash region used|130,484|Linker address span, including layout gaps; 1,048,576 bytes available|
|CM0+ startup section|6,580|Included in flash artifacts|
|CM4 `.text`|120,836|Code/constants including 3,016-byte model|
|`.data`|1,404|Initialized RAM, with flash load image|
|`.bss`|79,644|Includes RTOS heap, tensor arena and UART ring|
|Other static RAM + vectors|868|Shared/noinit/vector sections|
|Static RAM before C heap/main stack|81,916|Section sum, excludes small alignment gaps|
|C heap reservation|198,640|Stock linker reserves remaining SRAM; this is not measured heap use|
|Main/ISR stack reservation|4,096|Separate from RTOS task stacks|
|FreeRTOS heap_4 region|49,152|Contained within `.bss`; tasks/queues allocate from here|
|Application task stacks|24,576|Contained within RTOS heap, not an additional `.bss` allocation|
|Tensor arena reservation|24,576|Contained within `.bss`; actual arena use awaits AllocateTensors on MCU|

See [section report](build/memory-sections.txt), [ELF section flags](build/elf-sections.txt), [size summary](build/memory-summary.txt) and map. The stock linker reports RAM near 99% because it reserves the unused tail as a NOLOAD C heap. The aggregate `size` text figure also includes sections that are not flash payload; use the linker/section figures above instead of treating aggregate text as flash consumption.

The retained vendor linker warning is a LOAD segment with RWX permissions. It is present with the stock BSP layout; this build does not establish MPU execution-permission isolation. The final compiler log records any remaining warnings. Initial include-path integration failures were resolved by excluding TFLM headers from recursive auto-discovery and adding only intended roots, avoiding FlatBuffers `string.h` shadowing libc.

## Model and test evidence

Model SHA256: `666c12994e155e84e7faa80a956a2e1aa6bb97afee57928bc2a427b6747930a0`. Size: **3016 bytes**. Float32 Keras, float TFLite, fully INT8 TFLite, C embedding, holdout confusion matrix, per-class precision/recall/F1, training history and parity vectors are provided under `models/`. The source of every supplied training/test waveform is artificial. No final accuracy claim is made.

The converter completed and host tests confirm INT8 input/output, integer tensors, expected operators, repeatable saved-vector inference, exact generated C bytes and matching embedded model identity. Host TFLite invocation median was 11.10 µs and p95 16.97 µs on this machine. These are host benchmark values, not MCU or interaction latency. Initial normalization scale, gesture timing and rejection thresholds require physical calibration.

C/Python protocol tests cover the CRC check vector, all payload boundaries, fragmentation, corrupted payload recovery, invalid lengths and timeouts, acknowledged retries and sequence-preserving retransmission. Native firmware C normalization and segmentation are exercised through an executable bridge, including many synthetic waveform replays and C/Python window equality. Recorder provenance tests prevent replay from being recorded as physical data. Qt tests cover seven channels, accepted navigation, smoke/unknown guards and replay provenance.

The source and packaged EXE self-tests construct the dashboard offscreen, feed explicitly synthetic test signals, render plots, test CSV/Parquet exports and exit. These are software checks on the development machine, not a clean Windows install test or USB-UART execution. The EXE is 101,419,386 bytes, unsigned. [Deliverable SHA256](build/deliverable-sha256.json) records the final artifacts.

## Remaining hardware work

Use [FLASH_GUIDE.md](FLASH_GUIDE.md) only as a separate operator decision. Then collect real sessions, confirm raw access and signal feasibility, calibrate normalization, measure completed-scan intervals and end-to-end/inference latency, confirm actual tensor allocation and stack margins, train on physical data, and run SHA-checked device parity. No pinch/spread or multi-finger recognition is claimed. The expected 50 Hz sampling rate is a configured target. Complete [hardware validation template](docs/HARDWARE_VALIDATION_TEMPLATE.md) before treating the recognizer as experimentally validated.
