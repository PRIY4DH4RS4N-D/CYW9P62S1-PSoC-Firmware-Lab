# Testing

Run `.venv\Scripts\python -m pytest -q`. Host GCC must be on PATH for the actual C gesture-state-machine test. Qt GUI tests use the offscreen platform and isolated Qt test application-data paths.

Tests cover valid/invalid JSON, framing and oversized-frame recovery, coordinate bounds, X/Y independence, time-based smoothing, release behavior, button bounce/short press/hold/drag, duplicate clicks, STATUS release recovery, serial open failures, timeouts, sequence gaps, partial buffers on port change, and unplug/reconnect with injected serial objects. A deterministic trace of 3,300 samples is executed by both the compiled firmware C state machine and Python simulator. GUI tests dispatch through the same virtual pointer path as hardware: app launching, calculator input, touch keyboard, context menu, dragging, resizing, minimizing, closing, taskbar restore, and disconnect cancellation.

Build firmware with `python scripts/build_firmware.py`. Inspect `build/firmware-build.log`, memory reports, unresolved-symbol report, and SHA-256 records. A successful compiler/link result proves build compatibility, not touch sensitivity, timing under physical noise, or board operation.

Build EXE with `python scripts/package_app.py`, then run:

```powershell
dist\CapSlide.exe --smoke-test build\exe-smoke.json
dist\CapSlide.exe --simulator --smoke-test build\exe-simulator-smoke.json
```

Smoke mode launches all five apps, writes a report including `frozen:true`, and exits. Simulator smoke also processes a movement event; hardware smoke reports actual UART events. It exercises packaged imports/assets, Qt, and no-hardware startup. Running it on the build PC is not a clean-VM deployment test. For a deployment acceptance test, copy only `dist/CapSlide.exe` to a clean x64 Windows PC without Python, start disconnected, then connect/select the programmed board.

`python scripts/verify_exe.py --port COM22` automates disconnected, simulator, and live-hardware startup from temporary directories, checks the reports, and records the executable SHA-256. Omit `--port` to run without hardware.

## Physical acceptance procedure — operator required

1. Program CapSlide HEX and record board revision, firmware SHA, port, Windows version, and USB driver version.
2. Leave electrodes untouched during boot. Confirm STATUS at approximately 500 ms intervals and no unexpected input while idle for a minute.
3. Sweep slider to both ends in X; verify 0–100 and pointer endpoints. Tap B1 once to select Y and repeat. Release B1 and verify Y stays selected. Check that the inactive coordinate remains fixed. Account for the documented switch anchor/pickup behavior.
4. Tap B2 to select/launch. Hold B2 on a window title, slide in X, then tap B1 while B2 remains held and slide in Y; verify one continuous drag and clean release.
5. Tap B1 repeatedly with deliberate finger bounce; verify one toggle per debounced press and no repeated toggles during a hold. Use Launch or the fallback mouse for context-menu actions.
6. Lift the slider during movement, including a B2 drag. Verify immediate target freeze and continued left hold until B2 release.
7. Unplug USB while dragging/pressing an app button. Verify no stuck button or accidental activation, disconnected status within two seconds, and reconnection when the same COM device returns.
8. Verify noisy input/malformed UART data increments errors without crashing. Verify the other project's binary firmware is rejected rather than interpreted as pointer input.
9. Exercise every app, window focus, taskbar restore, context menu, Notes save/reopen, and keyboard control entirely through touch.
10. Record results from `scripts/capture_uart.py` or `main.py --port COM22 --record-uart build/session.ndjson` and the event monitor. See VERIFICATION.md for physical checks already observed and those still pending.
