# Pointer-control diagnosis and correction

The inspected firmware was implementing the initial project's hold-based scheme, not the requested persistent-toggle scheme. `firmware/gesture.c` had no B1 mode transition. It started a 350 ms timer on B2 down, entered Y only after that timer expired, and reset `vertical=false` on B2 release. Thus a B1 tap could never select Y, and B2 short presses emitted right-click instead. Normal slider MOVE packets were X outside the hold interval. This is a firmware state-machine/control-mapping cause, not a missing Qt vertical coordinate implementation.

`firmware/main.c` correctly read both generated widgets and the real slider centroid, serialized `mode` on MOVE/STATUS, and used the preserved BSP UART aliases. `event_parser.py` already accepted both X and Y, and `TouchEngine.apply` already assigned Y movement to `ty`. Those working SDK and UART components were retained. No evidence warranted changing pins, sensor configuration, or generated APIs.

The correction changes the full pipeline:

1. B1 rising edge after 30 ms debounce toggles a persistent axis latch. No hold timer exists. Holding does not repeat.
2. B2 down/up drives LEFT_CLICK; holding plus motion uses existing pressed-target drag handling.
3. BUTTON edges expose both physical buttons independently from their assigned action. MODE precedes same-sample movement; STATUS includes the latched mode.
4. HELLO/STATUS advertise `toggle-b1-click-b2`. The serial layer flags legacy firmware instead of claiming Connected with incompatible controls.
5. Python STATUS release recovery uses **B2**, replacing the old B1 check. The dashboard no longer infers B2 state from Y mode or B1 state from a click.
6. Axis changes anchor the new coordinate rather than immediately applying the previous axis's absolute slider position to it. Normalized resizing, configurable response and endpoint handling are implemented in the engine, not as a visual-only pointer override.

Regression coverage includes host-compiled C parity, deterministic repeated B1 taps/holds/bounce, B2 click/drag/up, MODE/MOVE/STATUS synchronization, both axes at five positions and multiple sizes, endpoint pickup, live-event parsing, and ten minutes of simulated movement. GUI tests pass events through actual virtual-mouse dispatch to application windows. See VERIFICATION.md for the observed physical session and its limits.
