# Hardware and API verification

Research performed 2026-11-07, before writing application firmware. Sources are official Infineon material and locally installed Infineon code; no PSoC 4 API assumptions were used.

Official references:

- [CYW9P62S1-43438EVB-01 kit guide, Doc. 002-28692](https://www.infineon.com/assets/row/public/documents/30/44/infineon-cyw9p62s1-43438evb-01-psoc-62s1-wi-fi-bt-pioneer-kit-guide-usermanual-en.pdf), pin table and sections 2.2.2, 3.2.7, 3.2.8.
- [Infineon FreeRTOS CapSense buttons and slider example](https://github.com/Infineon/mtb-example-psoc6-capsense-buttons-slider-freertos), confirmed support for this board and PSoC 6 interrupt/init/scan/process flow. A read-only reference clone is in `build/reference` with its original license. Application code is a separate implementation.
- [Infineon CapSense middleware release 2.0.0](https://github.com/Infineon/capsense/tree/release-v2.0.0), matched to the locally generated configuration's required major version 2. Choosing the current example's v4 middleware blindly would mismatch this BSP configuration.
- [Infineon FreeRTOS release 10.4.302](https://github.com/Infineon/freertos/tree/release-v10.4.302), used for the kernel and Cortex-M4 GCC port.

Local inspection: `C:/Psoc_Projects/psoc6_led_blink`, `Inference_Matrix`, `mtb_shared`, and `C:/Infineon/Tools`. Reused the working standalone project's exact-board BSP and pinned library manifests. Existing projects were not edited. `firmware/bsps/TARGET_APP_CYW9P62S1-43438EVB-01/config/GeneratedSource` retains the complete generated clocks, pins, peripherals and CapSense data, plus editable `.modus` and `.cycapsense` designs. The existing generated CapSense design uses **CSX buttons and a CSD slider**, producing 1+1+5 sensor contexts. It is not replaced with an invented seven-button configuration.

| Function | Verified assignment |
|---|---|
| MCU build device | CY8C6247BZI-D54, Cortex-M4 application + BSP CM0+ sleep image |
| Button 0 | P8.1 TX; common RX P1.0 |
| Button 1 | P8.2 TX; common RX P1.0 |
| Slider segments 0–4 | P8.3, P8.4, P8.5, P8.6, P8.7 |
| CMOD | P7.7 |
| CINTA / CINTB | P7.1 / P7.2 |
| RGB red / green / blue | P1.1 / P0.5 / P7.3, active low |
| KitProg3 primary UART | MCU RX P5.0, TX P5.1; BSP DEBUG_UART symbols |
| KitProg3 USB connector | J6; carries programming/debug and primary UART bridge |
| Target USB connector | J7; not used by this application's UART |
| User LEDs additionally available | orange LED8 P1.5; red LED9 per kit guide; neither needed by this application |

The board has no usable driven CapSense shield feature per the kit guide. The project name means a software false-touch filter. No external sensor, extra electrode, external UART adapter or shield driver is required. The kit configuration uses its normal 3.3 V operation.

Verified headers/implementations used: `cybsp_init`, `Cy_CapSense_Init`, `Cy_CapSense_Enable`, `Cy_CapSense_ScanAllWidgets`, `Cy_CapSense_IsBusy`, `Cy_CapSense_ProcessAllWidgets`, `Cy_CapSense_CalibrateAllWidgets`, `Cy_CapSense_InterruptHandler`; PDL `Cy_SysInt_Init`; HAL UART/GPIO/WDT APIs from installed `mtb-hal-cat1/release-v2.7.4`. In v2.0 the success constant is `CYRET_SUCCESS`, matching the official example. Sensor differences are read from verified `ptrWdConfig[w].ptrSnsContext[j].diff` fields. GPIO pin and active-low state macros come directly from the BSP. The middleware's Enable path performs startup calibration/baseline initialization.

Toolchain: ModusToolbox tools 3.9, core-make 3.10.0, recipe-make-cat1a 2.8.0, PDL 3.24.0, HAL 2.7.4, GCC ARM 14.2.1. See `sdk/` and `firmware/libs/*.mtb` for exact checked-out source commits.

All assignments are verified against source/documentation, not probed on the physical kit. Physical revision, solder links, sensor tuning, actual signal quality, serial enumeration, LED polarity at runtime and watchdog reset remain NOT VERIFIED.
