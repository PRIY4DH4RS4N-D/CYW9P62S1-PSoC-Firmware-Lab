# Final firmware memory report

Target: APP_CYW9P62S1-43438EVB-01 / CY8C6247BZI-D54, Release, GCC ARM 14.2.1.

- Flash utilized: 53,016 / 1,048,576 bytes (5.06%).
- CM0+ prebuilt image: 6,580 bytes.
- CM4 text: 45,084 bytes.
- BSS: 51,240 bytes, including the 49,152-byte FreeRTOS heap.
- Initialized data: 1,300 bytes; shared data: 12.
- RAM vector table: 652 bytes; noinit: 204.
- Main stack reservation: 4,096 bytes.
- Remaining C-heap address reservation: 227,160 bytes (not runtime consumption).
- Raw BIN span: 54,628 bytes; includes flash address gaps.
- Undefined symbols: none (empty undefined-symbols.txt).
- Identical clean-build HEX: True.
- HEX SHA256: `D3591B6E7AD4AE817B61B45FA8E92A8A4A93C65B538A98DEAA9307DB9885DB7F`.

Actual task stack/heap high-water marks and inference latency are HARDWARE NOT TESTED.
The inherited BSP linker emits an RWX LOAD segment warning; compiler warnings are absent.
