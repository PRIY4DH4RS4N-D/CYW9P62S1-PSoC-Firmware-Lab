# ChordSlide wire protocol v1 (normative)

115200 baud, 8 data bits, no parity, 1 stop bit, no flow control. All multi-byte integers and IEEE754 float32 values are little endian. No C structure is transmitted directly; firmware writes integer fields at defined offsets and copies float32 fields. `schema.json` is the machine-readable message table and `tests/test_protocol.py` enforces C/Python framing parity.

Frame: `A5 5A | version:u8=1 | type:u8 | sequence:u16 | payload_length:u16 | payload | crc:u16`.
CRC16-CCITT-FALSE: poly 0x1021, init 0xffff, refin/refout false, xorout 0; coverage starts at version and ends at payload. Test vector ASCII `123456789` ? 0x29B1. Max payload 512, max frame 522. Embedded sync bytes are legal in payload. Invalid version/oversize/CRC cause a one-byte resync search. Partial frames expire after 200 ms between input chunks/bytes. Receiver buffers are bounded for the C implementation; Python trims consumed bytes after feed.

Each endpoint increments its own sequence modulo 65536 for every transmitted frame. Command retries repeat the original sequence and exact bytes. Commands are idempotent: ping, setting a value, querying identity, and inference of a fixed input have no repeated external action. Firmware may repeat ACK/parity responses for a retry. Host removes a pending command only if ACK request sequence and command kind both match. Status 0=success, 1=invalid, 2=busy, 3=inference failure. Host retries after 600 ms up to three attempts. A lost result can be retried as the same parity input; `ml.parity` fails rather than silently accepting a missing result.

Telemetry/predictions are streaming best-effort, not retransmitted or ACKed. Sequence gaps and firmware drop counts expose losses. Commands always receive an ACK when accepted/invalid/busy, subject to link/queue loss. A queue drop can lose an ACK; host retries resolve idempotent operations. MCU tick timestamps are uint32 milliseconds and wrap. Detect modular gaps; do not treat a reboot as continuous sampling.

Channel order everywhere: **button0, button1, slider0, slider1, slider2, slider3, slider4**. Normalized bytes use 0..127. Type 18's payload is row-major 64×7 in that order. It is already normalized; firmware does not subtract baselines again.

See schema.json for exact struct formats. Prediction type2 flags: bit0 truncated, bit1 synthetic model, bit2 inference failure. Class7 is unknown. Confidence rejection additionally uses probability = configured permille and top-two margin =0.15. Prediction payload length is 74 bytes; feature order: duration_ms, peak, signed_slider_travel, mean_energy, mean_button0, mean_button1. Type1 is 39 bytes, type3 is 26 bytes, type4 is 34 bytes. Type5 carries 64 ASCII hexadecimal SHA256 characters; command19 queries it, allowing model identity verification before parity. ACK is a separate type128 four-byte payload.

Frame corruption checks and a valid CRC protect against accidental transport damage, not hostile senders. No authentication is implied. Do not send arbitrary console text on this UART.
