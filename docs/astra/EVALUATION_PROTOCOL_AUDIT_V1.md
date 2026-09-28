# Astra evaluation protocol audit V1

Date: 2026-09-27  
Scope: offline code/committed-metadata/fabricated examples only. No model rerun, no real-media access, no optimizer work, no threshold search, no P3.

## Inspected identities

- `astra_backend/evaluation/prepared_event_adapter_v1.py` — blob `c07a8e94ebf511041b0b8b3afe988ffa4c3f3ce2`
- `astra_backend/evaluation/pretrained_note_front_end_v1.py` — blob `235604085e0098043271ba6525ef9fd9211fbc58`
- `astra_backend/evaluation/pretrained_note_front_end_real_v1.py` — blob `ded0db28e173c08cd0496695f221426388c5d396`
- `astra_backend/evaluation/mr_mt3_front_end_v1.py` — blob `3fc1e1f2c379d75fc6e697d7578fa3b0b2b12380`
- `astra_backend/evaluation/test_pretrained_note_front_end_v1.py` — blob `77dea35b53382e8ea02eb2a571126a8622407ea6`
- `astra_backend/evaluation/test_mr_mt3_front_end_v1.py` — blob `f855accf0db4ff98b24a636f01a5acc6ade547d6`
- Basic Pitch frozen result — blob `fc3aa1ac611cdd8b551509e064a362c9cb0d3c4e`
- MR-MT3 frozen result — blob `f70645e44011df054f094672a6f40ece8bbde9ce`
- P1/P2 combined diagnostic result — blob `73a6bf9d61dfd84e9a1e584786e99002a71c4156`

Historical receipts are not edited by this audit.

## Findings

### 1. Boundary eligibility is asymmetric in the frozen Stage-A path

Confirmed.

Both frozen prediction adapters clip any event intersecting the crop and replace a pre-crop onset with local time zero:

- Basic Pitch: `basic_pitch_to_crop_events()`
- MR-MT3: `project_midi_to_guitar_events()`

The prepared reference path does something different: `prepared_event_adapter_v1.py` retains carry-in/carry-out occupancy but excludes any event crossing either crop boundary from `scorableEvents`. Therefore a prediction and its corresponding source event can have different score eligibility.

Consequences:

- a carry-in prediction can become an artificial local time-zero onset while its reference is ineligible;
- a carry-out prediction can remain an onset prediction while its reference is excluded wholesale;
- historical false positives cannot be interpreted as purely model-generated extras without boundary accounting.

This does **not** prove how many of Basic Pitch's frozen 52 false positives are boundary artifacts. No real predictions were rescored here.

The P1 decoder work already demonstrated the same general class of accounting problem in a different path: 23 raw decoded events became 16 boundary-corrected predictions. That evidence is not reused to numerically rewrite the Basic Pitch receipt.

### 2. Frozen greedy matching is not maximum-cardinality

Confirmed with the preregistered fabricated counterexample.

References: same pitch at 0.00 and 0.05 s. Predictions: same pitch at 0.04 and 0.09 s. Onset tolerance: 0.05 s.

The frozen nearest-error greedy ordering can consume prediction 0 with reference 1 and leave only one match, even though the valid assignment prediction 0 -> reference 0 and prediction 1 -> reference 1 gives two matches.

A prospective scorer therefore must maximize one-to-one match cardinality first and only then minimize timing error.

### 3. Same-pitch ambiguity needs separate onset and offset policies

Confirmed from frozen code.

The old collapse key is pitch + onset + offset. For onset-only scoring, two same-pitch notes beginning simultaneously but ending at different times are acoustically one observable pitch onset; leaving both as separate onset references can create an impossible onset recall requirement.

Prospective policy:

- onset score: collapse exact simultaneous same-pitch onsets regardless of duration;
- onset+offset score: collapse only exact same-pitch/onset/offset duplicates;
- preserve the original string-level multiplicity separately in metadata; pitch-only collapse must never be mistaken for string/fret correctness.

### 4. Identity validation is distributed, not one frozen-manifest assertion

Confirmed.

`validate_meta()` checks capture key, view, performer, frame count, and unresolved labels. The real Basic Pitch runner separately checks several source hashes. There is no single prospective assertion binding every capture to one manifest entry containing crop start, crop length/hop, source media hashes, feature hash, source-event hash, and target hash.

The new `validate_manifest_binding()` helper intentionally requires one manifest binding for those fields before a future V2 runner can score.

### 5. Malformed prediction handling is too permissive for a prospective protocol

Confirmed.

The frozen Basic Pitch converter silently skips nonfinite or nonpositive-duration rows after type coercion. A prospective evaluator should fail closed on malformed/nonfinite events so label corruption or adapter bugs cannot disappear from denominators.

### 6. MR-MT3 failure remains a program-semantic failure under its frozen contract; cause is unresolved

The frozen projector stores the zero-based MIDI program active at note-on, rejects channel 9 percussion, accepts programs 24-31 inclusive, then applies the guitar pitch range. Existing synthetic fixtures cover program bounds, non-guitar rejection, percussion rejection, pitch bounds, crop clipping, and deterministic multitrack projection.

The frozen result remains: 1,777 raw notes, 1,772 rejected for non-guitar program, 5 percussion, zero accepted. This audit found no code-only basis to relabel the emitted programs after seeing outcomes, and no evidence proving whether the observed program distribution is caused by model instrument classification, upstream serialization conventions, or another semantic mismatch. The gate remains failed. No third front end and no post-hoc remap are justified.

Because the projector admitted zero events, the matching fix alone cannot turn the frozen MR-MT3 result into a pass.

## Prospective isolated protocol

New file: `astra_backend/evaluation/evaluation_protocol_v2.py`.

It is deliberately **not** imported by frozen V1 workflows. It adds:

- original source onset/offset retention;
- explicit `carry_in` / `carry_out`;
- separate `onset_eligible` / `offset_eligible`;
- reason-counted boundary exclusions for predictions and references;
- deterministic maximum-cardinality one-to-one matching with minimum timing error as the secondary objective;
- separate onset and onset+offset ambiguity collapse;
- strict finite/integer MIDI validation;
- one frozen-manifest identity assertion helper.

A future real V2 runner must also provide boundary-aware reference events, not old `scorableEvents` alone. That reference representation is intentionally not synthesized from missing committed data in this audit. Runners must not silently mix V2 predictions with V1 reference eligibility.

## Focused tests actually run

Local isolated command equivalent:

`python -m unittest -v test_evaluation_protocol_v2.py`

Result: **7 tests passed, 0 failed**.

Covered:

1. symmetric carry-in/carry-out onset/offset eligibility;
2. the 1-TP greedy counterexample becomes 2 TP;
3. permutation invariance of counts;
4. exact 50 ms tolerance boundary is inclusive;
5. onset and offset ambiguity policies differ as specified;
6. nonfinite/fractional MIDI inputs fail closed;
7. target-hash or crop-start manifest drift is rejected.

These tests use fabricated events only. Existing MR-MT3 fixture tests were inspected but were not rerun in this audit.

## What this audit does not establish

- It does not recompute Basic Pitch's 27/52/4 result under V2.
- It does not establish that Basic Pitch would pass after corrected accounting.
- It does not change the ordering or status of any historical model result.
- It does not prove the cause of MR-MT3's program semantics.
- It does not justify threshold tuning.
- It does not authorize new real-media access.
- It does not authorize training or P3.

The correct next use of V2 is prospective only, under a separately frozen runner/manifest if real transfer evaluation is later authorized.
