# CYW9P62S1 · PSoC Firmware Lab

Embedded firmware projects for the **Infineon CYW9P62S1-43438EVB-01** PSoC 6 development board, with source code, preserved board configuration, reproducible build instructions and verification records.

## TouchRGB — CAPSense RGB Color Controller

Control the board's RGB LED directly with its two capacitive buttons and five-segment slider. Select a color, adjust brightness, choose a custom RGB preset, or run an automatic color demo.

| Feature | Implementation |
|---|---|
| Touch controls | Two CapSense buttons, five-segment slider, debounce and touch/release events |
| Operating modes | Color wheel, categorized presets, brightness, custom RGB and demo |
| Color engine | 24-bit RGB, HSV conversion, 30 named colors and eight custom presets |
| Light output | Onboard LED5, three 1 kHz hardware PWMs, gamma correction and smooth fades |
| Firmware | Modular C, one FreeRTOS application task and asynchronous scanning |
| Monitoring | Optional USB serial status at 115200 baud; no graphical dashboard |
| Build | ModusToolbox 3.9, Arm GCC 14.2.1 and included local SDK |

**[Project README](TouchRGB/README.md) · [Flash guide](TouchRGB/FLASH_GUIDE.md) · [Download firmware HEX](TouchRGB/prebuilt/TouchRGB.hex)**

### Get started

```powershell
git clone https://github.com/PRIY4DH4RS4N-D/CYW9P62S1-PSoC-Firmware-Lab.git
cd CYW9P62S1-PSoC-Firmware-Lab\TouchRGB
python scripts\test.py
python scripts\verify_bsp.py
python scripts\build_firmware.py
python scripts\verify_release.py
```

Install Python 3.11+, native GCC for host tests, and the toolchain listed in the [flash guide](TouchRGB/FLASH_GUIDE.md). The SDK and middleware are included; no neighboring workspace project is needed. To use the recorded build directly, follow the [prebuilt firmware instructions](TouchRGB/prebuilt/README.md).

### Physical controls

| Input | Action |
|---|---|
| Capacitive Button 1 / CSB1 | Cycle through the five modes |
| Slider | Choose hue, preset slot, brightness or demo speed according to mode |
| Capacitive Button 2 / CSB2 | Confirm a preset/custom color, or step brightness |
| Hold CSB2 while releasing the slider in preset mode | Advance the color category |

The mechanical push buttons are separate from the capacitive controls. Leave the electrodes untouched during startup calibration.

### Documentation

| Guide | Contents |
|---|---|
| [Project overview](TouchRGB/README.md) | Setup, complete controls, serial monitoring and module architecture |
| [Build and flash](TouchRGB/FLASH_GUIDE.md) | Tool paths, KitProg3 programming and troubleshooting |
| [Color system](TouchRGB/docs/COLOR_SYSTEM.md) | HEX/RGB color table, HSV, gamma, brightness and interpolation |
| [Hardware wiring](TouchRGB/docs/HARDWARE_WIRING.md) | Verified LED pins, polarity, resistors, diagrams and source references |
| [Testing](TouchRGB/docs/TESTING.md) | Software coverage, limitations and physical acceptance procedure |
| [Recorded build](TouchRGB/prebuilt/README.md) | HEX/ELF/BIN/MAP artifacts, checksums and verification records |

### Verification status

Firmware compilation/linking and software checks passed. The recorded firmware uses **57,040 bytes of flash**. Tests include **92,160 HSV reference vectors**, **140,608 RGB round trips**, input handling, transitions, operating modes and PWM-driver call contracts. All **187 preserved BSP files** match their snapshot hashes.

The vendor linker layout emits one documented RWX LOAD-segment warning. **Physical flashing, touch sensitivity and LED output have not been verified for this firmware.** The repository includes a bench procedure for those checks; software tests do not establish physical operation.

## Repository layout

```text
TouchRGB/
├── firmware/       Application C, FreeRTOS, BSP and CapSense middleware
├── sdk/            Local versioned SDK dependencies
├── scripts/        Build, test and release-verification tools
├── tests/          Native firmware tests and HAL contract tests
├── docs/           Color reference, hardware diagrams and testing guide
├── prebuilt/       Recorded firmware artifacts and verification evidence
├── FLASH_GUIDE.md
└── README.md
```

The application uses no machine learning, inference or model training. TouchRGB application code is MIT-licensed; vendor components retain their original licenses and notices. See [LICENSE](TouchRGB/LICENSE).
