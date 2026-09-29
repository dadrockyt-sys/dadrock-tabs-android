# Post-V8 measurement review V1

Date: 2026-09-29 UTC  
Branch: `astra-work`  
Scope: committed-record reconciliation and pure fixture validation only. No audio decoding, new annotation, model inference, optimizer work, workflow dispatch, or production mutation.

## Bottom line

V8 remains a frozen no-advance result. The pre-V9 audit found a real comparability defect in the historical timing scalar: synthetic summaries count simultaneous chord-note multiplicity as zero-length IOIs and therefore also as `<=250 ms` repeats, while V2B's 164 references are one-dimensional spectral-flux landmark timestamps rather than per-string note labels. Historical V6/V7/V8 results must not be rewritten, but a future timing target must use a common acoustic-attack-group unit before any V9 candidate timing population is generated.

The V2B inventory remains exactly C01-C13 positive and D01-D04 negative-only. The frozen duration overlay changes C04 to 5.799183673469388 s and D01 to 8.097959183673469 s, yielding 110.023183673 s positive and 31.857959184 s negative. Source-byte hashes and URLs are recorded in the manifest; this review did not re-download or independently re-hash the audio bytes.

**V9 is not launch-ready.** The smallest next step is a model-free remeasurement of already committed V2B onset-landmark timestamps and the frozen synthetic baseline under the common timing contract below, with no audio access or model execution. Numerical V9 gates must be frozen only after that comparable reference table exists.

## Evidence-status table

| Evidence item | Status | Review finding |
|---|---|---|
| V2B eligible inventory | recorded + Git-verified record | Frozen manifest has 17 entries: 13 positive C01-C13 and 4 negative-only D01-D04. This verifies the committed record, not original bytes. |
| Filename / source URL / original-byte SHA-256 | recorded | Present per clip; byte hashes inherited, not rechecked here. |
| Evaluation durations | recorded with correction overlay | C04 and D01 rounded values were superseded pre-inference. Corrected totals are 110.023183673 s positive and 31.857959184 s negative. |
| V2B onset annotations | recorded + Git-verified record | 164 spectral-flux landmarks; detector landmarks, not exhaustive human-verified attacks. |
| V2B pitch annotations | recorded + Git-verified record | 57 trusted-pitch landmarks, 50 marked high confidence; no string/fret truth. |
| V2B scored pitch populations | recorded, denominator trace incomplete | V6 scoring uses 56 trusted / 49 high-confidence refs. The one trusted and one high-confidence exclusion are not explained in the V6 result itself. |
| V1.1 | recorded exposed evidence | Previously evaluated; closed to further tuning/confirmation, not an untouched holdout. |
| P1/P2/P3 | closed | No access in this review. |
| V6 timing summary | recorded | Synthetic p50/p90 0.3482993197/0.4179591837 s. Exact full timing orchestration source was not located in the active synthetic directory. |
| V7 timing source | partially reproducible | Result records executed-script SHA-256 and manifests, but exact timing-screen source is not retained in the active synthetic directory. |
| V8 timing source | independently source-verified | Retained blob `3c7efea4ce00d737a9ed1bb2711185b7a5fb1955` proves the chord multiplicity/zero-IOI issue and limited invalidity checks. |
| V8 result | recorded | Accepted no-advance result remains frozen; not rerun here. |
| Future holdout independence | unresolved by current development set | V2B is development-exposed. Any confirmation set must be genuinely new and grouped by source recording/creator where practical. |

## Reconciled V2B identity

Eligible positive clips: C01-C13 only.  
Eligible negative/background-only clips: D01-D04 only.  
Other uploaded MP3s are not automatically eligible; V1.1 material remains excluded.

Duration overlay frozen before V2B candidate output:

- C04: 5.806 s nominal -> **5.799183673469388 s** exact evaluation duration.
- D01: 8.098 s nominal -> **8.097959183673469 s** exact evaluation duration.
- Corrected positive denominator: **110.023183673 s**.
- Corrected negative denominator: **31.857959184 s**.

Annotation identity:

- onset method: model-free spectral-flux onset detection;
- pitch method: model-free YIN stability around selected landmarks;
- 164 onset landmarks;
- 57 trusted-pitch landmarks, 50 marked high confidence in the raw annotation record;
- no string/fret annotations;
- polyphonic/effect-heavy clips explicitly are not exhaustive pitch ground truth.

V6 later scored 56 trusted and 49 high-confidence references. The committed result does not carry the exact per-landmark exclusion explanation. This is a provenance gap, not permission to infer or repair the denominator.

## Common timing contract for future pre-V9 measurement

This is prospective and does not alter V6/V7/V8 acceptance.

1. **Separate units.** Note labels are string/fret/pitch targets; acoustic attack groups are distinct temporal attacks for timing measurement. A three-note chord can be three note labels but one attack group.
2. **Simultaneous grouping tolerance.** Proposed default: 10 ms in crop-local seconds. Freeze the value before recomputing target statistics. Do not infer note multiplicity from real V2B landmark lists.
3. **Crop-local origin.** All attack times are relative to the frozen evaluation crop start.
4. **Duration identity.** Use exact corrected evaluation duration where an overlay exists; rounded display metadata is descriptive only.
5. **Endpoint rule.** Prospectively use half-open `[0, duration)`.
6. **IOI definition.** IOIs are positive differences between consecutive acoustic attack groups. Zero IOIs from note multiplicity are excluded by construction.
7. **Repeat metric.** `repeat250` is the fraction of eligible positive IOIs `<=0.250 s`. It is a short-gap statistic, not repeated-pitch/technique truth.
8. **Density denominator.** Aggregate positive attack density = total attack groups / positive evaluation seconds only.
9. **Negative evidence.** Negative/background-only duration is reported separately and gets no pseudo-onsets.
10. **Quantiles.** Freeze an exact quantile convention in source before corrected V9 targets are published; recommended is the linear empirical convention used historically.
11. **Pooling.** Report pooled and per-clip summaries. Synthetic data also require per-family counts/summaries. Do not invent equivalent family labels for V2B.
12. **Empty/singleton clips.** They contribute duration and clip rate, zero IOIs, and an undefined—not zero—clip repeat fraction.
13. **Completeness qualification.** V2B timing metrics describe the frozen detector-landmark sample, not exhaustive audible-attack truth.

## Historical timing reconciliation

### V6

The V6 committed result reports 273 positive synthetic clips, 903 events and 546 s, with synthetic p50/p90 IOIs **0.3482993197/0.4179591837 s**. V2B is reported as 164 landmarks over 110.023183673 s with p50/p90 **0.256/0.882358 s** and historical `repeat250` **0.4701986755**.

Those numbers remain historical. The exact full orchestration producing the V6 synthetic timing table is not retained under the active synthetic source names located in this review; only the onset-objective helper/test and result-side runner SHA-256 are readily identifiable. Therefore V6 timing source semantics were not independently reproduced here.

### V7/V8

V7/V8 template summaries use a 2-second baseline p50/p90 **0.34/0.40 s**, not V6's **0.3482993197/0.4179591837 s**. Do not call them numerically identical without a source trace explaining the transformation difference.

Retained V8 source shows the old `repeat250` comparison is unit-inconsistent:

- `base_attacks("chords")` emits `[.32,.32,.32,1.08,1.08,1.08]`;
- adjacent note-level timestamps are converted directly to IOIs;
- zero IOIs count both as simultaneous and as `<=.25` repeats;
- L0 reports simultaneous fraction and repeated fraction both as 0.2666667.

For the inspected templates, that equality means all L0 short-gap "repeat" mass can be explained by simultaneous chord multiplicity. It cannot be compared directly with one-dimensional V2B spectral-flux landmark gaps as if the units were the same.

V8 also changed more than duration: motif repetition, repeated-family spacing 0.18 s, and random 0.7-1.1 s inter-motif gaps. Its `invalidClipCount` checks onset bounds only; it does not validate pitch/string/fret labels, offsets, sustains, overlap, split identity, or negative examples. Its fallback numerator counts correction operations while the design refers to a fraction of clips with fallback. These limitations do not change V8's frozen no-advance decision.

## Pure validator added

Added:

- `astra_backend/synthetic/v9_measurement_contract_v1.py`
- `astra_backend/synthetic/test_v9_measurement_contract_v1.py`

Focused fixture run against the exact candidate source completed **10/10 tests passed**. Covered: chord grouping, distinct short-gap attacks, empty/singleton clips, crop boundaries, duplicate IDs, invalid numeric fields, impossible durations, correction propagation, positive-only density, and count/rate consistency.

No audio/model/numpy/torch dependency is imported.

## What is established versus uncertain

Established:

- V8 correctly stopped before rendering/training/inference.
- V2B inventory and corrected duration denominators are stable committed records.
- V2B annotations are algorithmic landmarks, not exhaustive human truth.
- Historical synthetic timing summaries mixed note multiplicity into attack timing in retained V8 source.
- V2B is development-exposed and cannot be used as a fresh confirmation holdout.

Uncertain:

- corrected synthetic-versus-V2B distance in a common attack-group unit;
- exact V6 -> V7/V8 baseline transformation provenance;
- exact 57/50 -> 56/49 pitch-reference exclusion trace;
- whether event timing is causally important for transfer once renderer/representation/loss/calibration interactions remain;
- fresh independent product performance.

## Readiness assessment and exact next step

**Not ready for V9 empirical execution.**

The smallest next task is **PRE-V9-MEASUREMENT-V1**:

- use only committed V2B manifest/correction/annotation JSON and retained frozen synthetic baseline records/source;
- no original audio access;
- no new annotations;
- no inference or optimizer;
- apply the common acoustic-group contract;
- publish per-clip counts plus pooled/clip-balanced timing summaries, and per-family synthetic summaries;
- preserve raw historical metrics and corrected-unit metrics as different versions;
- resolve or explicitly retain as unresolved the 57/50 -> 56/49 scoring provenance;
- freeze the target table and implementation hash before any V9 candidate generator emits candidate timing output.

Only after that table is reviewed should V9 numerical gates be frozen and empirical authorization requested.
