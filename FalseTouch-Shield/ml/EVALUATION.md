# Model evaluation status

**Recorded-data accuracy: NOT AVAILABLE.** No labelled physical dataset has been supplied or recorded. A real trained touch classifier and physical confusion matrix cannot honestly be produced from the available evidence.

The firmware's production `model.h` returns UNKNOWN with zero confidence and `FT_MODEL_TRAINED=0`. It does not disguise the baseline as ML. `train.py` trains an actual weighted decision tree from labelled physical-event JSONL, evaluates a session-grouped held-out split, exports the learned branches to C and writes a confusion matrix. `--install` explicitly replaces the production model header.

The `synthetic_smoke/` directory contains a genuinely fitted tree using **explicitly artificial pipeline-test vectors only**. Its evaluation JSON and confusion matrix PNG are labelled SYNTHETIC. They test software plumbing, not touch recognition. `native_parity.json` records host-compiled C equivalence on 1129 vectors, including split boundaries. It does not establish Cortex-M4 execution or physical performance.

MCU parity tooling is implemented via protocol command 0x13 and `python -m ml.parity ARTIFACT_DIRECTORY --port COMx`. It remains NOT VERIFIED. Do not compare a recorded model's expectations against the shipped untrained firmware.
