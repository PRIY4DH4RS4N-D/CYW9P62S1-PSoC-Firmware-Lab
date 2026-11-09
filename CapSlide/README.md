# CapSlide — Mini Desk

A local Windows desktop simulation controlled by the CYW9P62S1-43438EVB-01 PSoC 6 board's two CapSense buttons and five-segment slider. Python 3.11+, PySide6, pyserial, FreeRTOS. No models or inference libraries are used.

Run **`dist/CapSlide.exe`** for the standalone app, or **`dist/CapSlide.exe --simulator`** without hardware. No Python installation is required to run the EXE. The connected development board has been programmed and verified on **COM22**; run `dist/CapSlide.exe --port COM22` to connect directly. Other boards require programming the supplied firmware first; see [FLASH_GUIDE.md](FLASH_GUIDE.md).

In the GitHub repository, recorded deliverables are published under **[prebuilt/](prebuilt/README.md)**: [Windows EXE](prebuilt/CapSlide.exe), [firmware HEX](prebuilt/CapSlide.hex), and verification records. `dist/` and `build/` are regenerated locally and excluded from Git.

The animated navy/cyan workspace contains Calculator, Notes with a touch keyboard and local save, an interactive mock File Explorer, pointer Settings, and System Monitor. Launch applications using desktop icons or Launch. Drag a title bar, resize from the bottom-right grip, minimize/maximize/restore/close, and switch through the taskbar. Right-click with the fallback mouse opens the context menu; physical controls can use Launch for the same actions. Input stays inside CapSlide and never controls other Windows applications.

| Physical input | Action |
|---|---|
| Button 1 short press | Toggle X ↔ Y once per debounced press; mode persists after release |
| Slider in X | Horizontal movement across the full window width |
| Slider in Y | Vertical movement across the full window height |
| Button 2 press/release | Left mouse down/up: click/select |
| Button 2 hold + slide | Drag the pressed control/window on the active axis |
| Slider release | Stop movement; B2 stays down until physically released |

This is sequential two-axis control from one one-dimensional slider. It does not sense independent simultaneous X/Y positions.

The header animates the X/Y mode switch. The control deck shows five slider segments, physical button states, live coordinates, click/drag/release feedback, serial status, event rate and FPS. The pointer has a fading movement trail and click rings. Settings saves speed, smoothing, sensitivity, endpoint snap zone and accent theme locally.

Axis switching freezes the old target and anchors the new axis to the first received slider position. Move toward either end to reach the complete axis range. If switching while the slider is at an endpoint, the HUD shows PICKUP until it crosses the current pointer position. This avoids a mode-switch jump. Coordinates scale with window resizing. See [touch mapping](docs/TOUCH_MAPPING.md) for the mapping formula.

## Setup from source

```powershell
git clone https://github.com/PRIY4DH4RS4N-D/CYW9P62S1-PSoC-Firmware-Lab.git
cd CYW9P62S1-PSoC-Firmware-Lab\CapSlide
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python main.py --simulator
.venv\Scripts\python main.py --port COM22
```

Without `--port`, the app starts disconnected. Click Refresh ports, then the COM selection button to open the in-app port list. Select KitProg3 USB-UART. Selection opens the port at 115200 8N1. The label says Connected only after firmware advertises `toggle-b1-click-b2`. An older build displays Firmware update required: flash the updated HEX. Serial failure or two seconds without valid messages cancels held controls and retries the selected port every second. Close any other terminal using the port.

## Simulator and mouse fallback

Enable Simulator in the control panel. Tap B1 Axis or F6 to toggle axes; press B2 Select or F7 to click, and hold it to drag. The same 30 ms debounce applies. Left/right arrow keys move the simulated slider; Space toggles slider touch when the desktop has keyboard focus. F6/F7 work across child widgets. Mouse controls support UI testing, including the simulator panel. Simulator events use the same pointer engine and dispatch path as hardware messages. The actual C state machine is separately host-compiled and checked against simulator traces.

## Build and test

```powershell
.venv\Scripts\python scripts\build_firmware.py
.venv\Scripts\python -m pytest -q
.venv\Scripts\python scripts\package_app.py
dist\CapSlide.exe --smoke-test build\exe-smoke.json
.venv\Scripts\python scripts\verify_exe.py --port COM22
```

Firmware builds use installed ModusToolbox 3.9 and Arm GCC 14.2.1; paths can be overridden with `--tools` and `--compiler`. Host tests require `gcc` on PATH. Firmware HEX/ELF/MAP/BIN and SHA-256 records are in `build/artifacts` and `build/artifact-sha256.json`. Use the HEX for programming.

## Layout

`firmware/` preserves the supplied BSP, generated CapSense files, FreeRTOS configuration, and required middleware. `sdk/` is this repository's own SDK copy. `main.py`, `serial_manager.py`, `event_parser.py`, `touch_engine.py`, `mini_desk.py`, `app_manager.py`, `widgets/`, and `assets/` implement the app. No imports or build paths depend on ChordSlide, FalseTouch-Shield, or TouchRGB.

See [architecture](docs/ARCHITECTURE.md), [protocol](docs/PROTOCOL.md), [touch mapping](docs/TOUCH_MAPPING.md), [testing](docs/TESTING.md), and [verification report](docs/VERIFICATION.md).

## Troubleshooting

- No COM port: connect the board through KitProg3 USB, check its Windows driver and Device Manager, then Refresh ports. Board power alone does not establish USB-UART.
- UART open but no valid events: confirm CapSlide firmware is flashed, 115200 8N1, and the correct COM port. Another project's binary protocol is rejected.
- Access denied: close serial terminals and other desktop instances, then allow the automatic retry.
- Pointer moves along the wrong axis: tap B1 once and check the header mode. B2 is selection/drag and does not change axis.
- Firmware update required: the board is running the previous hold-B2 control mapping. Flash the new `build/artifacts/CapSlide.hex`; restarting Python alone cannot change firmware controls.
- Pointer pauses just after switching axes: the first sample anchors the pointer. If PICKUP appears, slide toward the current pointer coordinate, then continue normally. This is endpoint handling that avoids a jump.
- A missed release or USB unplug: status reconciles left-button release; disconnect cancels pending clicks/drag without activating the pressed control.
- Touch won't register: leave electrodes untouched during startup calibration and use the original board jumper configuration. No pin rewiring is required.
- Windows EXE: this is an unsigned build. Verify its hash and run on the same x64 Windows architecture used to build it. Windows system libraries remain OS prerequisites.

Notes save to Qt's per-user application-data directory (`CapSlide/CapSlide/notes.txt`), separate from the repository. File Explorer displays a mock hierarchy.

To record live hardware events and pointer targets without simulation, run `dist/CapSlide.exe --port COM22 --record-uart build/session.ndjson`. Add `--run-seconds 120` for an automatically closing diagnostic session. This captures validated UART events; it does not generate physical input.
