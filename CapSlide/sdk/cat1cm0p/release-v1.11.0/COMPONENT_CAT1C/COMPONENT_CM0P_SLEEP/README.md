# CAT1C Cortex M0+ DeepSleep prebuilt image (CM0P_SLEEP)

### Overview
This DeepSleep prebuilt application image is executed on the Cortex M0+ core of a dual-core MCU.
The image is provided as C array ready to be compiled as part of the Cortex M7_0 application.
The Cortex M0+ application code is placed to internal flash by the Cortex M7_0 linker script.

The DeepSleep prebuilt image executes the following steps:
- Starts CM7_0 core at CY_CORTEX_M7_0_APPL_ADDR (this address is set in system_cat1c.h in the pdl repo)
- Puts the CM0+ core into Deep Sleep.

### Usage

This image is used by Infineon BSPs that target any CAT1C Dual-Core MCUs.

To use this image in the custom BSP, adjust the BSP target makefile to
add the COMPONENT_CM0P_SLEEP directory to the list of components
discovered by ModusToolbox build system:

```
COMPONENTS+=CM0P_SLEEP
```

Make sure there is a single CM0P_SLEEP* component included in the COMPONENTS list.

---
(c) (2020-2026), Infineon Technologies AG, or an affiliate of Infineon Technologies AG.
