# Operator flash guide — NOT EXECUTED

No flash, erase, debug attach, reset, board reconfiguration or KitProg firmware update was performed by the development process. Build and host tests do not need a connected board.

1. Read VERIFICATION_REPORT.md. The supplied model is synthetic and gesture navigation is disabled.
2. Inspect/rebuild firmware using `powershell -ExecutionPolicy Bypass -File scripts\build_firmware.ps1`.
3. Verify the physical board is CYW9P62S1-43438EVB-01 and your power/debug jumpers match its kit guide. Connect KitProg USB. Do not attach external sensors or LEDs.
4. When you explicitly decide to program, use ModusToolbox Programmer to select the KitProg probe and `build/artifacts/ChordSlide.hex`. The HEX includes board-default startup sections; a flat BIN is only an archival representation and must not be blindly programmed at address zero.
5. Alternatively, an operator can run `make -C firmware program` from the ModusToolbox shell **as a separate explicit programming action**. None of the supplied automation runs it.
6. Open the COM port in the dashboard at 115200 8N1. Confirm ACK to Ping, model status, seven live channels and health messages. Red after an attempted gesture is expected for the smoke model.
7. Measure idle noise, scan intervals, touch amplitude and saturation. Record real sessions, train a collected-data model, rebuild, then decide separately whether to program the new HEX.
8. Run `python -m ml.parity --port COMx --models models\collected` against the already-running matching firmware. Inspect actual arena use, free stack watermarks and drop counter before accepting a build for operation.

Record the model SHA, HEX SHA, board revision, actual scan interval histogram, inference p50/p95/max, arena bytes, stack watermarks, runtime faults and per-class physical validation. A successful compiler/link result does not establish these hardware properties.
