# Firmware build and programming

The firmware is built for **CYW9P62S1-43438EVB-01**, using the copied and unchanged board configuration. Do not substitute a similarly named kit target. No external electrodes or UART wiring are needed.

1. Confirm the physical board model and original power/debug jumpers. Connect its KitProg3 USB connector to Windows using a data cable. Leave CapSense electrodes untouched during reset/calibration.
2. Build with `.venv\Scripts\python scripts\build_firmware.py`. The script only compiles, links, and checks artifacts; it never flashes, resets, or updates KitProg.
3. Open ModusToolbox Programmer, select the intended KitProg3 probe, and program **`build/artifacts/CapSlide.hex`**. This replaces the application currently on that board. Use the HEX with its embedded addresses; do not program the flat BIN at address zero.
4. Alternatively, run `make -C firmware program` in the installed ModusToolbox shell as an explicit operator programming step. Ensure the tool/compiler paths match `firmware/Makefile`.
5. Close the programmer/other serial terminals. Run `dist\CapSlide.exe`, refresh ports, and select the KitProg3 USB-UART COM port. UART is 115200 baud, eight data bits, no parity, one stop bit, no flow control.
6. Expect a valid STATUS every 500 ms with `controls:"toggle-b1-click-b2"` and the current `mode`. HELLO appears only after boot and may have occurred before the port opens. The desktop can connect using STATUS without resetting the board. Firmware without this control identifier is shown as Firmware update required.
7. Tap **B1** to toggle X/Y; release must retain the selected mode and holding must not toggle repeatedly. Sweep the slider in each mode. Use **B2** for left click/selection, or hold B2 while sliding to drag. Neither axis control nor selection requires a hold threshold. Verify slider release and unplug/replug using [TESTING.md](docs/TESTING.md).

For recorded validation, close the app and run:

```powershell
.venv\Scripts\python scripts\capture_uart.py --port COM22 --seconds 30 --output build\physical-touch-capture.json
```

COM22 was enumerated as KitProg3 on the development PC; COM numbers can change. USB enumeration alone does not verify this firmware or touch operation. See [VERIFICATION.md](docs/VERIFICATION.md) for the exact work performed.

The updated firmware was flashed and verified on the connected board during this upgrade. A user-operated physical session subsequently recorded X/Y movement, persistent axis toggles and B2 clicks. Do not reuse the old HEX from the initial release: the Python dashboard cannot add axis toggling to that older firmware.

The generated board configuration maps UART RX/TX to P5.0/P5.1; firmware uses `CYBSP_DEBUG_UART_RX/TX`. CapSense Button0 and Button1 share RX P1.0 and use TX P8.1/P8.2. Slider sensors use P8.3–P8.7. These values were inspected in `cycfg_peripherals.h` and `cycfg_pins.h`; preserve the generated files.
