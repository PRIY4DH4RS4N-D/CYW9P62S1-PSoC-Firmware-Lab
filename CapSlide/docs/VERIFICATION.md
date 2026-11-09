# CapSlide verification

This report covers the working B1-axis-toggle / B2-click version saved for publication on **9 November 2026**. The firmware and physical touch session were verified on **7 November 2026**. No hardware was reflashed as part of publishing the repository.

## Software and build checks

- **56 automated tests passed again on 9 November 2026.** Coverage includes host-compiled firmware C parity, B1 repeated presses/hold/bounce, B2 click/drag/release, both axes at five positions and multiple window sizes, endpoint pickup, normalized resizing, protocol validation, serial recovery and interactive application/window behavior. A ten-minute simulated input test is included.
- The preserved **188 BSP/board configuration and FreeRTOS configuration files** match `board-config-sha256.json`. No board pin mappings or CapSense configuration were changed.
- Updated firmware compiled with ModusToolbox 3.9 and GCC Arm 14.2.1, using the project's own SDK and middleware. Flash verification recorded **53,172 bytes**. HEX, ELF, BIN, MAP and artifact SHA-256 records are included in `prebuilt/`.
- The standalone Windows EXE was rebuilt from the saved application source for publication. Disconnected and simulator startup are checked from unrelated temporary working directories by `scripts/verify_exe.py`; reports and SHA-256 records are published in `prebuilt/verification/`.
- Build and cache directories, Python environments, nested Git metadata and runtime user data are excluded from publication. Source copies include vendor license notices. Other projects are not build dependencies.

## Physical evidence — 7 November 2026

After the user's explicit authorization, the updated firmware was programmed through KitProg3. OpenOCD reported **Verified OK** and reset the board. UART ran on **COM22 at 115200 8N1** and advertised `controls:"toggle-b1-click-b2"`.

During a user-operated dashboard recording, the validated UART stream contained:

| Observation | Recorded result |
|---|---|
| X movement | 505 MOVE events, reported positions 0–100 |
| Y movement | 422 MOVE events, reported positions 9–92 |
| Axis switching | Three MODE transitions: Y, X, Y |
| Button 2 selection | Two left-down/up cycles |
| Sequence continuity | Zero gaps |
| Firmware UART errors | `tx_errors:0` |

The recorded pointer coordinates changed in both X and Y. The user confirmed: **“i tested its working”**. A machine-readable summary is included with the prebuilt verification records. This establishes physical axis switching, movement in both axes and selection for that observed session.

## Limits

- The physical Y sweep did not cover reported 0 and 100. Full-range mapping is covered by automated tests; physical endpoint calibration remains a separate bench check.
- Long-duration physical dragging, deliberate noise/bounce characterization, measured scan timing and actual USB unplug/replug were not separately verified. Drag and disconnect/reconnect behavior are covered by automated tests with synthetic input/transports.
- The EXE startup checks run on the development Windows PC. A clean Windows machine without Python remains a deployment acceptance check.
- The inherited BSP linker layout emits one RWX LOAD-segment warning. Board configuration is preserved; build, flash verification and live UART succeeded.
- The executable is unsigned. No fresh physical test is claimed for the publication date.

See [TESTING.md](TESTING.md) for reproducible software checks and the remaining physical acceptance procedure, and [POINTER_FIX.md](POINTER_FIX.md) for the diagnosed firmware-to-Python correction.
