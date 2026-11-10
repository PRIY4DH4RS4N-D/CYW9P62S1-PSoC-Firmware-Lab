# Hardware validation record template

Status: HARDWARE NOT TESTED. No connected serial ports were found during development.

Record these on an already programmed board, separately from software build verification:

- Firmware/HEX SHA256 and model SHA256; board and kit revision.
- Startup status, model identity command19, successful AllocateTensors and actual arena bytes.
- Requested and observed scan intervals, p50/p95/max, active-scan duration, jitter, queue drops over 30 minutes.
- Per-channel idle noise, baseline tracking, touched amplitude, normalization saturation and crosstalk.
- Actual inference DWT p50/p95/max, with clock frequency recorded. Include end-to-end action latency separately.
- Each task's minimum free stack words, minimum free RTOS heap, UART error/loss observations.
- Parity results for exported test vectors against matching firmware/model SHA.
- Independent-session/person physical confusion matrix, per-class precision/recall/F1 and unknown false accepts per hour.
- Tap/double-tap gap overlap, long-press baseline drift, slider/button reachability and contact ambiguity.

Current telemetry provides sample timestamps, drops, inference microseconds, arena bytes and five task stack watermarks. A logic-analyzer scan-time measurement would require external hardware and is outside this project's allowed equipment; measure completed-scan timestamps and software instrumentation using the built-in board/USB-UART only.

Do not replace missing measurements with the configured 50 Hz or the host TFLite benchmark. Do not call the synthetic model's test metrics sensor accuracy.
