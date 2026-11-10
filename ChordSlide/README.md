# ChordSlide

An independent PSoC 6 / FreeRTOS gesture interface and Windows sensor studio for **CYW9P62S1-43438EVB-01**, using only its two CapSense buttons, five slider electrodes, RGB LED and KitProg USB-UART.

**The included CNN is a SYNTHETIC SMOKE TEST model. It is not a validated gesture recognizer.** Firmware runs inference on the MCU and deliberately rejects all gesture actions while `CS_MODEL_TRAINED=0`. Collect real sessions and train/install a collected-data model before assessing recognition or using physical navigation. No board was flashed or modified during development. See [verification](VERIFICATION_REPORT.md) for the actual build/test evidence and remaining hardware work.

## Repository

- `firmware/`: complete five-task CM4 application, local BSP, CapSense, FreeRTOS and Infineon TFLM runtime.
- `sdk/`: local snapshot of SDK dependencies; building does not depend on another application directory.
- `dashboard/`: PySide6/pyqtgraph desktop application; `build/dist/ChordSlide.exe` is the packaged Windows app.
- `ml/`: collection, augmentation, grouped training, INT8 conversion and device parity utility.
- `models/`: float and INT8 smoke models, generated C, evaluation and replay vectors.
- `protocol/`: normative schema, Python framing and reliable command transport.
- `tests/`: protocol corruption, C/Python replay, preprocessing, model and Qt tests.
- `docs/`: hardware evidence, feasibility, architecture and operating procedures.
- `build/`: compiler/package/test logs, memory reports and flash artifacts.

## Set up on Windows

Python 3.11 x64, Windows 10/11, ModusToolbox 3.9, GCC Arm 14.2.1. Native host C tests use MinGW GCC (`gcc` on PATH); a pipe bridge also supports a 32-bit compiler with 64-bit Python.

```powershell
cd C:\Psoc_Projects\ChordSlide
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -WithML
.\.venv\Scripts\python.exe -m dashboard.app
```

For a dashboard-only installation, omit `-WithML`. An existing local `.venv` was used for the recorded checks; reproducible dependency snapshots are in `build/python-freeze.txt`. Use a clean virtual environment for other machines. The EXE does not require Python or the training runtime. It has not been validated on a clean Windows machine.

## Build without flashing

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_firmware.ps1
powershell -ExecutionPolicy Bypass -File scripts\test.ps1
powershell -ExecutionPolicy Bypass -File scripts\package_dashboard.ps1
```

Build tools can be overridden with `-Tools` and `-Compiler` on `build_firmware.ps1`. Its only firmware operation is `make build`; it never calls program/erase/debug. Artifacts are copied to `build/artifacts/`. Programmer use is described separately in [FLASH_GUIDE.md](FLASH_GUIDE.md).

## Collect real data and train

1. Have an operator load the firmware using the separate flash guide. This project generation did not do that.
2. Connect KitProg's USB-UART at 115200 8N1, no flow control. Select its COM port in the dashboard.
3. In **Collect dataset**, follow the per-label instruction, click **Arm next gesture**, then perform it. One accepted 64×7 window is saved per arm. Release before the end of the 1.12 s post-trigger capture. Use **unknown** for broad touches, accidental brushes and unsupported motion. Exclude ambiguous labels.
4. Save session NPZ, export raw telemetry CSV/Parquet, start a new session, and repeat across people, days, placement and environment. Collect all eight labels in every session. Use at least four sessions; target at least 50 independent attempts per class per person and several people. These are collection targets, not evidence of accuracy.
5. Train with session holdouts:

```powershell
.\.venv\Scripts\python.exe -m ml.train data\session1.npz data\session2.npz data\session3.npz data\session4.npz --output models\collected --epochs 40 --install
powershell -ExecutionPolicy Bypass -File scripts\build_firmware.ps1
```

The sorted last session is test; the previous session is validation; remaining sessions are training. Partition by **person** as well for any cross-person claim. Augmentation applies only to training samples; representative calibration uses training only. Quantized evaluation uses the same untouched test split as float evaluation. Grouping is checked before fitting. The source tag is an operator assertion, not authenticated provenance.

The CNN is Conv2D(12, 5×1, stride 2×1, ReLU) applied along time, average pool over the 30 remaining time positions, reshape, Dense(8, softmax). This is a 1D temporal CNN expressed using TFLM's Conv2D operator. Full integer conversion requires INT8 input/output and integer kernels. There is no laptop inference in the operational dashboard.

A smoke reproduction is available, and is always marked synthetic:

```powershell
.\.venv\Scripts\python.exe -m ml.train --smoke --epochs 25 --output models --install
```

It will restore the smoke model and disable MCU gesture actions. Never describe its accuracy as physical sensor accuracy.

## Evaluate integration

After an operator has separately installed a matching model/firmware, device parity can run without programming:

```powershell
.\.venv\Scripts\python.exe -m ml.parity --port COM7 --models models\collected --output build\device-parity.json
```

It verifies the model SHA256, sends normalized recorded test windows to the MCU, and compares eight dequantized probabilities with a 1/256 tolerance. A firmware ACK timeout or model mismatch fails the run. Close the dashboard first so it does not own the port. This command was not run against physical hardware during development.

## Dashboard navigation

With a collected-data model, accepted left/right swipes select adjacent tabs, tap advances, double tap opens Live, long press opens Collect, and slider?button0 / slider?button1 opens Analytics / Settings. Actions are confined to the dashboard. Unknown, truncated, inference-error and smoke-model predictions never navigate. No global keyboard injection or external hardware is needed.

Replay accepts normalized dataset NPZs, labels the source, and visualizes them without inference or recording them as physical data. Analytics loads an `evaluation.json`; live histograms use MCU-reported DWT invocation time. UART logs include ACKs and timeouts. Exports contain a `source` column and an adjacent events JSON. In-memory histories are bounded; export periodically for long sessions.

## Limitations

Hardware scan rate, calibrated sensitivity, sustained throughput, stack margins, arena allocation at runtime, gesture distinguishability, real accuracy, USB cable/COM behavior and actual latency require board execution. Configured 50 Hz is a target, not a measurement. The current normalization saturates at a raw-minus-baseline count of 512; tune this only from real sensor evidence, regenerate datasets/model and rerun parity. The gesture window supports short motions and 700–850 ms holds, not arbitrarily long presses. Multi-touch/pinch/spread is not claimed.

## Packaged application self-test

The shipped EXE was launched and passed its offscreen self-test on this machine. It rendered the dashboard and exported CSV/Parquet without opening hardware. Reproduce with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_exe.ps1
python scripts\audit_deliverables.py
```

The report, screenshot and exported data are `build/exe-self-test.json` and its adjacent `.png`, `.csv` and `.parquet` files. `build/verification.json` summarizes evidence, and `build/deliverable-sha256.json` identifies the firmware, model and EXE. The EXE self-test is not a physical UART or clean-machine installation test.
