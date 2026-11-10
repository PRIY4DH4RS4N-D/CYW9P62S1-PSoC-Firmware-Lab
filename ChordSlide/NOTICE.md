# Source and dependency notices

ChordSlide application source is licensed under the accompanying MIT LICENSE.

The local BSP, generated configuration, CapSense middleware, FreeRTOS and SDK snapshots retain their original copyright headers and license files. They were copied from the inspected local ModusToolbox installation and local board-support project. Dependency revisions and sources are recorded in docs/dependency-provenance.json and firmware/libs/*.mtb. The generic CRC framing parser was adapted from the local FalseTouch-Shield implementation under its MIT license; it has a larger payload limit and a separate ChordSlide specification and cross-language tests.

The Infineon TensorFlow Lite Micro precompiled runtime is from the official Infineon/ml-tflite-micro repository at commit 9501efde9411c482c9149e82cb361953271259e8. Its original LICENSE, EULA, README, release notes and component headers are in firmware/vendor/tflm. TensorFlow/FlatBuffers/CMSIS-NN notices remain in the supplied asset. No claim of authorship is made over vendor libraries or generated BSP files.

Desktop dependencies include PySide6/Qt (LGPL/commercial licensing as supplied), pyqtgraph (MIT), NumPy and pandas (BSD), PyArrow (Apache 2.0), and PyInstaller (GPL with its bootloader exception). Training uses TensorFlow (Apache 2.0), scikit-learn (BSD) and matplotlib (PSF-compatible license). Their installed distributions retain their notices. build/python-freeze.txt records the actual development environment; requirements files specify the intended independently installed project dependencies.

The provided model and sample windows are trained/generated entirely from artificial waveforms and are marked SYNTHETIC SMOKE TEST ONLY. They are not recordings from a physical board.
