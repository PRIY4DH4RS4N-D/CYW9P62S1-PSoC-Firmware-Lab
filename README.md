# CYW9P62S1 · PSoC Firmware Lab

Embedded firmware projects for the **Infineon CYW9P62S1-43438EVB-01** PSoC 6 development board, with source code, preserved board configuration, reproducible build instructions and verification records.

## Projects

| Project | What it does | Get started |
|---|---|---|
| **[ChordSlide](ChordSlide/README.md)** | Seven-channel FreeRTOS acquisition, MCU INT8 temporal CNN, guided dataset recording and Windows gesture dashboard. **Included model is synthetic-only; physical training/validation is pending.** | [Windows EXE](ChordSlide/build/dist/ChordSlide.exe) / [Firmware HEX](ChordSlide/build/artifacts/ChordSlide.hex) / [Verification](ChordSlide/VERIFICATION_REPORT.md) |
| **[FalseTouch-Shield](FalseTouch-Shield/README.md)** | Seven-channel touch acquisition, false-touch baseline, ML collection/training pipeline and Windows dashboard. **Live dataset collection is pending; production ML is untrained.** | [Windows ZIP](FalseTouch-Shield/prebuilt/FalseTouch-Shield-Windows-x64.zip) / [Firmware HEX](FalseTouch-Shield/prebuilt/firmware/FalseTouch-Shield.hex) / [Verification](FalseTouch-Shield/VERIFICATION_REPORT.md) |
| **[CapSlide Mini Desk](CapSlide/README.md)** | Touch-controlled Windows virtual desktop with persistent X/Y axis switching, click/drag, five interactive apps and live hardware telemetry | [Windows app](CapSlide/prebuilt/CapSlide.exe) · [Firmware HEX](CapSlide/prebuilt/CapSlide.hex) · [Flash guide](CapSlide/FLASH_GUIDE.md) |
| **[TouchRGB](TouchRGB/README.md)** | Standalone capacitive RGB controller with color wheel, presets, brightness and demo modes | [Firmware HEX](TouchRGB/prebuilt/TouchRGB.hex) · [Flash guide](TouchRGB/FLASH_GUIDE.md) |

Each project includes its own SDK and board configuration. Choose the firmware for the application you want: programming any project replaces the application currently on the board.

## ChordSlide - Temporal Gesture CNN and Dataset Studio

ChordSlide uses the onboard two CapSense buttons and five-segment slider to acquire seven sensor channels, segment 64?7 temporal windows, and run a compact INT8 temporal CNN on the PSoC 6 using Infineon TFLM with CMSIS-NN. Its PySide6/pyqtgraph Windows dashboard includes live waveforms and heatmap, probability bars, guided recording, timeline, confusion matrix, latency histogram and CSV/Parquet export.

**The included model is a synthetic smoke-test model, not a validated physical gesture recognizer.** Firmware rejects gesture actions until a model trained on collected data is installed. No pinch/spread or multi-finger recognition is claimed.

| Evidence | Status |
|---|---|
| Firmware | **BUILD VERIFIED**; ELF, HEX, BIN and map included; 130,484-byte flash address span |
| Host software | **HOST TEST VERIFIED**; 16 passed, one hardware parity test skipped |
| Windows EXE | Packaged and launched; offscreen rendering and CSV/Parquet export self-test passed |
| ML pipeline | Synthetic-only training, float evaluation, INT8 conversion and embedding verified |
| Physical data, scan rate, MCU inference latency and device parity | **HARDWARE NOT TESTED**; no serial ports were available during development |
| Programming | No board was flashed or modified for ChordSlide |

Download the [Windows EXE](ChordSlide/build/dist/ChordSlide.exe) using **Download raw file**. The ChordSlide EXE is included directly in Git and does not require LFS. See the [project README](ChordSlide/README.md), [model card](ChordSlide/models/MODEL_CARD.md), [signal feasibility](ChordSlide/docs/FEASIBILITY.md), [verification report](ChordSlide/VERIFICATION_REPORT.md) and [operator flash guide](ChordSlide/FLASH_GUIDE.md). Build caches, virtual environments and package-download caches are excluded; the recorded final artifacts and reports remain under `ChordSlide/build/`.

## FalseTouch-Shield - Touch Classification and Dataset Collection

FalseTouch-Shield combines FreeRTOS firmware with a PySide6/pyqtgraph dashboard for the onboard two CapSense buttons and five slider segments. It includes seven sensor traces, event segmentation, a threshold baseline, dataset recording/labelling, CSV/Parquet export, CRC-protected UART and a portable C decision-tree training/export pipeline.

> **Live dataset collection and ML deployment are pending.** Real touch recordings have not yet been collected or labelled. Production firmware deliberately reports **UNKNOWN with zero confidence** for ML predictions. The separate synthetic smoke model validates software plumbing only; it does not demonstrate real touch accuracy or deployment readiness.

| Evidence | Status |
|---|---|
| Firmware | Clean builds verified; recorded ELF, HEX, BIN and map included |
| Host software | 16 tests passed in recorded development verification |
| Windows app | Packaged and launched independently in an offline smoke check |
| Model export | Synthetic-only native C/Python parity checked on 1,129 vectors |
| Live dataset / real ML evaluation | **Pending: data has not been collected and production ML is untrained** |
| Board validation | **Not flashed or physically tested for this project** |

Download the [Windows ZIP](FalseTouch-Shield/prebuilt/FalseTouch-Shield-Windows-x64.zip), extract the entire folder, and run its EXE. The application displays actual board messages; it does not generate fake sensor activity. See the [project README](FalseTouch-Shield/README.md), [flash guide](FalseTouch-Shield/FLASH_GUIDE.md), [data collection procedure](FalseTouch-Shield/docs/DATA_COLLECTION.md) and [verification report](FalseTouch-Shield/VERIFICATION_REPORT.md).

## CapSlide — Touch-Controlled Mini Desk

Use the PSoC 6 as a physical input device for a PySide6 desktop simulation on Windows. The workspace includes Calculator, locally saved Notes, a mock File Explorer, pointer Settings and System Monitor. Windows can be dragged, resized, minimized, maximized and switched through the taskbar.

| Input | Action |
|---|---|
| Capacitive Button 1 | Tap to toggle the persistent X/Y axis; holding does not repeat |
| Five-segment slider | Move the pointer horizontally in X or vertically in Y |
| Capacitive Button 2 | Left-click/select; hold while sliding to drag |
| Slider release | Stop movement while preserving a held selection button |

The dashboard shows an animated axis indicator, pointer trail, five-segment touch visualization, button states, coordinates, connection status, event rate and FPS. USB-UART uses KitProg3 at **115200 8N1**. This is sequential control of two axes using one one-dimensional slider.

**[Project README](CapSlide/README.md) · [Download/build instructions](CapSlide/prebuilt/README.md) · [Protocol](CapSlide/docs/PROTOCOL.md) · [Control mapping](CapSlide/docs/TOUCH_MAPPING.md) · [Verification](CapSlide/docs/VERIFICATION.md)**

### Run CapSlide

Download [CapSlide.exe](CapSlide/prebuilt/CapSlide.exe) using GitHub's **Download raw file** action. The standalone x64 Windows app does not require a Python installation. Flash [CapSlide.hex](CapSlide/prebuilt/CapSlide.hex), then select the board's COM port in the app. COM22 was used during development; select the actual port assigned by Windows.

```powershell
# Hardware-independent desktop testing
.\CapSlide.exe --simulator

# Connect to an already-programmed board
.\CapSlide.exe --port COM22
```

For source setup and rebuild commands, see the [CapSlide README](CapSlide/README.md#setup-from-source).

### CapSlide verification

**56 automated tests passed**, covering the compiled firmware gesture logic, both axes, debounce, coordinate mapping, serial recovery and interactive desktop behavior. The updated firmware was flashed and verified. A user-operated COM22 session recorded X/Y movement, three axis toggles and Button 2 click cycles with no sequence gaps or firmware TX errors; the user confirmed the controls worked. Long-duration physical dragging, actual USB unplug/replug and clean-PC deployment remain separate acceptance checks. See the [verification report](CapSlide/docs/VERIFICATION.md) for evidence and limits.

## TouchRGB — CAPSense RGB Color Controller

Control the board's RGB LED directly with its two capacitive buttons and five-segment slider. Select a color, adjust brightness, choose a custom RGB preset, or run an automatic color demo.

| Feature | Implementation |
|---|---|
| Touch controls | Two CapSense buttons, five-segment slider, debounce and touch/release events |
| Operating modes | Color wheel, categorized presets, brightness, custom RGB and demo |
| Color engine | 24-bit RGB, HSV conversion, 30 named colors and eight custom presets |
| Light output | Onboard LED5, three 1 kHz hardware PWMs, gamma correction and smooth fades |
| Firmware | Modular C, one FreeRTOS application task and asynchronous scanning |
| Monitoring | Optional USB serial status at 115200 baud; no graphical dashboard |
| Build | ModusToolbox 3.9, Arm GCC 14.2.1 and included local SDK |

**[Project README](TouchRGB/README.md) · [Flash guide](TouchRGB/FLASH_GUIDE.md) · [Download firmware HEX](TouchRGB/prebuilt/TouchRGB.hex)**

### Get started

```powershell
git clone https://github.com/PRIY4DH4RS4N-D/CYW9P62S1-PSoC-Firmware-Lab.git
cd CYW9P62S1-PSoC-Firmware-Lab\TouchRGB
python scripts\test.py
python scripts\verify_bsp.py
python scripts\build_firmware.py
python scripts\verify_release.py
```

Install Python 3.11+, native GCC for host tests, and the toolchain listed in the [flash guide](TouchRGB/FLASH_GUIDE.md). The SDK and middleware are included; no neighboring workspace project is needed. To use the recorded build directly, follow the [prebuilt firmware instructions](TouchRGB/prebuilt/README.md).

### Physical controls

| Input | Action |
|---|---|
| Capacitive Button 1 / CSB1 | Cycle through the five modes |
| Slider | Choose hue, preset slot, brightness or demo speed according to mode |
| Capacitive Button 2 / CSB2 | Confirm a preset/custom color, or step brightness |
| Hold CSB2 while releasing the slider in preset mode | Advance the color category |

The mechanical push buttons are separate from the capacitive controls. Leave the electrodes untouched during startup calibration.

### Documentation

| Guide | Contents |
|---|---|
| [Project overview](TouchRGB/README.md) | Setup, complete controls, serial monitoring and module architecture |
| [Build and flash](TouchRGB/FLASH_GUIDE.md) | Tool paths, KitProg3 programming and troubleshooting |
| [Color system](TouchRGB/docs/COLOR_SYSTEM.md) | HEX/RGB color table, HSV, gamma, brightness and interpolation |
| [Hardware wiring](TouchRGB/docs/HARDWARE_WIRING.md) | Verified LED pins, polarity, resistors, diagrams and source references |
| [Testing](TouchRGB/docs/TESTING.md) | Software coverage, limitations and physical acceptance procedure |
| [Recorded build](TouchRGB/prebuilt/README.md) | HEX/ELF/BIN/MAP artifacts, checksums and verification records |

### Verification status

Firmware compilation/linking and software checks passed. The recorded firmware uses **57,040 bytes of flash**. Tests include **92,160 HSV reference vectors**, **140,608 RGB round trips**, input handling, transitions, operating modes and PWM-driver call contracts. All **187 preserved BSP files** match their snapshot hashes.

The vendor linker layout emits one documented RWX LOAD-segment warning. **Physical flashing, touch sensitivity and LED output have not been verified for this firmware.** The repository includes a bench procedure for those checks; software tests do not establish physical operation.

## Repository layout

```text
FalseTouch-Shield/
|-- firmware/       FreeRTOS acquisition, baseline, portable inference and BSP
|-- sdk/            Included versioned SDK dependencies
|-- dashboard/      PySide6 + pyqtgraph application and serial worker
|-- ml/             Collection, features, training, evaluation and C export
|-- protocol/       Shared codec and documented UART framing
|-- tests/          Protocol, C parity, training and dashboard checks
|-- scripts/        Setup, build, test and Windows packaging
|-- docs/           Architecture, hardware research and dataset procedure
|-- prebuilt/       Windows ZIP, firmware artifacts and verification evidence
|-- VERIFICATION_REPORT.md
|-- FLASH_GUIDE.md
|-- README.md

CapSlide/
├── firmware/       FreeRTOS touch input, UART, preserved BSP and middleware
├── sdk/            Independent versioned SDK dependencies
├── widgets/        Desktop windows, pointer, icons and telemetry widgets
├── assets/         Dashboard theme
├── tests/          Firmware parity, protocol, pointer, serial and GUI tests
├── scripts/        Firmware/app builds, UART capture and EXE verification
├── docs/           Architecture, protocol, controls and verification
├── prebuilt/       Windows EXE, firmware and verification records
├── main.py         PySide6 application entry point
├── FLASH_GUIDE.md
└── README.md

TouchRGB/
├── firmware/       Application C, FreeRTOS, BSP and CapSense middleware
├── sdk/            Local versioned SDK dependencies
├── scripts/        Build, test and release-verification tools
├── tests/          Native firmware tests and HAL contract tests
├── docs/           Color reference, hardware diagrams and testing guide
├── prebuilt/       Recorded firmware artifacts and verification evidence
├── FLASH_GUIDE.md
└── README.md
```

TouchRGB uses no machine learning, inference or model training. FalseTouch-Shield includes an ML pipeline, with live data collection and production ML deployment still pending. TouchRGB application code is MIT-licensed; vendor components retain their original licenses and notices. See [LICENSE](TouchRGB/LICENSE).
