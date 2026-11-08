# Prebuilt TouchRGB firmware

Recorded build for **CYW9P62S1-43438EVB-01**, device **CY8C6247BZI-D54**, target `APP_CYW9P62S1-43438EVB-01`, Release / GCC_ARM. It was compiled and software-verified on 7 November 2026 with ModusToolbox 3.9 and Arm GCC 14.2.1.

## Program the board

1. Download `TouchRGB.hex` from this directory using GitHub's **Download raw file** action, or clone the repository.
2. Confirm the board model and connect its KitProg3 USB connector (J6).
3. Open ModusToolbox Programmer, select the intended KitProg3 probe, load `TouchRGB.hex`, then program and verify. Programming replaces the application currently on the board.
4. Reset with the capacitive electrodes untouched. Follow the [controls](../README.md#controls) and [physical acceptance procedure](../docs/TESTING.md#physical-verification-procedure--not-yet-performed).

Use the HEX for normal programming. It includes load addresses and the BSP's CM0+ sleep image. The flat BIN must not be programmed at address zero. ELF and MAP are supplied for debugging and inspection.

## SHA-256 checksums

```text
d923d6f5415353ca80ad85f603eee46d883999d6a2cb1780e2d04e278be65465  TouchRGB.bin
02b837bf586028bf0e70ac357d1fb5855fe63943d0f70e99fffc4d42d5bec9a2  TouchRGB.elf
670196a3227cc8cac8380098d9b3b554669e45001bbb9a0e1a3d589402e60a67  TouchRGB.hex
3fe2cfa9fab5fa964cea35211102274f1ecd7b7dfb22341ea4122d6f6ed4a5a3  TouchRGB.map
```

To check a downloaded HEX in PowerShell:

```powershell
Get-FileHash .\TouchRGB.hex -Algorithm SHA256
```

Compare the result with the HEX entry above. [artifact-sha256.json](verification/artifact-sha256.json) contains the machine-readable values.

## Verification records

- [Release verification](verification/verification.json): source/artifact hashes, HEX checks, flash addresses and physical-test status.
- [Compiler version](verification/compiler-version.txt) and [firmware build log](verification/firmware-build.log).
- [Software tests](verification/software-tests.log) and [unresolved-symbol check](verification/undefined-symbols.txt).
- [Memory sections](verification/memory-sections.txt) and [ELF segment flags](verification/elf-segments.txt).

The build uses **57,040 bytes of flash**. One inherited BSP linker RWX LOAD-segment warning is documented in [TESTING.md](../docs/TESTING.md).

**No board was programmed or physically tested for this recorded build.** Software checks establish compilation, firmware logic and file consistency; they do not verify electrical output or touch sensitivity.

To regenerate these artifacts from source, follow the [flash guide](../FLASH_GUIDE.md) and run `python scripts/verify_release.py` after building. New outputs are written to `build/artifacts/`; this `prebuilt/` directory is the recorded snapshot.
