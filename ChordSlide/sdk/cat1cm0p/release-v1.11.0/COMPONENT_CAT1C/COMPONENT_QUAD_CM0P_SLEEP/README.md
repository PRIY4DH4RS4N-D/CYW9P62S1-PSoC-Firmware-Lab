# QUAD Cortex M0+ DeepSleep prebuilt image (QUAD_CM0P_SLEEP)

### Overview
DeepSleep prebuilt application image is executed on the Cortex M0+ core of the T2G quad CM7-core MCU (CM0+, CM7_0, CM7_1, CM7_2 and CM7_3).
The image is provided as C array ready to be compiled as part of the Cortex M7_0 application.
The Cortex M0+ application code is placed to internal flash by the Cortex M7_0 linker script.

DeepSleep prebuilt image executes the following steps:
- starts CM7_0 core at CY_CORTEX_M7_0_APPL_ADDR. (check the address in partition.h in pdl repo)
- starts CM7_1 core at CY_CORTEX_M7_1_APPL_ADDR. (check the address in partition.h in pdl repo)
- starts CM7_2 core at CY_CORTEX_M7_2_APPL_ADDR. (check the address in partition.h in pdl repo)
- starts CM7_3 core at CY_CORTEX_M7_3_APPL_ADDR. (check the address in partition.h in pdl repo)
- puts the CM0+ core into Deep Sleep.

Note: After CM7_0 boots up, delays of 600 ms are added before each CM7_1, CM7_2 and CM7_3 boots up. This is to take care of race condition if several cores try to configure the same clock.

### Usage

This image is used by default by all Infineon BSPs that target Quad-Core MCU.

To use this image in the custom BSP, adjust the BSP target makefile to
add the QUAD_CM0P_SLEEP directory to the list of components
discovered by ModusToolbox build system:

```
COMPONENTS+=QUAD_CM0P_SLEEP
```

Make sure there is a single QUAD_CM0P_* component included in the COMPONENTS list.

---
(c) 2020-2026, Infineon Technologies AG, or an affiliate of Infineon Technologies AG.
