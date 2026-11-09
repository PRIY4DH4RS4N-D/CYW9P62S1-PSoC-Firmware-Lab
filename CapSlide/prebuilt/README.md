# Prebuilt CapSlide Mini Desk

Recorded deliverables for the **CYW9P62S1-43438EVB-01** PSoC 6 board and x64 Windows. This snapshot uses the corrected **B1 axis toggle / B2 click and drag** control scheme.

## Downloads

| File | Purpose |
|---|---|
| [CapSlide.exe](CapSlide.exe) | Standalone Windows desktop application; Python is not required |
| [CapSlide.hex](CapSlide.hex) | Firmware image for normal KitProg3 programming |
| [CapSlide.elf](CapSlide.elf) | Linked firmware/debug image |
| [CapSlide.map](CapSlide.map) | Linker memory map |
| [CapSlide.bin](CapSlide.bin) | Flat archival binary; use the HEX for programming |

On GitHub, open a file and use **Download raw file**. Download the EXE itself rather than the HTML file-view page.

## Run and connect

1. Confirm the board model and program `CapSlide.hex` using ModusToolbox Programmer and KitProg3. Programming replaces the application currently on that board. Keep the capacitive electrodes untouched during startup calibration.
2. Run `CapSlide.exe`. Select the KitProg3 USB-UART COM port from the control deck. UART is **115200 8N1**. The correct firmware advertises `toggle-b1-click-b2`; older firmware is reported as requiring an update.
3. Tap capacitive B1 to toggle X/Y; use the slider to move on the selected axis. B2 selects/clicks, or stays held to drag. Use Launch to open applications.

```powershell
.\CapSlide.exe --simulator
.\CapSlide.exe --port COM22
```

COM22 was used during development; use the actual port assigned on your PC. Simulator mode works without hardware. Input controls only the CapSlide workspace.

## Verify the download

[verification/sha256.json](verification/sha256.json) contains SHA-256 checksums for every supplied binary. For example:

```powershell
Get-FileHash .\CapSlide.exe -Algorithm SHA256
Get-FileHash .\CapSlide.hex -Algorithm SHA256
```

The executable is unsigned. It was rebuilt for publication on 9 November 2026. Disconnected and simulator startup checks run from temporary working directories; reports are included below. A clean Windows PC without Python remains a deployment acceptance check.

## Verification evidence

- [Automated tests](verification/pytest-results.xml): 56 passing tests.
- [Disconnected EXE startup](verification/exe-disconnected-smoke.json) and [simulator EXE startup](verification/exe-simulator-smoke.json).
- [Firmware build log](verification/firmware-build.log), [compiler version](verification/compiler-version.txt) and [memory summary](verification/memory-summary.txt).
- [Firmware programming/verification log](verification/firmware-program.log), recorded 7 November 2026.
- [Physical-session summary](verification/physical-session-summary.json): user-operated X/Y movement, axis toggles and B2 click cycles, with no sequence gaps or firmware TX errors.

The user confirmed that the physical controls worked. Prolonged physical dragging, actual USB unplug/replug, physical Y endpoint calibration and clean-PC deployment are not claimed as completed. See the full [verification report](../docs/VERIFICATION.md).

To rebuild, follow the [project README](../README.md#build-and-test) and [flash guide](../FLASH_GUIDE.md). Build outputs go to `build/artifacts/` and `dist/`; this folder is the published snapshot.
