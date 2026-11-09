# Repository publication checks

Publication date: 2026-11-09.

- All 16 host tests passed from the copied repository project; see [publication-host-tests.log](publication-host-tests.log).
- Local SDK dependencies are included under `FalseTouch-Shield/sdk/`. The firmware Makefile resolves this directory directly.
- The Windows ZIP passed full ZIP CRC/integrity checks and contains the EXE plus its complete runtime folder. Its size is below GitHub's 100 MiB per-file limit.
- Recorded firmware and Windows ZIP checksums are listed in [../SHA256SUMS.txt](../SHA256SUMS.txt).
- Production ML remains untrained. Live labelled touch recordings, real accuracy evaluation and ML deployment are pending.
- The source and root README both state the pending live dataset prominently.
- No board was flashed and no new physical validation is claimed.

The independent repository clean firmware build passed using the included SDK, with no unresolved symbols. Its HEX is byte-identical to the recorded firmware (SHA256 `d3591b6e7ad4ae817b61b45fa8e92a8a4a93c65b538a98deaa9307db9885db7f`). See [publication-firmware-build.log](publication-firmware-build.log), [publication-memory-sections.txt](publication-memory-sections.txt) and [publication-checks.json](publication-checks.json). The only linker warning is the documented BSP RWX LOAD segment warning.

The Windows ZIP is tracked using Git LFS after the ordinary large Git upload timed out. Source, SDK and firmware remain normal Git objects; Windows download instructions cover LFS retrieval.
