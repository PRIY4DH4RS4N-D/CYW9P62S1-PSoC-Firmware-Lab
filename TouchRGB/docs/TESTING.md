# Verification and acceptance

## Software verification

Run from the project root:

```powershell
python scripts\test.py
python scripts\verify_bsp.py
python scripts\build_firmware.py --clean
```

The first command compiles the actual portable C modules using native GCC with warnings treated as errors. It writes `build/software-tests.log` and returns a nonzero exit code on failure. No Python packages are required for building or running these tests.

| Check | Coverage |
|---|---|
| HSV to RGB | All 360 integer hues, 16 saturation values and 16 value values: 92,160 vectors against an independent floating point reference, channel error <=1 |
| RGB to HSV | Primary/secondary exact values; 140,608 RGB grid round trips, per-channel error <=5 |
| RGB representation | Pack/unpack boundary/grid checks; required orange, purple and pink constants |
| Gamma | All 256 entries checked against independently evaluated gamma 2.2; endpoints and monotonicity |
| Brightness | Every 8-bit channel at every percentage 0–100; clamping, zero and full scale |
| Slider | All 1001 normalized positions, monotonic hue 0–359 and endpoint clamping |
| Inputs | Bounce cancellation, delayed press/release, held-button single event, second button, slider touch/release, retained last position, timer wrap |
| Transitions | Initial off, fade endpoints, halfway values, zero duration, retarget continuity, timestamp wrap |
| Controller | Every mode, simultaneous-press priority, all categories, preset/custom confirmation, brightness zero/full/step, demo interval and cycling |
| PWM driver contract | Correct symbolic pins, explicit inversion, 1 kHz, zero duty before start, midpoint/full duty, allocation failures and cleanup, update failure and latched off |
| BSP | 187 copied board/configuration files checked against SHA-256 snapshot |
| Arm firmware | Actual installed SDK compile/link, ELF unresolved-symbol check, exported HEX/ELF/MAP/BIN and artifact hashes |

The PWM contract test uses mock HAL/GPIO functions and does **not** simulate the TCPWM peripheral. Native tests exclude the hardware-specific CapSense adapter; the real adapter is compiled by the Arm build and requires the physical board to exercise.

Software checks passed on 7 November 2026. Exact final build evidence is in `build/firmware-build.log`, `build/memory-sections.txt`, `build/undefined-symbols.txt`, and `build/artifact-sha256.json`. Run `python scripts/verify_release.py` after a build to generate `build/verification.json` with artifact, source and Intel HEX checks. No board was programmed or physically tested during this implementation.

The preserved vendor linker layout produces an Arm GCC linker warning about an ELF LOAD segment with RWX permissions. `build/elf-segments.txt` records segment flags. The supplied layout places writable sections into executable program segments; it is retained to preserve the BSP. This is not a compiler error, and no source compilation warnings were observed. The ELF flags do not establish a hardware memory-protection policy. No claim of a warning-free link is made.

The final application consumes 57,040 bytes of flash including the CM0+ image and initialized data. `.bss` is 18,940 bytes, including the 16 KiB FreeRTOS heap; see the section report for vector, initialized-data and stack reservations. The vendor linker reserves remaining RAM as `.heap`, so GNU `size`'s aggregate `text` column includes that reservation and is not actual flash consumption. Use the ModusToolbox flash report and individual sections when assessing memory.

## Physical verification procedure — not yet performed

Record board revision, firmware HEX SHA-256, programmer verification result, power/jumper configuration, instruments, observations and pass/fail for each step. A terminal readout only establishes reported firmware state; it does not establish emitted light.

1. Program the HEX per [FLASH_GUIDE.md](../FLASH_GUIDE.md). Keep electrodes untouched during reset. Confirm there is no sustained full-brightness flash during startup and that red settles to 50%. Use an oscilloscope for short startup glitches if required.
2. Connect an oscilloscope ground to board GND. Probe P1.1, P0.5 and P7.3 using accessible test/header connections identified in the board guide. Confirm idle-off cathodes are HIGH and active PWM LOW pulses repeat at approximately 1 kHz. Avoid shorts between adjacent pins.
3. In wheel mode, sweep the slider slowly end-to-end. Expect red → yellow → green → cyan → blue → magenta → near-red, with smooth fades. Lift the finger and confirm the selected color remains. Move rapidly and reverse direction to check fade retargeting without flashes.
4. Tap CSB1 once per mode and verify the serial `mode` changes 1→2→3→4→5→1. Hold CSB1 for two seconds and verify only one mode advance. Apply short touches below the debounce threshold and check for accidental transitions; actual sensor middleware adds its own response time. Press both capacitive buttons together and verify B1 priority when their debounced edges coincide.
5. In preset mode, sweep the slider without B2: output must remain unchanged. Tap B2 to apply. Hold B2, touch and release the slider, then release B2 to advance category. Repeat for all five categories. Confirm selection index and applied `RGB` against the color table.
6. Select red, green and blue independently through presets. At 100% brightness, the chosen channel must remain LOW and other channels HIGH; at 50%, its LOW duty should be approximately 50% after the ramp. For a mid-level encoded channel such as orange's green=128, expect gamma-adjusted light duty near 21.95% at full brightness. The actual HAL period quantizes the duty.
7. Select white, warm white, cool white and black. White should drive all channels; black should drive none regardless of brightness. Warm/cool white are RGB mixes, not calibrated white emitters or color temperatures. Judge visual differences separately from digital values.
8. Enter brightness mode. Sweep from 0% to 100% on a fixed color, watching gradual intensity changes. Confirm 0% holds all channels HIGH and 100% restores that color. Tap B2 through 25/50/75/100/0; confirm no held-button repeat and a smooth 180 ms ramp.
9. Enter custom mode. Select all eight slots and confirm with B2. Check emitted channel ratios and reported HEX against `custom_presets[]`. Changes to custom values require rebuilding and flashing.
10. Enter demo mode. Confirm automatic color changes, left slider gives ~300 ms intervals, right slider ~10 seconds, and B1 exits promptly. Repeat with brightness at zero and restore it via B2.
11. Leave the board untouched for ten minutes under full white, then under fast demo. Check no false mode, brightness or category changes. Exercise both buttons and slider while PWM is active. Record sensitivity/noise issues rather than treating a compile as evidence of noise immunity.
12. Reset with each mode active; startup must return to wheel/red/50%. Settings are intentionally volatile. Unplug/reconnect USB and repeat. Disconnect a serial terminal or leave it closed: lighting must remain responsive.
13. In a debugger, inspect each failure path through controlled fault injection in a separate test build. Confirm PWM initialization/update or CapSense errors lead to LED-off and a stable `fault_code`. Restore and reflash the unmodified release HEX afterward. Do not modify electrodes or short pins to induce faults.

Measure touch-to-output latency with a scope/logic analyzer where needed. The application services every 5 ms, normally processes scans every 10 ms, adds 30 ms button / 20 ms slider debounce, then fades for 180 ms. These are scheduling/design parameters, not measured latency guarantees. The 100 ms scan watchdog prevents a permanently busy scan from leaving lighting running indefinitely.

## Limits

No physical LED output, PWM waveform, touch sensitivity, debounce timing at the electrodes, color accuracy, electrical startup behavior or flashing result is claimed verified. RGB values are encoded digital requests. Optical gamut, channel currents, LED binning and PWM resolution limit physical color output. Gamma 2.2 is an approximate transfer curve and does not replace photometric calibration.
