# FalseTouch-Shield UART protocol v1

USB-UART via KitProg3; 115200 baud, 8 data bits, no parity, one stop bit, no flow control. All multibyte integers and IEEE754 float32 values use little endian. Never send text to this binary stream.

| Offset | Bytes | Meaning |
|---|---:|---|
| 0 | 2 | magic A5 5A |
| 2 | 1 | version = 1 |
| 3 | 1 | message type |
| 4 | 2 | sequence, wraps modulo 65536 |
| 6 | 2 | payload length, maximum 128 |
| 8 | n | payload |
| 8+n | 2 | CRC16 CCITT-FALSE over bytes 2 through 7+n |

CRC polynomial 0x1021, init 0xFFFF, no reflection, no final XOR. `123456789` gives 0x29B1. Sequence numbers are independent in each direction; device increments on every transmitted frame. Dropped frames are detectable, but samples/events are not retransmitted. CRC is error detection, not authentication.

| Type | Direction | Payload |
|---|---|---|
| 1 SAMPLE | device → host | uint32 ms, uint16 diff[7] (18 bytes) |
| 2 EVENT | device → host | uint32 ID, uint32 end_ms, float32 features[6], uint8 prediction, uint8 baseline, float32 confidence, uint32 queue_drops (42 bytes) |
| 3 HEALTH | device → host | uint32 uptime_ms, uint32 queue_drops, uint32 fault, uint8 model_trained (13 bytes) |
| 4 INFERENCE | device → host | uint16 request_seq, uint8 prediction, float32 confidence (7 bytes) |
| 0x10 PING | host → device | empty |
| 0x11 THRESHOLD | host → device | uint16 activity threshold, allowed 10–4000 |
| 0x12 CALIBRATE | host → device | empty; remove fingers before issuing |
| 0x13 INFER | host → device | float32 features[6] (24 bytes); runs the MCU model for parity |
| 0x80 ACK | device → host | uint16 request_seq, uint8 request_type, uint8 status (4 bytes) |

ACK statuses: 0 completed successfully, 1 unsupported command/length, 2 invalid threshold, 3 calibration failure, 5 command queue full. Inference produces a result and ACK. ACKs are queued after execution, not merely receipt. The host waits two seconds then reports outcome unknown; it does not silently retry. All supported commands are safe to reissue, but calibration runs again and duplicate inference requests produce duplicate results. No exactly-once guarantee is claimed. Corrupt frames get no ACK. Invalid headers/CRC discard one byte and search again. Incomplete frames expire after a 200 ms receive gap. A corrupt in-range length can delay synchronization until enough bytes arrive or the gap expires. Sequence gaps and CRC failures should invalidate affected dataset sessions.

Prediction IDs: TAP=0, HOLD=1, GRAZE=2, WIDE=3, UNKNOWN=255. TAP/HOLD are accepted; GRAZE/WIDE rejected. UNKNOWN is neither. Confidence is a tree leaf class proportion, not a calibrated probability. The supplied firmware model abstains with confidence zero because physical training data is unavailable.

Channels: button0, button1, slider0, slider1, slider2, slider3, slider4. Features: duration_ms, peak difference, maximum number of channels above activity threshold, mean sum of seven differences per frame, accumulated absolute weighted-centroid travel (channel index ×100), sample count. See `firmware/core.c` and `ml/features.py` for identical definitions. Sensor differences are processed CapSense values; raw counts/baselines are held by the middleware, not sent by this protocol.
