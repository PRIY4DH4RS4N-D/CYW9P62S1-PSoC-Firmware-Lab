# Programming guide — instructions only, no board was flashed

Target: **CYW9P62S1-43438EVB-01**, build BSP `APP_CYW9P62S1-43438EVB-01`, device `CY8C6247BZI-D54`. Programmer: onboard KitProg3. Firmware HEX includes the BSP's CM0+ sleep image and CM4 application; do not substitute an ELF built for another kit.

1. Review `VERIFICATION_REPORT.md` and rebuild with `scripts/build_firmware.ps1 -Clean`. The default model is intentionally untrained and will display UNKNOWN for ML events, with baseline classifications separately available.
2. When you choose to program the board, attach a USB data cable from the PC to **J6 (KitProg3 USB Micro-B)**. J7 is the target MCU USB connector and does not provide this application's UART path. Keep normal kit jumpers and the supported 3.3 V configuration. No external programmer or wiring is required.
3. Verify KitProg3 appears in Windows Device Manager. Use its primary PSoC UART COM port, rather than the secondary wireless-module UART. Close the dashboard and other COM port users before programming.
4. If programmer detection fails, inspect KitProg3 mode with SW3 and consult the [official kit guide](https://www.infineon.com/assets/row/public/documents/30/44/infineon-cyw9p62s1-43438evb-01-psoc-62s1-wi-fi-bt-pioneer-kit-guide-usermanual-en.pdf), section 2.2.1. Do not guess a firmware-loader mode sequence for an unknown KitProg firmware revision.
5. Program through the installed ModusToolbox target configuration. These commands are provided for you to execute later; they have **not** been executed during this task:

```powershell
cd CYW9P62S1-PSoC-Firmware-Lab\FalseTouch-Shield
$env:PATH='C:\Infineon\Tools\ModusToolbox\tools_3.9\modus-shell\bin;'+$env:PATH
make -C firmware program
```

Alternatively, open Infineon Programmer, select the detected KitProg3 and matching device, load `prebuilt\firmware\FalseTouch-Shield.hex` (or your rebuilt `build\artifacts\FalseTouch-Shield.hex`), then program and verify using its GUI. Do not use the raw BIN in a generic programmer without the correct base address and target configuration. HEX is the preferred portable artifact because it preserves addresses.

6. Remove fingers from all electrodes, then press SW1/XRES if needed. Startup calibrates CapSense. Open the dashboard, select the primary KitProg COM port and Connect at fixed 115200 8N1, no flow control. Wait for actual samples and HEALTH messages.
7. Verify button0/button1 and each slider position affect the expected traces. Record known TAP/HOLD/GRAZE/WIDE interactions, check baseline classifications, then train and install a physical-data model using README. Rebuild and separately reprogram before running `ml.parity --port` for MCU inference comparison.
8. Validate red/green/blue feedback, serial ACKs, disconnect/reconnect behavior, scan timing, watchdog recovery and signal tuning. These are hardware tests, not established by compilation. A resetting or silent kit is a failure requiring diagnosis, not proof of successful classification.

Runtime fatal codes in `firmware/main.c`: 1 allocation; 2 task stack; 3 CapSense Init; 4 interrupt setup; 5 Enable; 6 scan start; 7 scan timeout; 8 process; 9 UART write (reported health fault); 10 heartbeat; 11 UART init; 12 baud; 13 RGB init; 14 queues; 15 task creation; 16 scheduler returned; 17 watchdog init. Debug `fault` through KitProg3 for fatal startup failures. The watchdog can reset the MCU after fatal errors once enabled; its reset timing must be validated on your board.
