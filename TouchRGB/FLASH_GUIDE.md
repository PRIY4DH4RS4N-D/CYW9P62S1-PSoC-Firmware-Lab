# Build and flash TouchRGB

## Use the recorded build

The repository includes [prebuilt/TouchRGB.hex](prebuilt/TouchRGB.hex). Verify its [SHA-256 checksum](prebuilt/README.md), then follow the programming steps below using that file. To regenerate firmware, use the rebuild steps.

## Rebuild

Default installed tool paths are:

```text
C:/Infineon/Tools/ModusToolbox/tools_3.9
C:/Infineon/Tools/mtb-gcc-arm-eabi/14.2.1/gcc
```

From PowerShell, starting in the repository root:

```powershell
cd .\TouchRGB
python scripts\verify_bsp.py
python scripts\test.py
python scripts\build_firmware.py --clean
```

For another installation:

```powershell
python scripts\build_firmware.py --tools C:/path/to/tools_3.9 --compiler C:/path/to/gcc
```

The script adds ModusToolbox's `modus-shell/bin` to PATH for its child processes, builds `APP_CYW9P62S1-43438EVB-01` in Release with GCC_ARM, and exports HEX, ELF, MAP and BIN into `build/artifacts/`. Compiler version, build log, ELF sections, unresolved-symbol check, memory reports and SHA-256 hashes are saved under `build/`. It performs no programming or reset operation. Use the SDK shipped here; `make getlibs` is unnecessary and can change dependency resolution.

## Program

1. Confirm board model **CYW9P62S1-43438EVB-01**, factory power/debug jumper setup and no attached shield driving LED/CapSense pins. Connect a data-capable USB cable to **J6, KitProg3**, not just J7 (the MCU USB connector).
2. In ModusToolbox Programmer, connect to the intended KitProg3 probe and select **`TouchRGB.hex`** from `build/artifacts/` after rebuilding, or from `prebuilt/` for the recorded build. Programming replaces the application on that board. Program and verify, then reset/run. Leave the capacitive electrodes untouched during calibration.
3. Alternatively, open a ModusToolbox shell, change to this project, and run:

```sh
make -C firmware program
```

4. Confirm red appears at 50% after calibration, then exercise each mode with CSB1/CSB2 and the slider. Optional: open the KitProg3 USB-UART port at 115200 8N1. Identify its actual COM port in Device Manager; no fixed COM number is assumed.
5. Follow [the physical acceptance procedure](docs/TESTING.md). Record the programmed artifact hash, board revision, test instrument settings and results.

The HEX contains address information and the CM0+ sleep image required by this BSP. Use the HEX for ordinary programming. The BIN is a diagnostic flat image and must not be written at address zero. ELF is available for debugging in ModusToolbox.

## Troubleshooting

- No probe: use J6 and a data USB cable, check KitProg3 driver/enumeration and close other debug sessions. Select the correct probe when several are attached.
- Build cannot find tools: supply `--tools` and `--compiler`; verify those folders contain `modus-shell/bin/make.exe` and `bin/arm-none-eabi-gcc.exe` respectively.
- SDK missing: restore the local `sdk/`, `firmware/vendor/`, and `firmware/libs/` contents. The project does not reference neighboring projects.
- LED stays dark: brightness may be zero or black may be selected. Reset and inspect serial output. If halted, inspect `fault_code`: 1 allocation failure, 2 stack overflow, 3 sensing initialization, 4 sensing scan/process failure or timeout, 5 PWM update, 6 BSP initialization, 7 PWM initialization, 8 task creation, 9 scheduler return. All faults latch the LED off.
- Touch absent: use capacitive CSB1/CSB2, keep fingers clear during reset and preserve factory CapSense jumpers. Check raw status changes and allow debounce time. Do not replace the generated configuration with another board's files.
- Preset browsing does not change output: tap CSB2 to confirm. For category advance, hold CSB2 while releasing the slider. A 500 ms status interval can miss a short tap; this is not a loss of the internal button event.
- Wrong or inverted colors: compare the board revision and wiring against the schematic. The supplied driver uses onboard LED5 with active-low PWM and is not configured for a common-cathode external LED.
- No serial text: select the actual KitProg3 COM port, close other terminals, and use 115200 8N1. A serial init failure does not prevent standalone touch control. A CapSense/PWM failure stops normal operation.
