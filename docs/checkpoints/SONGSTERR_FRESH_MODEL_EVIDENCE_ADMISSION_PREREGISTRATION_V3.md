# Songsterr Fresh — Model-Evidence Admission Preregistration V3

Status: **PREREGISTERED EXTERNAL-VALIDATION SUCCESSOR / NOT ADMISSION AUTHORITY**

Recorded: 2026-09-11 America/Toronto

## Purpose

V1 and V2 are closed as admission authority. V2 completed its full preregistered lifecycle and was rejected because controlled fixtures plus Policy C-S reproducibility plus one protected-song research run did not establish independently measured real-world correctness.

V3 does **not** patch or tune the frozen V2 per-event corroborator. Instead, V3 preregisters an independent annotated-corpus validation protocol for that frozen rule. No V2 score, threshold, competitor set, window, channel logic, Basic Pitch threshold, historical protected-song measurement, or V1/V2 stress case may be changed from external-corpus results under this version.

No external-corpus model result had been viewed when this preregistration was written. Dataset documentation, file identities, license/publication metadata, and documented dataset errors were reviewed only to define the protocol before evaluation.

## Frozen scorer under evaluation

The event-level rule under evaluation is unchanged frozen V2:

- implementation: `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`
- contract: `songsterr-fresh-independent-pitch-corroboration-research-v2`
- sample rate: exactly `44100 Hz`
- fixed post-onset window: `16384` samples
- playable MIDI: `40..88`
- competitors: `{-12,-7,-2,-1,+1,+2,+7,+12}` in range
- demeaned RMS `<1e-4` => insufficient
- strict `>` unique-best; exact equality fails closed
- Channel A: coherent four-harmonic semitone-cell spectral score
- Channel B: YIN/CMND half-period-disambiguated score
- positive label only when both channels select the existing MIDI as strict unique best
- no duration, model-note end, next onset, same-pitch reattack, reference tab, professional scorer, GOAT/V143 logic, confidence fitting, or event rewriting.

V3 must import/reuse this frozen implementation rather than duplicating or silently modifying its scoring logic.

## External validation corpus — frozen before results

Dataset: **GuitarSet v1.1.0**

Canonical public record:
- DOI: `10.5281/zenodo.3371780`
- published: 2019-08-20
- 360 excerpts, approximately 30 seconds each
- 6 players
- modes: comping and soloing
- styles: Jazz, Bossa Nova, Rock, Singer-Songwriter, Funk
- time-aligned per-string MIDI-note annotations are available.

Only these V3 assets are authorized:

1. `audio_mono-mic.zip`
   - Zenodo v1.1.0 file
   - MD5: `275966d6610ac34999b58426beb119c3`
   - microphone recording; used as the model/evaluator audio.
2. `annotation.zip`
   - Zenodo v1.1.0 file
   - MD5: `b39b78e63d3446f2e54ddb7a54df9b10`
   - JAMS annotations; used only as locked evaluation truth after model outputs/classifications are complete.

`audio_mono-pickup_mix`, original/debleeded hex pickup audio, F0 contours, chords, beats, keys, and any published model outputs are outside the V3 evaluation input boundary.

### Right-to-use basis

- GuitarSet is publicly downloadable as an open Zenodo dataset.
- The accompanying `marl/GuitarSet` repository carries an MIT license and `mirdata` identifies GuitarSet with `LICENSE_INFO = "MIT License."`.
- V3 uses the dataset for internal research validation only and does not redistribute dataset audio or annotations.
- The GuitarSet publication must be cited in any external report using these results.
- If a later commercial-policy review determines additional dataset-rights documentation is required, that must be resolved before customer promotion; it may not be bypassed by the V3 result.

## Known-error exclusions — frozen before results

Exactly three tracks are excluded because the public GuitarSet issue tracker identifies annotation defects:

- `04_BN3-154-E_comp` — note annotations offset by approximately `+0.409 s`
- `04_Jazz1-200-B_comp` — note annotations offset by approximately `+0.309 s`
- `02_Funk2-119-G_comp` — duplicated MIDI-note annotation near `10.860 s`

No other track may be excluded after V3 results are viewed. If another dataset-integrity defect is discovered during execution, V3 fails closed and requires a new preregistration version rather than a post-hoc exclusion.

Therefore the locked evaluation corpus is the other **357 tracks**.

## Development / evaluation separation

V3 has **no GuitarSet development split** because no parameter fitting is allowed.

- Development data: deterministic synthetic/unit fixtures only.
- Evaluation data: all 357 locked GuitarSet v1.1.0 tracks above.
- No GuitarSet track may be used to choose thresholds, tolerances, weights, competitor definitions, channel combination, Basic Pitch settings, or exclusion rules.
- No per-track or aggregate GuitarSet correctness result may be inspected until the evaluator and validation harness are frozen and contract tests are green.

## Model event generation on GuitarSet

GuitarSet microphone audio is already isolated acoustic guitar. V3 therefore validates the pitch/onset model-evidence boundary directly and **does not invoke Demucs** on this corpus. This isolates the exact policy question left unresolved by V2: whether an emitted selected pitch/onset that passes the frozen independent corroborator is correct against an external note annotation.

For each locked track:

1. Require the microphone WAV to decode at exactly `44100 Hz`; any selected track at another rate fails the V3 protocol rather than being silently resampled or dropped.
2. Run the existing `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py` exactly once with its frozen defaults:
   - Basic Pitch package `0.4.0`
   - MIDI `40..88`
   - onset threshold `0.5`
   - frame threshold `0.3`
   - minimum note length `127.7 ms`
   - `multiple_pitch_bends=False`
   - `melodia_trick=True`
3. For each decoded note, V3 uses only:
   - deterministic note/event identity
   - `startSeconds`
   - integer `midi`.
4. Decoded Basic Pitch note end and confidence are diagnostics only and may not affect admission classification or reference matching.
5. Apply the frozen V2 `classify_window` rule to the exact microphone audio beginning at that event's rounded source start.
6. Preserve every decoded event; no failed/ambiguous event may be deleted or have its MIDI/onset rewritten.

The V3-positive evaluation set is exactly the decoded events classified `independently-corroborated-candidate` by the frozen V2 rule.

## Reference-note construction

For each locked track, reference notes are the union of all six GuitarSet per-string `midi_note` annotations in the track's v1.1.0 JAMS file.

For each reference note use only:
- annotated onset time in seconds;
- annotated MIDI value (continuous/fractional MIDI is preserved for pitch-distance calculation).

Reference offsets, fret/string identity, F0 contour, chords, beat position, key, mode, style, and any inferred chord annotation are not used to determine whether an estimated event is correct.

## Event matching — frozen before results

Correctness uses one-to-one maximum bipartite matching between V3-positive estimated events and reference notes, following the standard note-onset/pitch evaluation convention used by `mir_eval.transcription` with offsets ignored:

- onset tolerance: absolute difference `<= 0.050 s`
- pitch tolerance: absolute difference `<= 50 cents`
- offsets ignored
- each estimated event may match at most one reference note
- each reference note may match at most one estimated event
- matching maximizes the number of valid correspondences; no confidence or score is used to break correctness ties.

Estimated integer MIDI is converted to frequency using equal temperament, `440 * 2^((midi-69)/12)`. Reference continuous MIDI is converted using the same formula before cents comparison.

Polyphony is handled by the one-to-one matching across the union of all six strings; simultaneous valid notes may each match independently.

## Frozen metrics

Primary admission-evidence metric:

`positive precision = correctly matched V3-positive events / all V3-positive events`

Primary uncertainty measure:
- one-sided 95% Wilson score lower confidence bound
- `z = 1.6448536269514722`
- computed on the pooled locked 357-track V3-positive event inventory.

Secondary diagnostics, not tuning inputs:
- total Basic Pitch decoded event count
- total V3-positive / negative / insufficient counts
- baseline precision of all decoded Basic Pitch events under the same onset/pitch match rule
- V3-positive recall relative to all reference notes
- per-player and per-mode V3-positive precision/counts
- style/tempo/track diagnostics
- false-positive pitch-distance/onset-distance summaries.

No diagnostic may create a new threshold or post-hoc subgroup exception under V3.

## Frozen pass/fail policy

V3 external validation passes only if **all** of the following are true:

1. Dataset/file/version/exclusion identities exactly match this preregistration.
2. All 357 locked tracks execute without a post-hoc exclusion.
3. At least **1,000** V3-positive events exist across the locked evaluation corpus.
4. Overall V3-positive precision has a one-sided 95% Wilson lower bound **>= 0.9900**.
5. For each player ID `00..05`, V3-positive event count is at least `50` and point precision is **>= 0.9500**.
6. For each mode `comp` and `solo`, V3-positive event count is at least `50` and point precision is **>= 0.9500**.
7. Exact event identity is preserved and every non-promotion guard remains false/zero.

These are deliberately conservative product-policy gates selected before any GuitarSet model result is viewed. They may not be relaxed after evaluation. Failure requires a new successor preregistration based on independently justified changes; GuitarSet outcomes from V3 then become evaluation history and may not be used to tune that successor unless explicitly allowed by a new preregistered development protocol.

## Execution / inspection embargo

Before the V3 preregistration commit:
- dataset documentation and known-error metadata may be read;
- no Basic Pitch inference may be run on GuitarSet;
- no frozen V2/V3 classification may be run on GuitarSet;
- no event correctness/precision/recall result may be viewed.

After this preregistration commit, implementation and deterministic contract tests may proceed. The validation harness must be frozen before the first GuitarSet inference/evaluation run.

The first real GuitarSet validation execution must emit an immutable result artifact containing:
- dataset version and exact archive checksums
- complete 357-track identity list
- implementation/source commit
- package/runtime versions
- per-track event counts and aggregate class counts
- exact matching parameters
- pooled precision and Wilson lower bound
- fixed player/mode gates
- all non-promotion guards.

## Protected-song boundary

V3 external-corpus validation must not inspect or rerun the protected authorized song.

The historical V2 protected-song result (`187 / 951 / 2`) remains research history and cannot be retrospectively promoted by a V3 pass.

If V3 external validation passes, a **separate explicit policy review** is still required. Only after that review, and only if explicitly authorized, may a new Policy C-S epoch run a fresh protected-song V3 execution. No historical C-S epoch may be reused.

## Promotion boundary

Until V3 external validation is complete and a separate policy review explicitly authorizes further progression:

- `modelValidationComplete:false`
- customer-eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research remains paused
- no customer admission decision exists.

V3 must fail closed. Controlled tests, external aggregate counts, a high point estimate without the frozen lower-bound gate, a subgroup exception, or a protected-song historical result cannot independently promote the system.
