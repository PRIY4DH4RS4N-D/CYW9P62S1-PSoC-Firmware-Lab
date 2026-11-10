# Signal feasibility before implementation

The local BSP configures CSD self-capacitance widgets in the order Button0 (one sensor), Button1 (one sensor), LinearSlider0 (five sensors). Firmware records seven raw values and seven adaptive middleware baselines. The difference gives contact amplitude; relative activation over the five slider electrodes gives coarse position and time-dependent travel. The configured generated definitions explicitly disable `CY_CAPSENSE_MULTI_TOUCH_LINEAR_SLIDER_EN`.

Five electrodes are five overlapping electric-field measurements, not five independent finger position estimates. A wide contact, moisture, a palm and two fingers can yield similar activation. The ordinary slider centroid is insufficient to identify multiple contacts. Raw access permits future experiments, but is not evidence of uniqueness. **Pinch and spread are excluded.** No additional gesture classes are added beyond those below and explicit unknown.

|Candidate|Observable evidence|Required physical validation|
|---|---|---|
|Swipe left/right|Ordered amplitude migration between electrodes|Direction orientation, travel minimum, speed and finger placement|
|Tap/double tap|One/two brief slider contacts separated by release|Noise, contact bounce and timing gap distributions|
|Long press|Sustained activation for 700–850 ms|Baseline adaptation during hold, distinction from broad contact|
|Slider?button0/1|Slider activity then a separately wired button channel|Reachability, timing and adjacent-contact crosstalk|
|Unknown|Unsupported or ambiguous activity|Real negative data and calibrated rejection behavior|

The labels are defined operationally by `ml/data.py` guided instructions. They are plausible candidates, not experimentally demonstrated classes. Reverse left/right if physical electrode orientation differs from the kit label; do not change firmware channel ordering. Button-only tap/hold variants are excluded from these labels initially to reduce ambiguity.

The capture is 64 samples ×7 at requested 50 Hz (1.28 s), consisting of up to eight pre-trigger samples and 56 samples starting at activation. A fixed temporal window preserves absolute hold length, gaps and order; no time resampling erases duration. A 15/127 onset and 10/127 release hysteresis reduces noise; a touch still active at sample 64 is marked truncated and rejected, and no new window starts until release. Double-tap's gap should be 180–280 ms. A prediction is emitted only when the fixed window completes, so response delay is intentionally roughly 1.12 s after onset plus scheduling/inference/transport. This is a deliberate accuracy/interaction tradeoff and should be reconsidered after measured data.

Normalization is integer `clip(raw-baseline,0,512)*127//512`, independently per channel. Its count scale is an initial setting requiring real calibration. Baseline values come from the PSoC 6 middleware, not PSoC 4 register APIs. Temporal features (active duration, peak, signed slider travel, mean energy, button0/1 mean) are reported alongside CNN predictions for diagnosis; the CNN consumes all 448 normalized values.

Before an accuracy claim: plot idle and touched distributions; measure crosstalk; check saturation per channel; record gesture speed/hold distributions; collect real unknowns; check session/person holdouts, false acceptance per hour, confusion matrix and macro/per-class scores. Tune thresholds on validation only. Class confidence is not a calibrated probability of correctness. No final recognition claim is possible from the synthetic smoke test.
