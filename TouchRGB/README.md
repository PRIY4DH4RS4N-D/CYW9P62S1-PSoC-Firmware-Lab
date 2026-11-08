# TouchRGB ? CAPSense RGB Color Controller

Standalone CapSense RGB controller for **CYW9P62S1-43438EVB-01**. Firmware uses the board's LED5 RGB LED, two capacitive buttons and five-segment capacitive slider. No additional hardware is required. All lighting runs on the board; the USB serial terminal is optional.

The project contains modular C firmware, an independent local SDK, the original matching BSP and generated CapSense configuration, software tests, and build/programming instructions. It contains no machine learning or inference components.


| Platform | Control | Output | Runtime |
|---|---|---|---|
| CYW9P62S1-43438EVB-01 / PSoC 6 | Two CapSense buttons + five-segment slider | Onboard LED5, three 1 kHz hardware PWMs | C + FreeRTOS |

**30 named colors ? 8 custom RGB presets ? 5 modes ? 24-bit RGB ? Gamma 2.2 ? Smooth transitions**

[Quick start](#build-and-use) ? [Controls](#controls) ? [Serial monitoring](#serial-monitoring) ? [Architecture](#architecture) ? [Color reference](docs/COLOR_SYSTEM.md) ? [Wiring](docs/HARDWARE_WIRING.md) ? [Tests](docs/TESTING.md)

## Build and use

Run these commands from the repository root after cloning:

```powershell
cd .\TouchRGB
python scripts\test.py
python scripts\verify_bsp.py
python scripts\build_firmware.py
python scripts\verify_release.py
```

Use Python 3.11+, native GCC for software tests, ModusToolbox tools 3.9 and Arm GCC 14.2.1 for firmware. The build script accepts `--tools`, `--compiler`, and `--clean`. It uses the copied, pinned SDK without fetching dependencies. See [FLASH_GUIDE.md](FLASH_GUIDE.md) to program `build/artifacts/TouchRGB.hex` with KitProg3.

## Prebuilt firmware

To program the recorded build directly, use [prebuilt/TouchRGB.hex](prebuilt/TouchRGB.hex). See [prebuilt instructions and checksums](prebuilt/README.md). The HEX, ELF, BIN, MAP, and build/test records are included; generated build caches are excluded.

## Controls

Leave the touch electrodes untouched during power-up calibration. Startup selects red at 50% brightness with a 180 ms fade from off. Tap **capacitive Button 1 (CSB1)** to cycle modes 1 through 5. These are not the mechanical SW2/SW4 switches.

| Mode | Slider | Capacitive Button 2 (CSB2) |
|---|---|---|
| 1 Color wheel | Hue 0–359 degrees across the spectrum | Cycle brightness to next 25% step, wrapping 100% to off |
| 2 Color presets | Choose one of six slots in the current category | Tap to apply selected color; hold while releasing the slider to advance category |
| 3 Brightness | Set 0–100%, retaining current color | Next 25% brightness step |
| 4 Custom RGB | Choose one of eight structured RGB presets | Tap to apply |
| 5 Demo | Transition interval 300–10000 ms, left = fast | Next 25% brightness step |

Preset categories cycle **warm hues → greens → blues → pinks → neutrals**. In mode 2, to advance a category, hold B2, touch and release the slider, then release B2. Each slider release advances one category; this gesture initially confirms the old selection on B2 press. The selection resets to slot zero after advancing. Normal slider browsing leaves the applied output unchanged until confirmation. Categories and slots are zero-based in serial status. To select white, advance four categories from startup's category zero, choose leftmost slot, then tap B2. Use the table in [COLOR_SYSTEM.md](docs/COLOR_SYSTEM.md).

## Serial monitoring

There is no graphical dashboard in this version. Use a serial terminal for live firmware status; no PC application is required for touch-controlled lighting.

USB-UART at **115200 8N1**, no flow control, emits status every 500 ms: mode, category, slot, selected `RGB=RRGGBB`, target brightness, buttons, slider (0–1000 or -1), and demo speed. This reports firmware state; it does not measure emitted light. Simultaneous button presses give B1 priority.

## Architecture

| Module | Responsibility |
|---|---|
| `capsense_input.c` | Async middleware scanning, 100 ms scan timeout, input validation, touch/release events, 30 ms button and 20 ms slider debounce |
| `color_engine.c` | 24-bit RGB, integer HSV conversions, 30 named colors, eight custom RGB values, gamma lookup and interpolation |
| `rgb_output.c` | Three inverted 1 kHz hardware PWMs, checked SDK calls, off initialization and fault shutdown |
| `touch_controller.c` | Five modes, confirmations, brightness ramp, retargetable color fades, demo timing |
| `main.c` | One 5 ms FreeRTOS application task, bounded optional UART reporting, fault hooks |

The scheduler also runs its idle task. Software timers are disabled; the FreeRTOS heap is 16 KiB and the application stack is 1024 words. Scans start and complete on separate service calls, normally producing a new frame every 10 ms or longer if sensing takes longer. Fades continue while scanning; there are no busy waits or blocking delay loops in normal operation. Gamma uses a 512-byte constant table and no runtime `pow()`. Faults latch the LED cathodes high until reset; debugger variable `fault_code` identifies the cause.

All source dependencies are under `firmware/` and `sdk/`; other workspace repositories are not needed to build. Their configuration was read and copied, not edited. BSP hashes are recorded in `docs/bsp-sha256.json`. Original vendor notices and licenses remain with their files. Application code is supplied under the MIT license in [LICENSE](LICENSE).

See [hardware and sources](docs/HARDWARE_WIRING.md), [color system](docs/COLOR_SYSTEM.md), and [test results and physical acceptance procedure](docs/TESTING.md). Software tests and a successful firmware link cannot establish physical LED output, touch sensitivity, or startup electrical behavior; those require the bench procedure.

## Verification status

| Check | Result |
|---|---|
| Arm GCC firmware compilation and linking | Passed; 57,040 bytes of flash |
| HSV reference tests | Passed; 92,160 vectors |
| RGB round-trip tests | Passed; 140,608 vectors |
| Gamma, brightness, slider, buttons, modes and transitions | Passed |
| PWM driver call contract and error cleanup | Passed with mock HAL |
| Preserved BSP/configuration | 187 files match the recorded hashes |
| HEX checksums, addresses, BIN consistency and release hashes | Passed |
| Physical LED output, touch sensitivity and flashing | Not yet verified |

The preserved BSP linker layout produces one documented RWX LOAD-segment warning. See [testing and limitations](docs/TESTING.md) for the exact scope of software verification and the bench acceptance procedure.

## Documentation

- [Flash guide](FLASH_GUIDE.md): tool paths, building, programming and troubleshooting.
- [Color system](docs/COLOR_SYSTEM.md): all 30 HEX/RGB presets, HSV conversions, gamma, brightness and custom values.
- [Hardware wiring](docs/HARDWARE_WIRING.md): verified pins, polarity, resistor values and circuit diagrams.
- [Testing](docs/TESTING.md): test coverage, recorded results and physical verification procedure.
