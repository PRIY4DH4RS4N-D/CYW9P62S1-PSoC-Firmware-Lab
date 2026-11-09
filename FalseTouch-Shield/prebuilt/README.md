# Recorded Builds

## Windows application

Download [FalseTouch-Shield-Windows-x64.zip](FalseTouch-Shield-Windows-x64.zip), extract it, and run `FalseTouch-Shield/FalseTouch-Shield.exe`. Keep the complete extracted folder, including `_internal`. Python is not required for the packaged application. The archive contains the verified offline-launch build, not a simulated or pre-trained physical touch demo.

## Firmware

| Artifact | Use |
|---|---|
| [FalseTouch-Shield.hex](firmware/FalseTouch-Shield.hex) | Address-preserving programming image |
| [FalseTouch-Shield.elf](firmware/FalseTouch-Shield.elf) | Linked image and debug symbols |
| [FalseTouch-Shield.bin](firmware/FalseTouch-Shield.bin) | Raw image; requires correct addresses if used |
| [FalseTouch-Shield.map](firmware/FalseTouch-Shield.map) | Linker sections and memory layout |

Target: `APP_CYW9P62S1-43438EVB-01`, device `CY8C6247BZI-D54`. Follow [FLASH_GUIDE.md](../FLASH_GUIDE.md) if you choose to program the board. No board was flashed for this project.

> **Live dataset collection and production ML deployment are pending.** This firmware's ML model deliberately abstains with UNKNOWN and zero confidence. Baseline classification remains separate. Synthetic smoke metrics do not establish real sensor accuracy.

See [SHA256SUMS.txt](SHA256SUMS.txt), [verification evidence](verification/) and the [verification report](../VERIFICATION_REPORT.md). Rebuilds use `scripts/build_firmware.ps1` and `scripts/package.ps1`; current local outputs are generated under ignored `build/` directories.

## Git LFS

This large Windows ZIP is tracked with Git LFS. Use GitHub's **Download raw file** action, or run `git lfs install` and `git lfs pull` after cloning. Verify the downloaded ZIP using [SHA256SUMS.txt](SHA256SUMS.txt). Firmware and source files use normal Git storage.
