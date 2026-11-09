# Verification Report

## Current ML status: LIVE DATASET PENDING

Real touch recordings have not yet been collected or labelled. Production `firmware/model.h` remains **untrained** and returns **UNKNOWN, confidence 0**. A real classifier must be trained and evaluated on labelled live recordings before ML deployment. No physical touch accuracy is claimed.

## Recorded development verification (2026-11-07)

| Category | Result | Evidence |
|---|---|---|
| Firmware | BUILD VERIFIED, exact board target and complete link | [Clean build log](prebuilt/verification/firmware-clean-build-2.log) |
| Reproducibility | Two clean HEX outputs identical | [Hashes](prebuilt/verification/reproducibility.json) |
| Flash use | 53,016 / 1,048,576 bytes | [Memory report](prebuilt/verification/MEMORY_REPORT.md) |
| Symbols | No unresolved symbols | [Symbol report](prebuilt/verification/undefined-symbols.txt) |
| Host tests | HOST TEST VERIFIED: 16 passed | [Test log](prebuilt/verification/host-tests.log) |
| Feature parity | C and Python streaming feature implementations agree | Host native tests |
| Learned-tree export | 1,129 synthetic vectors match native C and Python | [Parity log](prebuilt/verification/ml-parity.log) |
| Windows packaging | EXE built; independent offline launch, exit 0 | [Frozen-app record](prebuilt/verification/dashboard-exe-smoke.json) |
| Desktop preview | Seven empty sensor curves, zero events, no hardware connection | [Preview](prebuilt/verification/dashboard-exe-smoke.png) |

The recorded HEX SHA256 is `D3591B6E7AD4AE817B61B45FA8E92A8A4A93C65B538A98DEAA9307DB9885DB7F`. The inherited BSP linker emits one documented RWX LOAD segment warning; no application compiler warnings were recorded. The linker reserves unused CM4 RAM as a C heap, so its region occupancy is not actual runtime consumption. The FreeRTOS 49,152-byte heap is included in the 51,240-byte BSS.

Synthetic evaluation and confusion-matrix files under `ml/synthetic_smoke` are explicitly artificial. They validate pipeline operation, not physical touch recognition. Native C parity does not establish Cortex-M4 inference parity.

## Repository publication (2026-11-09)

The project is published as an independent `FalseTouch-Shield/` subdirectory, with local SDK dependencies, preserved BSP/vendor licenses, source, firmware artifacts and a ZIP containing the complete Windows runtime folder. The firmware Makefile now resolves dependencies from this project's `sdk/`, rather than the original workstation's neighbouring `mtb_shared/`. New publication checks are recorded in `prebuilt/verification/PUBLICATION_CHECKS.md`.

The original virtual environment, temporary build trees, workstation uninstall logs and unrelated environment inventories are excluded from publication. Preserved development logs may contain original build paths; they describe the recorded development build rather than a new hardware test.

## HARDWARE NOT TESTED

No FalseTouch-Shield firmware was flashed during this work. Actual calibration/sensitivity, seven physical channels, UART traffic/ACKs, RGB feedback, scan deadlines, watchdog recovery, task stack/heap high-water marks, inference timing, actual MCU parity and touch accuracy are **NOT VERIFIED**.

The collection, grouped training/evaluation, C export and UART MCU parity tools are implemented, but the live collection, real-data model training and physical deployment/acceptance steps remain pending. See [DATA_COLLECTION.md](docs/DATA_COLLECTION.md), [ML evaluation status](ml/EVALUATION.md) and [FLASH_GUIDE.md](FLASH_GUIDE.md).
