# V147 Phase C — Pre-Execution Evidence Clarification

Status: **FROZEN BEFORE PHASE-C IMPLEMENTATION OR REAL-AUDIO ACCESS**

Branch: `v143-contextual-prune-lobo`

This clarification corrects a transcription error in `docs/v147-phase-c-real-audio-artifact-preregistration.md` before any Phase-C implementation or real-audio execution occurred.

## What was wrong

The Phase-C preregistration restated the V147 candidate score as:

`fundamental_delta_db + 0.5 * max(0, octave_delta_db)`

That restatement conflicts with the already-frozen and already-proven V147 implementation `modal/v147_pitch_hypothesis.py`, Git blob:

`49bce8b968406bb0d61ab61394954ef8a8303eb7`

The frozen implementation defines `OCTAVE_WEIGHT = 0.25` and therefore scores exactly:

`fundamental_delta_db + 0.25 * max(0, octave_delta_db)`

The Phase-C prose also described the band-delta arithmetic in a way that could be interpreted as a new reimplementation. Phase C must not create a second interpretation of the already-frozen V147 CQT evidence contract.

## Authoritative rule

For all Phase-C evidence extraction and selection, the frozen V147 implementation blob above is authoritative and MUST be called directly:

- `candidate_midis`
- `_band_delta_db` through the public extractor
- `extract_candidate_evidence_from_cqt`
- `choose_pitch_hypothesis`
- or `choose_pitch_hypothesis_from_cqt`

The exact frozen constants in that blob are authoritative:

- MIDI range `[40, 88]`
- `OCTAVE_WEIGHT = 0.25`
- `MIN_ALTERNATE_FUNDAMENTAL_DB = 3.0`
- `MIN_SCORE_MARGIN_DB = 3.0`
- `MIN_FUNDAMENTAL_MARGIN_DB = 2.0`
- `SCORE_ROUND_DIGITS = 6`
- `CANDIDATE_BAND_SEMITONES = 0.30`
- `BASELINE_WINDOW_SEMITONES = 2.0`
- `BASELINE_EXCLUSION_SEMITONES = 0.75`
- `DB_FLOOR = 1e-8`

Its already-frozen behavior is also authoritative:

- candidate-band magnitude is summed per frame;
- baseline magnitude is the median baseline-bin magnitude multiplied by candidate-bin count;
- band and baseline are separately floored with `DB_FLOOR` before the dB subtraction;
- per-event evidence is the median of per-frame deltas;
- octave evidence is used only when the full ±2-semitone octave window is represented, otherwise octave evidence is `0.0`;
- missing/malformed/non-finite/tied/weak/ambiguous evidence fails closed to the original MIDI.

## Scope of this clarification

This is an execution-contract correction only. It does **not** authorize or change:

- any V147 code;
- any threshold;
- candidate family;
- CQT front-end parameters newly frozen for Phase C;
- event-time mapping;
- frame-selection window;
- fixed-timing candidate-construction rules;
- accepted family #10 identity;
- source-audio identity;
- reference/gold access;
- Modal/GPU execution;
- Production integration.

No Phase-C candidate, real-audio evidence, score, or musical result existed when this clarification was frozen. Therefore this correction is pre-result and cannot be informed by Phase-C musical outcomes.

## Execution requirement

Any Phase-C implementation/test/workflow MUST verify the V147 blob is exactly `49bce8b968406bb0d61ab61394954ef8a8303eb7` and MUST use the frozen V147 extractor/decision functions directly rather than reproducing their evidence math.

If that blob differs, Phase C is STOP.
