# ChordSlide smoke model card

**Status: SYNTHETIC SMOKE TEST ONLY. Not validated for physical gesture recognition.**

- Artifact: `chordslide_int8.tflite`, 3,016 bytes.
- SHA256: `666c12994e155e84e7faa80a956a2e1aa6bb97afee57928bc2a427b6747930a0`.
- Architecture: temporal 5-sample convolution, 12 output channels, stride 2, ReLU; temporal average pooling; eight-output dense softmax. 536 trainable parameters. Conv2D expresses a 1D temporal kernel as `(5,1)` for TFLM compatibility.
- Input: `[1,64,1,7]` INT8. Firmware converts normalized uint8 0..127 values to real 0..1, then applies the TFLite input scale/zero point. Channel order is button0, button1, slider0..4.
- Output: eight INT8 scores dequantized using the output tensor's scale/zero point. Label order is in evaluation.json and protocol/__init__.py.
- Training: deterministic artificial traces from ml/train.py, six artificial groups, 35 examples per class per group, 25 epochs. Last group held out for test, preceding group for validation. Training-only amplitude/time/noise augmentation and representative calibration.
- Intended use: compiler/runtime integration, conversion, serialization, dashboard replay and parity tooling checks.
- Excluded use: accuracy claims, human-subject generalization, reliable laptop control, multi-finger gesture claims or calibration of physical thresholds.

The supplied firmware defines CS_MODEL_TRAINED=0 and always rejects actions with this artifact. It still runs MCU inference so subsequent hardware testing can validate initialization, invocation and serial parity. No inference was executed on a physical MCU during this development run.

`evaluation.json` contains float/INT8 artificial holdout confusion matrices and per-class scores. The host latency numbers refer only to TFLite on this development PC. No real CapSense dataset, physical accuracy, MCU inference latency or actual scan-rate measurement is supplied.

For a final model, record physical UART sessions in the dashboard, include real unsupported gestures as unknown, split by session/person, inspect saturation/noise and timing, train/evaluate on untouched holdouts, install generated C arrays, rebuild firmware, then validate identity and parity on an already-running matching target. See the repository README and hardware validation template.
