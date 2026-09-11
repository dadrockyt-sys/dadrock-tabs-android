# Songsterr Fresh — IDMT V4 Stage B Scoring Preregistration

Status: **PREREGISTERED EXTERNAL HOLDOUT SCORING / NOT ADMISSION AUTHORITY**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This document freezes the complete V4 IDMT external-validation scoring protocol before Basic Pitch or the frozen V4 classifier is run on any IDMT evaluation file.

No IDMT correctness result, estimate/reference match, precision, recall, Wilson bound, or V4-positive count had been viewed when this scoring preregistration was committed.

The historical GuitarSet/V3 result is not a tuning input. V4 keeps the same conservative product-policy accuracy target and the same standard note-onset/pitch matching convention that were frozen before V3 results existed.

## Bound dataset / Stage A evidence

Dataset: IDMT-SMT-Guitar Dataset, Zenodo v1.0.0, DOI `10.5281/zenodo.7544110`.

Bound archive:
- filename `IDMT-SMT-GUITAR_V2.zip`
- MD5 `06796e08731bccffaed6ae59361486e4`
- SHA-256 `02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a`.

Bound Stage A inventory:
- report SHA-256 `fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f`
- 4,292 ZIP members
- 1,173 WAV files
- 667 XML files
- 569 exact one-to-one WAV/XML leaf-stem pairs before Stage B mechanical filtering.

## Bound Stage B manifest-preparation result

Stage B manifest-preparation output SHA-256:

`dfea0060296ea2289e82041545e8da0f80dd81c5dee6668e8bc7ab08293bbdeb`

Included-manifest SHA-256:

`0c7946f6ac5af341bcca155a24189c4cd85b9366c0cab3282469ad43236ca344`

Frozen population summary:
- included WAV/XML pairs: **568**
- excluded exact Stage A pairs: **1**
- included by dataset directory:
  - `dataset1`: **312**
  - `dataset2`: **252**
  - `dataset3`: **4**
- total included reference note events: **4,661**
- reference pitch range: **MIDI 40.0 through 92.0**
- non-integer reference pitch count: **0**
- reference onset range: **0.19 through 68.0664 seconds**
- reference offset range: **1.4448 through 73.9406 seconds**.

The exact 568 included rows, the one excluded row and its frozen mechanical reason code(s), member identities, WAV headers, XML paths and per-file reference counts are defined by the hash-bound Stage B manifest-preparation artifact. The scoring harness MUST verify the exact output SHA-256 and included-manifest SHA-256 and MUST consume only those 568 included rows. No post-hoc file exclusion is permitted.

If the artifact cannot be reproduced byte-for-byte from the bound archive and Stage A report, scoring fails closed and this preregistration version is not executable.

## Annotation interpretation

For each included XML file:
- `instrumentRecording/transcription/event/onsetSec` is note onset in seconds from the paired WAV start;
- `instrumentRecording/transcription/event/offsetSec` is note offset in seconds from the paired WAV start;
- `instrumentRecording/transcription/event/pitch` is a MIDI-note coordinate.

Stage B non-scoring inspection established that every included `pitch` is mathematically integer-valued within `1e-9`.

For correctness matching V4 uses only:
- reference onset = `onsetSec`;
- reference MIDI = integer-valued `pitch`.

Reference `offsetSec`, duration, fret, string, expression, excitation, modulation, performer/instrument metadata and other XML fields are diagnostics only and MUST NOT affect correctness classification.

Reference notes above V4's playable range (MIDI 89..92) remain in the corpus and in recall diagnostics but cannot match a V4-positive estimate because the frozen Basic Pitch/V4 path emits only MIDI 40..88. They MUST NOT be removed post hoc.

## Audio / model execution

IDMT audio is already isolated guitar audio. **Demucs is not invoked** for this external validation.

Every included WAV must decode as mono, 44,100 Hz, uncompressed PCM with sample width 16 or 24 bit exactly as frozen by the Stage B manifest. No resampling, remixing, normalization, denoising or stem separation is permitted.

For each included WAV run the existing isolated-guitar transcriber exactly once with frozen defaults:
- script `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`
- Basic Pitch package `0.4.0`
- MIDI range `40..88`
- onset threshold `0.5`
- frame threshold `0.3`
- minimum note length `127.7 ms`
- `multiple_pitch_bends=False`
- `melodia_trick=True`.

For each decoded event preserve exact event identity and use only:
- decoded onset/start seconds as `sourceStart`;
- decoded integer MIDI as `selectedMidi`.

Decoded note end, duration and confidence are diagnostics only and may not affect V4 classification or reference matching.

## Frozen V4 classifier

Use the frozen implementation:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
- contract `songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4`
- implementation freeze commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`
- method record freeze commit `1f4e42a53d74d1ef6bec85a00546d7196f021135`.

No V4 constant or logic may change under this preregistration.

The V4-positive evaluation set is exactly the Basic Pitch decoded events classified `independently-corroborated-candidate` by the frozen V4 classifier.

All other decoded events remain preserved as negative/insufficient diagnostics and may not be deleted or rewritten.

## Matching rule — frozen before IDMT results

Correctness uses one-to-one maximum-cardinality bipartite matching between V4-positive estimated events and reference notes **within the same included file**.

A candidate estimate/reference edge exists only when both conditions hold:
- absolute onset difference `<= 0.050` seconds;
- absolute pitch difference `<= 50` cents.

Because both estimate and included reference MIDI values are integer-valued, the 50-cent rule is equivalent here to exact MIDI-note equality, but the cents calculation remains the formal rule.

Frequency conversion for cents calculation:

`frequency = 440 * 2^((midi - 69) / 12)`.

Additional matching rules:
- offsets ignored;
- each estimate matches at most one reference;
- each reference matches at most one estimate;
- maximize total valid correspondences;
- no Basic Pitch confidence, V4 score/margin, duration, string/fret or metadata is used to break correctness ties;
- simultaneous polyphonic notes may each match independently.

This is the same standard note-onset/pitch convention preregistered before V3 results and is intentionally not altered in response to V3.

## Metrics

Primary metric:

`V4-positive precision = matched V4-positive events / all V4-positive events`.

Primary uncertainty measure:
- one-sided 95% Wilson score lower confidence bound;
- `z = 1.6448536269514722`;
- computed on the pooled V4-positive inventory across all 568 included files.

Required diagnostics:
- total Basic Pitch decoded event count;
- V4-positive / not-corroborated / insufficient counts;
- matched V4-positive count;
- pooled V4-positive precision and one-sided Wilson lower bound;
- baseline precision of all decoded Basic Pitch events under the same one-to-one matching rule;
- V4-positive recall relative to all 4,661 reference notes;
- counts/precision by dataset directory (`dataset1`, `dataset2`, `dataset3`);
- counts/precision by WAV sample width (16-bit vs 24-bit) when both contain V4-positive events;
- unmatched-positive onset/pitch-distance diagnostics.

Diagnostics are not tuning inputs and cannot create new thresholds or exclusions under this version.

## Frozen pass/fail gates

V4 IDMT external validation passes only if **all** of the following are true:

1. Archive, Stage A report and Stage B manifest identities exactly match the hashes in this preregistration.
2. All 568 included files execute successfully with **zero** post-hoc exclusions.
3. At least **1,000** pooled V4-positive events are produced.
4. Overall V4-positive precision has a one-sided 95% Wilson lower bound **>= 0.9900**.
5. `dataset1` produces at least **100** V4-positive events and point precision **>= 0.9500**.
6. `dataset2` produces at least **100** V4-positive events and point precision **>= 0.9500**.
7. `dataset3` remains included in the pooled result, but with only four preregistered files it is a diagnostic stratum and has no standalone pass threshold. It may not be excluded from the pooled metric.
8. Any sample-width stratum with at least **100** V4-positive events must have point precision **>= 0.9500**. A sample-width stratum with fewer than 100 positives remains pooled and diagnostic only.
9. Exact decoded event identity/onset/MIDI is preserved through classification and matching.
10. Every policy/non-promotion guard remains false/zero.

The `0.9900` pooled lower-bound gate is the pre-existing conservative product-policy target frozen before V3 results existed. It is not selected from the historical V3 result and may not be relaxed after IDMT execution.

Failure of any mandatory gate closes this V4 admission-authority attempt. No threshold, V4 constant, matching tolerance, subgroup exception, file exclusion or Basic Pitch setting may be changed after seeing results under this preregistration.

## Runtime / provenance contract

The official run must use a clean checkout of `songsterr-fresh-pipeline-v1` at one exact commit containing this preregistration, the frozen V4 implementation and the final validation harness.

Runtime must be bound and recorded at minimum to:
- Linux x86_64;
- Python 3.10.x;
- Basic Pitch `0.4.0`;
- NumPy `1.26.4`;
- SoundFile `0.13.1`;
- librosa `0.11.0`.

The official immutable result must record:
- exact Git source commit and clean-worktree assertion;
- archive MD5/SHA-256;
- Stage A report SHA-256;
- Stage B manifest-preparation output SHA-256;
- included-manifest SHA-256;
- SHA-256 of the transcriber, frozen V4 implementation, scoring harness and this preregistration;
- runtime/package versions;
- complete 568-file identity list or hash-bound included manifest;
- per-file decoded/classification/matching counts;
- aggregate and required stratum metrics/gates;
- policy boundary.

Any source drift, dirty worktree, package-version mismatch, input-identity mismatch, failed file, malformed output, missing result row or rerun that overwrites an existing official result fails closed.

## Execution semantics

Exactly one official full-corpus result is permitted after the validation harness and its synthetic/contract CI are frozen green.

A pre-inference infrastructure failure that produces **no completed model inference result and no correctness observation** may be repaired only for execution plumbing without changing this preregistration, V4 logic, model settings, manifest, matching or gates. The failed attempt must be preserved as provenance.

Once any real correctness result is observed, no repair/tuning under this version is permitted; further methodological changes require a new successor preregistration and this IDMT result becomes evaluation history.

## Protected-song / product boundary

The protected authorized song MUST NOT be run under V4 during IDMT validation.

Even a full IDMT pass does not automatically authorize customer admission or a protected-song run. A separate post-result policy review is mandatory.

Until such a review explicitly authorizes advancement:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged;
- duration research paused;
- persistent Policy C remains `UNENROLLED`.

Historical GuitarSet/V1/V2/V3 results and the historical protected-song result cannot promote V4.
