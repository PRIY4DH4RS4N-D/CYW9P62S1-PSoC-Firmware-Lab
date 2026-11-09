# Source notices

Original FalseTouch-Shield application sources and documentation are provided under the MIT license in LICENSE. Third-party BSP, generated configuration, middleware, kernel and reference example retain their own original copyright notices and license files. The root license does not relicense those files.

- `firmware/bsps`: copied from the existing working local exact-board BSP, with Infineon license notices retained.
- `firmware/vendor/capsense`: Infineon/Cypress CapSense 2.0.0; see its LICENSE.
- `firmware/vendor/freertos`: Infineon FreeRTOS distribution 10.4.302; see LICENSE.md and EULA.
- `firmware/FreeRTOSConfig.h`: adapted from Infineon's official buttons-and-slider FreeRTOS example; original notices retained.
- Reference example: https://github.com/Infineon/mtb-example-psoc6-capsense-buttons-slider-freertos (the development reference clone is not included in this publication).
- `sdk/`: ModusToolbox libraries corresponding to pinned `.mtb` manifests; each retains its upstream license.

Python dependencies retain their upstream licenses, including Qt/PySide6 licensing. Review those licenses when distributing packaged executables.
