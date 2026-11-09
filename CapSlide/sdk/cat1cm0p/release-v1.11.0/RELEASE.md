### CAT1 Cortex M0+ prebuilt images
Prebuilt application images are executed on the Cortex M0+ core of the CAT1 dual-core MCU. The images are provided as C arrays ready to be compiled as part of the Cortex M4/M7 application. The Cortex M0+ application code is placed to internal flash by the Cortex M4/M7 linker script.

### What's Included?

#### CAT1A

* [COMPONENT_CM0P_SLEEP](./COMPONENT_CAT1A/COMPONENT_CM0P_SLEEP/README.md)

    This image starts CM4 core at CY_CORTEX_M4_APPL_ADDR
    and puts CM0+ core into a deep sleep mode.  (Check your device's
    linker file (psoc6) or partition file (Traveo) for the
    location of CY_CORTEX_M4_APPL_ADDR.)

* [COMPONENT_CM0P_CRYPTO](./COMPONENT_CAT1A/COMPONENT_CM0P_CRYPTO/README.md)

    This image starts crypto server on CM0+ core,
    starts CM4 core at CY_CORTEX_M4_APPL_ADDR=0x1000A000
    and puts CM0+ core into a deep sleep mode.

* [COMPONENT_CM0P_BLESS](./COMPONENT_CAT1A/COMPONENT_CM0P_BLESS/README.md)

    This image starts BLE controller on CM0+ core,
    starts CM4 core at CY_CORTEX_M4_APPL_ADDR=0x10020000
    and puts CM0+ core into a deep sleep mode.

* [COMPONENT_CM0P_SECURE](./COMPONENT_CAT1A/COMPONENT_CM0P_SECURE/README.md)

    This image starts CM4 core at address corresponding
    to Secure Boot policy, sets required security settings,
    initializes and executes code of Protected Register Access
    driver, puts CM0+ core into a deep sleep mode.

#### CAT1C

* [COMPONENT_QUAD_CM0P_SLEEP](./COMPONENT_CAT1C/COMPONENT_QUAD_CM0P_SLEEP/README.md)

    This image is meant for quad CM7 core (CM7_0/1/2/3) CAT1C device applications. This image starts four CM7_0, CM7_1, CM7_2 and CM7_3 cores at CY_CORTEX_M7_0_APPL_ADDR, CY_CORTEX_M7_1_APPL_ADDR, CY_CORTEX_M7_2_APPL_ADDR and CY_CORTEX_M7_3_APPL_ADDR respectively and puts CM0+ core into a deep sleep mode.

* [COMPONENT_DUAL_CM0P_SLEEP](./COMPONENT_CAT1C/COMPONENT_DUAL_CM0P_SLEEP/README.md)

    This image is meant for dual CM7 core (CM7_0/1) CAT1C device applications. This image starts both CM7_0 and CM7_1 cores at CY_CORTEX_M7_0_APPL_ADDR and CY_CORTEX_M7_1_APPL_ADDR respectively and puts CM0+ core into a deep sleep mode.

* [COMPONENT_CM0P_SLEEP](./COMPONENT_CAT1C/COMPONENT_CM0P_SLEEP/README.md)

    This image is meant for single CM7 core (CM7_0) device applications. This image starts CM7_0 core at CY_CORTEX_M7_0_APPL_ADDR and puts CM0+ core into a deep sleep mode.

* [COMPONENT_XMC7xDUAL_CM0P_SLEEP](./COMPONENT_CAT1C/COMPONENT_XMC7xDUAL_CM0P_SLEEP/README.md)

    This image is meant for dual CM7 core (CM7_0/1) XMC7xxx device. This image starts both CM7_0 and CM7_1 core at CY_CORTEX_M7_0_APPL_ADDR and CY_CORTEX_M7_1_APPL_ADDR respectively and puts CM0+ core into a deep sleep mode.  Not recommended for new projects; use the COMPONENT_DUAL_CM0P_SLEEP for new projects.

* [COMPONENT_XMC7x_CM0P_SLEEP](./COMPONENT_CAT1C/COMPONENT_XMC7x_CM0P_SLEEP/README.md)

    This image is meant for single CM7 core (CM7_0) XMC7xxx device. This image starts CM7_0 core at CY_CORTEX_M7_0_APPL_ADDR and puts CM0+ core into a deep sleep mode.  Not recommended for new projects; use the COMPONENT_CM0P_SLEEP for new projects.

### What Changed?
#### v1.11.0
* Adds CAT1C support for TRAVEO&trade; T2G CYT6BJ devices.
#### v1.10.0
* Adds CAT1C support for TRAVEO&trade; T2G CYT3DL devices.
#### v1.9.0
* BLESS FW update to v5.0.15.699
  * Implementation of new Vendor command - Set PILO Trim Interval (supported only with legacy cypress host)
  * Fixed issue related to Disconnection due to instant passed error when channel map update instant is just 2 events away
#### v1.8.0
* BLESS FW update to v5.0.14.511
  * Fixed issues related to Resolvable Private address resolution
  * Fixed issues related to rejecting control PDUs when received unexpected PDUs based on role of the IUT
  * Changes in HCI layer to return the proper error code when unsupported command is issued
#### v1.7.0
* BLESS FW update to v5.0.13.492
  * Implementation ONE-SHOT advertisement
  * Updated logic to calculate number of events to skip when slave latency is present.
  * Send Number of Completed Packets Event with correct Num_Completed_Packets parameter when ACL packet is dropped by controller.
  * Optimization in controller to start the RPA timer only when Scanning/Advertisement/Connection Initiator procedure is in progress and higher layer uses RPA for own address.
#### v1.6.0
* Adds CAT1C support for TRAVEO&trade; T2G CYT4DN devices.
* Renames the CAT1C component names to be more generic.  Previous XMC7x and XMC7xDUAL images are still available, but not recommended for new projects.
#### v1.5.0
* Adds new support for TRAVEO&trade; T2G CYT2B6 and CYT2B9 devices, and updates CM0P allocations for CYT2B7 device.
#### v1.4.0
* Built prebuilts with mtb-pdl-cat1 3.9.0
#### v1.3.0
* Production support added for TRAVEO&trade; T2G CYT2B6/CYT2B7/CYT2B9 devices.
#### v1.2.0
* BLESS FW update to v5.0.12.462
  * Changes for Bluetooth 5.4 Re-Certification
#### v1.1.0
* Driver maintenance and code efficiency enhancement.
* BLESS FW update to v5.0.11.449
  * Fix for LE-ACL data transfer issue observed during testing with PTS
  * Fix for connection establishment issue when using Resolvable Private Address
  * Fix related Cy_BLE_SetSlaveLatencyMode API
#### v1.0.0
* Initial release

### Known Issues in CAT1A M0+ prebuilt images:
  1. With ble-example-hello-sensor app running in CY8CKIT-062-BLE, when Remote Device A is bonded, Remote Device B would have scanning/connecting issues.
       Recovery is to delete the bonding of Remote Device A.

### Product/Asset Specific Instructions
To pick which image is used in an application update the COMPONENTS variable in the Board Support Package (BSP)'s makefile. Depending on which image is selected, an update to the BSPs linker script may also be required to allocate the proper space for the CM0+ image and that the CM4 has the starting address listed above.

### Supported Software and Tools
This version of the (CAT1 Cortex M0+ prebuilt images) was validated for compatibility with the following Software and Tools:

| Software and Tools                        | Version |
| :---                                      | :----:  |
| GCC Compiler                              | 11.3.1  |
| IAR Compiler                              | 9.3     |
| ARM Compiler 6                            | 6.16    |

### More information
Use the following links for more information, as needed:
* [Infineon Technologies AG](https://www.infineon.com)
* [ModusToolbox&trade; Software](https://www.infineon.com/design-resources/development-tools/sdk/modustoolbox-software)

---
© Infineon Technologies AG or an affiliate of Infineon Technologies AG, 2023-2026.
