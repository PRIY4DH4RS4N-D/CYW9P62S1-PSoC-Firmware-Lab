# Source provenance and dependencies

The board configuration and supported FreeRTOSConfig.h were copied from the existing local CYW9P62S1-43438EVB-01 project without changing their contents. The resulting BSP/configuration hashes are in `board-config-sha256.json`. Firmware application logic is implemented specifically for CapSlide.

Local source copies retain upstream notices and licenses:

| Dependency | Local source |
|---|---|
| Infineon CapSense middleware 2.0 | `firmware/vendor/capsense` |
| Supported FreeRTOS middleware | `firmware/vendor/freertos` |
| PDL 3.24.0 | `sdk/mtb-pdl-cat1/release-v3.24.0` |
| HAL 2.7.4 | `sdk/mtb-hal-cat1/release-v2.7.4` |
| CMSIS 6.1.1 | `sdk/cmsis/release-v6.1.1` |
| ModusToolbox make recipes/core and board startup dependencies | `sdk/` |

Desktop runtime uses Python 3.11, PySide6 Essentials 6.7.3 (QtCore, QtGui, QtWidgets), shiboken6 6.7.3, and pyserial 3.5. Development uses pytest and PyInstaller; exact resolved versions are in `requirements-verified.txt`. Qt/PySide6 and other dependencies retain their upstream licensing terms. Windows fonts are loaded from the operating system for previews and are not redistributed.

No model runtime, dataset, classifier, AI service, or inference library is part of CapSlide. Board-support dependencies may contain general vendor documentation; only the selected FreeRTOS/CapSense/HAL/PDL components are linked.
