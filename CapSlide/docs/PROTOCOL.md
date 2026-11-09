# CapSlide NDJSON v1 — axis-toggle controls

KitProg3 USB-UART: 115200 baud, 8N1, no flow control. Device-to-PC only. Each UTF-8/ASCII JSON object ends with LF; CRLF is accepted. Lines are bounded to 256 bytes. Firmware uses a 240-byte transmit buffer and a 50 ms write deadline.

Every message contains integer `v:1`, unsigned 32-bit `seq`, and `type`. Sequence starts at zero on boot and wraps modulo 2^32. Unknown types/versions are rejected. Extra fields are permitted. The existing MOVE/MODE/LEFT_CLICK/RELEASE/STATUS shapes are preserved. BUTTON and a control-profile advertisement are additive v1 extensions.

| Type | Fields in addition to v/seq/type | Meaning |
|---|---|---|
| HELLO | `device:"CapSlide"`, `controls:"toggle-b1-click-b2"` | Boot/profile announcement |
| MODE | `mode:"X"` or `"Y"` | Persistent axis latch changed by B1 |
| BUTTON | `button:1` or `2`, `state:0` or `1` | Debounced physical button edge |
| MOVE | `position:0..100`, `mode:"X"` or `"Y"` | Normalized position on the active axis |
| LEFT_CLICK | `state:0` or `1` | B2 down/up; a held down supports drag |
| RELEASE | no extra fields | Slider release; retain B2 state |
| STATUS | `controls`, `b1:0/1`, `b2:0/1`, `position:-1..100`, `mode`, `tx_errors:uint32` | 500 ms synchronization/heartbeat; −1 means released slider |
| RIGHT_CLICK | `state:0` or `1` | Retained parser compatibility; new firmware does not emit this event |

```json
{"v":1,"seq":0,"type":"HELLO","device":"CapSlide","controls":"toggle-b1-click-b2"}
{"v":1,"seq":1,"type":"MODE","mode":"Y"}
{"v":1,"seq":2,"type":"BUTTON","button":1,"state":1}
{"v":1,"seq":3,"type":"MOVE","position":50,"mode":"Y"}
{"v":1,"seq":4,"type":"BUTTON","button":1,"state":0}
{"v":1,"seq":5,"type":"BUTTON","button":2,"state":1}
{"v":1,"seq":6,"type":"LEFT_CLICK","state":1}
{"v":1,"seq":7,"type":"MOVE","position":75,"mode":"Y"}
{"v":1,"seq":8,"type":"BUTTON","button":2,"state":0}
{"v":1,"seq":9,"type":"LEFT_CLICK","state":0}
{"v":1,"seq":10,"type":"RELEASE"}
{"v":1,"seq":11,"type":"STATUS","controls":"toggle-b1-click-b2","b1":0,"b2":0,"position":-1,"mode":"Y","tx_errors":0}
```

The parser accepts old v1 messages for diagnostics. The serial session requires the exact `controls` value on HELLO or STATUS before enabling input. Missing/different profiles display **Firmware update required** and suppress input. The periodic advertisement allows connection after the boot HELLO has already been sent. Reflash the updated HEX to migrate from the previous B2-hold firmware; restarting the desktop is insufficient.

Numeric schema fields must be integers, excluding booleans and fractions. Missing fields, out-of-range values, invalid axes, malformed/incomplete JSON, and oversized frames are rejected. Oversized input is discarded through the next newline. Partial messages are buffered across reads, never interpreted before newline.

Sequence duplicates are ignored/counted. Gaps or a HELLO cancel current pointer actions and resynchronize. The first accepted message may have any sequence. More than two seconds without valid traffic closes the port; retry occurs after one second. Profile mismatch remains visible while the old firmware continues sending STATUS. Reconnect never invents a down from STATUS. B2=0 clears a lost left release, and position=−1 clears slider motion. Axis in STATUS repairs a missed MODE transition. Firmware TX errors and PC communication errors are displayed separately.

Position changes are throttled to 20 ms (50 Hz). New contact and mode changes may send immediately. Unchanged positions produce no movement events. Button edges, MODE and RELEASE bypass movement throttling. This is a live-control stream, not a guaranteed-delivery event journal.
