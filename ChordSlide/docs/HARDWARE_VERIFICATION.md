# Hardware and SDK evidence

Inspected before application implementation, 7 November 2026. Board was not accessed or programmed.

|Item|Local evidence and result|
|---|---|
|Target|`firmware/bsps/TARGET_APP_CYW9P62S1-43438EVB-01/bsp.mk`: CY8C6247BZI-D54, CM0+ / CM4, 1024 KiB flash, 288 KiB SRAM|
|Execution|CM4 application; BSP/default CM0+ startup image and official GCC linker script selected by recipe|
|Generated sensing|`config/design.cycapsense`, `config/GeneratedSource/cycfg_capsense.c`, `.h`, `_defines.h`: two buttons + five segment CSD linear slider, multi-touch disabled|
|Raw access|`cy_capsense_context.ptrWdConfig[w].ptrSnsContext[j].raw`, `.bsln`, `.diff` are actual installed PSoC 6 sensor-context members|
|Scan|Installed `vendor/capsense`: Cy_CapSense_Init, Enable, ScanAllWidgets, IsBusy, ProcessAllWidgets; CSD ISR invokes Cy_CapSense_InterruptHandler|
|RGB|Generated cycfg_pins.h: red P1_1, green P0_5, blue P7_3. HAL gpio init/write; CYBSP_LED_STATE_ON=0|
|UART|Generated cycfg_pins.h: RX P5_0, TX P5_1. cyhal_uart at 115200, 8N1, no RTS/CTS; KitProg USB-UART bridge|
|RTOS|Local FreeRTOS 10.4.3 LTS Patch 2 asset, CM4 port, heap_4; COMPONENTS=FREERTOS|
|SDK|PDL 3.24.0, HAL 2.7.4, CMSIS 6.1.1, recipe-make-cat1a 2.8.0, core-make 3.10.0 copied locally into sdk/|
|Tools|C:/Infineon/Tools/ModusToolbox/tools_3.9; C:/Infineon/Tools/mtb-gcc-arm-eabi/14.2.1/gcc|
|ML|Official Infineon ml-tflite-micro HEAD `9501efde9411c482c9149e82cb361953271259e8`, release notes v3.5.0, includes CM4 HARDFP GCC precompiled runtime and headers|
|CMSIS-NN|`arm-none-eabi-nm` of official runtime archive contains arm_convolve_s8 and CMSIS-NN helpers; no extra incompatible CMSIS-NN archive added|

The pre-existing local BSP/SDK/CapSense/RTOS installation was inspected and copied as a baseline, not fetched from an assumed PSoC 4 example. The board-specific generated files retain Infineon copyright and license notices. General CRC framing was adapted from the local FalseTouch-Shield project's independently inspected wire implementation; ChordSlide application, CNN, windowing, dashboard and training are separate.

Official references checked:

- [Infineon board kit guide](https://www.infineon.com/assets/row/public/documents/30/44/infineon-cyw9p62s1-43438evb-01-psoc-62s1-wi-fi-bt-pioneer-kit-guide-usermanual-en.pdf): board sensing circuit, RGB LEDs and KitProg serial.
- [Official buttons-slider example](https://github.com/Infineon/mtb-example-psoc6-capsense-buttons-slider): PSoC 6 two buttons and five-segment slider architecture.
- [Official custom scan example](https://github.com/Infineon/mtb-example-psoc6-capsense-custom-scan): scan architecture.
- [Official ML profiler](https://github.com/Infineon/mtb-example-ml-profiler): PSoC 6 MCU ML profiling and model validation.
- [Official runtime](https://github.com/Infineon/ml-tflite-micro): copied CM4 GCC runtime, documented ML_TFLM/ML_INT8x8 and TF_LITE_STATIC_MEMORY flags.
- [Official ML middleware](https://github.com/Infineon/ml-middleware): available wrapper; ChordSlide directly uses the supplied MicroInterpreter interface.

Runtime is kept in vendor/tflm with its LICENSE and EULA. Compiler/link results, rather than repository availability alone, determine compatibility. No claim is made that AllocateTensors or Invoke ran on the MCU until hardware verification is performed.
