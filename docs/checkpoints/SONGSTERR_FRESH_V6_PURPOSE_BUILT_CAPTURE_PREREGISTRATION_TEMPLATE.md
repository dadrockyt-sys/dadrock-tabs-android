# Songsterr Fresh V6 — Purpose-Built External Holdout Capture Preregistration Template

Status: **DRAFT TEMPLATE ONLY — NOT A PREREGISTRATION, NOT FROZEN, NO CAPTURE/PROCUREMENT AUTHORIZED**

Branch: `songsterr-fresh-pipeline-v1`

## How this template may be used

This file exists so a future purpose-built external holdout can be frozen **before the first admitted holdout take is recorded**.

It is not itself an experiment authorization. Before use:

1. the user must explicitly choose/authorize the purpose-built route and any spending/contact/acquisition;
2. copy this template to a new corpus-specific dated checkpoint;
3. replace every `TBD` / placeholder with an exact value;
4. delete any inapplicable option rather than leaving alternatives open;
5. commit the completed corpus-specific preregistration before any admitted holdout take exists;
6. after that commit, do not change capture/reference/population rules in response to holdout data or model output.

Calibration-only recordings made under a separately frozen non-holdout calibration section may precede admitted holdout capture. They can never enter the holdout.

This template does **not** reopen archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research or protected-song execution.

---

## 1. Immutable frozen V6 authority

The completed preregistration must cite, without modification:

- V6 method checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`
- V6 implementation commit: `3a6cbb144fec5613ab6350deb6539297d713df28`
- V6 implementation blob: `2b18ef0ee710a6ad5ecb27253b977495db7d6534`
- external scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`
- external scoring framework commit: `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`

Frozen model/scoring essentials remain:

- Basic Pitch `0.4.0` CPU;
- MIDI range `40..88`;
- onset threshold `0.5`;
- frame threshold `0.3`;
- minimum note length `127.7 ms`;
- `multiple_pitch_bends=False`;
- `melodia_trick=True`;
- every decoded event preserved/classified exactly once;
- V6 cannot delete/repitch/rewrite a decoded event;
- match onset tolerance `<=0.050 s`;
- pitch tolerance `<=50 cents`;
- deterministic one-to-one maximum-cardinality matching;
- primary V6-positive precision;
- one-sided 95% Wilson lower bound;
- pooled V6-positive minimum `>=1,000`;
- pooled Wilson lower bound `>=0.9900`;
- player/category strata with `>=100` positives require point precision `>=0.9500`;
- categories exactly `chords`, `scales`, `singlenotes`, `techniques`, `music`;
- deferred correctness reveal;
- one official real-holdout correctness run;
- no duration-authority change;
- no protected-song use;
- no Production/customer promotion from the execution itself.

No field in this capture preregistration may weaken or modify those rules.

---

## 2. Corpus identity

Fill before admitted capture:

- corpus working name: `TBD`
- corpus version: `TBD`
- capture start date/time window: `TBD`
- capture organization/location(s): `TBD`
- responsible capture operator(s): `TBD`
- number of planned players: `TBD`
- target raw reference note-ons: `TBD`
- planned total performances/takes: `TBD`
- exact source-control commit freezing this preregistration: `TBD AFTER COMMIT`

Planning values such as a target of ~20,000 raw reference note-ons or >=5 players are collection-capacity preferences only. They do not replace the frozen >=1,000 V6-positive admission gate.

---

## 3. Rights / originality contract

Before admitted capture, freeze exact rights terms and document hashes/identities.

Required:

- every musical exercise/excerpt is newly composed for this project, public domain, or covered by explicit written rights suitable for commercial/product-validation use;
- no protected song, recognizable protected-song excerpt, backing track or third-party recording is used;
- performer releases cover the audio performance, raw reference/MIDI/sensor stream, metadata and reproducibility storage needed for validation;
- capture personnel/venue rights are cleared where applicable;
- the project may retain immutable source bytes/hashes and internally reproduce validation results;
- no term depends on a later commercial release, stream count or music-production-only incorporation license.

Freeze:

- rights agreement filename(s): `TBD`
- SHA-256(s): `TBD`
- exact rights holder(s): `TBD`
- allowed product-validation/research use: `TBD EXACT TEXT/REFERENCE`
- redistribution/publication limitations: `TBD`

Failure to establish rights before admitted capture => **do not capture the holdout**.

---

## 4. Reference hardware architecture

### 4.1 Evaluated audio path

Exact guitar / pickup / interface path:

- guitar model/serial: `TBD`
- conventional magnetic pickup(s): `TBD`
- pickup selector/control settings: `TBD`
- DI/interface model + serial: `TBD`
- input channel: `TBD`
- gain/pad/Hi-Z settings: `TBD`
- sample rate / bit depth / container: `TBD`
- DAW/capture software/version: `TBD`
- effects/amp/cab/saturation/noise gate/compression: **NONE unless frozen framework explicitly permits; expected NONE**

The evaluated V6 source must be isolated real-guitar DI. Reference-sensor audio/piezo channels cannot become alternate scoring audio or a rescue path.

### 4.2 Independent reference path

Exact hardware:

- reference device/model/revision/serial: `TBD`
- firmware version/hash or exact version identifier: `TBD`
- fret/string sensing mechanism: `TBD`
- trigger/onset sensing mechanism: `TBD`
- bend/aftertouch mechanism: `TBD`
- MIDI protocol/mode: `TBD`
- per-string channel mapping: `TBD`
- raw event format: `TBD`
- host/interface model/serial: `TBD`
- capture software/version: `TBD`

Freeze every configurable setting that can affect emitted note identity/timing, including as applicable:

- trigger gain/sensitivity by string: `TBD`
- trigger filter/window by string: `TBD`
- decay/note-off behavior: `TBD`
- open-string behavior: `TBD`
- legato/hammer/pull-off mode: `TBD`
- slide/retrigger mode: `TBD`
- pitch-bend range: `TBD`
- hand-position/ghost-note filtering: `TBD`
- transpose/tuning: `TBD`
- velocity/dynamics mode: `TBD`
- MPE/poly mode: `TBD`
- any DAW MIDI transformations: **NONE** unless explicitly enumerated and frozen.

The reference may be sensor/algorithm derived; it is not presumed infallible. The experiment relies on independent sensing + pre-correctness structural rejection, not vendor marketing claims.

### 4.3 Settings export

Before admitted capture:

- export configuration file if supported;
- screenshot/record every non-exportable hardware setting;
- hash all configuration artifacts;
- commit configuration identities, not private credentials, to the corpus-specific checkpoint.

Settings may not change during admitted holdout capture except under a preregistered catastrophic-device replacement rule. If changed, the affected population treatment must already be frozen here.

---

## 5. Clocking / timing topology

Freeze exact topology before capture:

- audio clock source: `TBD`
- MIDI timestamp source: `TBD`
- shared host/timeline: `TBD`
- buffer size: `TBD`
- audio input latency handling: `TBD`
- MIDI input latency handling: `TBD`
- operating system/version: `TBD`
- driver/version: `TBD`
- MIDI transport (USB/DIN/etc.): `TBD`

Preferred: audio DI and raw MIDI recorded simultaneously on one host/timeline without post-recording quantization.

If a constant transport offset may exist, freeze a **reference-blind alignment audit** before admitted capture. That audit may estimate only a whole-performance/global timing offset under a preregistered method. It may not:

- move individual note events independently;
- delete/insert/repitch notes;
- use V6/Basic Pitch correctness;
- optimize an offset to maximize correctness.

Exact permitted alignment outcomes/method: `TBD IN CORPUS-SPECIFIC PREREGISTRATION`.

---

## 6. Non-holdout hardware/player calibration phase

Calibration recordings are **not holdout data** and can never be admitted later.

Freeze before calibration:

- calibration exercise list/hash: `TBD`
- exact allowed setting ranges: `TBD`
- calibration success criteria: `TBD`
- maximum calibration iterations per player/device: `TBD`
- operator-visible diagnostics: `TBD`

Allowed calibration evidence may include:

- raw emitted MIDI/reference events;
- known calibration-note/fret sequences;
- hardware diagnostics;
- transport integrity;
- device-specific tuning/sensitivity guidance.

Forbidden during calibration:

- Basic Pitch predictions;
- V6 classes;
- V6 correctness;
- protected-song material;
- selecting settings because they improve model performance.

At calibration completion:

- export/hash final settings;
- mark calibration data permanently `NON_HOLDOUT`;
- freeze final settings before the player's first admitted take.

No admitted holdout take may be retroactively reclassified as calibration.

---

## 7. Musical population frozen before capture

### 7.1 Exercise source

Freeze exact exercise corpus before admitted capture:

- composition/source manifest path: `TBD`
- manifest SHA-256: `TBD`
- exercise score/tab hashes: `TBD`
- rights identity per exercise: `TBD`

Exercises must not be selected or revised using Basic Pitch/V6 output.

### 7.2 Categories

Each exercise receives exactly one frozen category before capture:

- `chords`
- `scales`
- `singlenotes`
- `techniques`
- `music`

Freeze category assignment manifest SHA-256: `TBD`.

### 7.3 Difficulty/style/tempo/tuning factors

Freeze in advance as applicable:

- tempo grid/distribution: `TBD`
- standard/alternate tuning policy: `TBD`
- pick/finger policy: `TBD`
- clean technique set (hammer-on, pull-off, slide, bend, mute, etc.): `TBD`
- polyphony/chord density distribution: `TBD`
- target note range: must remain compatible with frozen scoring MIDI range; exact capture population `TBD`
- player/exercise assignment rule: `TBD`
- randomized order seed/algorithm: `TBD`

No later model-driven balancing is allowed.

---

## 8. Player diversity and independence

Freeze:

- player inclusion criteria: `TBD`
- player exclusion criteria unrelated to model output: `TBD`
- planned number: `TBD`
- experience-stratum policy if any: `TBD`
- handedness policy if relevant: `TBD`
- instrument sharing/assignment: `TBD`

Players/capture staff must not receive:

- Basic Pitch/V6 output;
- target failure examples discovered from revealed holdouts;
- optimizer/threshold results;
- instructions to alter technique to help the model.

---

## 9. Attempt / retake rule — freeze before capture

This section is essential to prevent reference-quality cherry-picking.

Recommended rigorous rule to adopt or replace explicitly:

### 9.1 Acquisition attempt

For each scheduled player/exercise slot, attempts are numbered chronologically.

An attempt may be discarded/retaken **only before it becomes admitted** and only for an objective acquisition failure from the frozen list below.

Allowed acquisition-failure reasons (fill exact thresholds):

- missing/truncated audio file: `TBD`
- missing/truncated raw reference file: `TBD`
- device disconnect/logged transport failure: `TBD`
- wrong sample rate/container/channel count: `TBD`
- clipping threshold exceeded: `TBD`
- capture software crash: `TBD`
- operator starts/stops wrong scheduled exercise before performance completion: `TBD`
- other purely infrastructural failures: `TBD EXHAUSTIVE LIST`

### 9.2 First transport-valid attempt is admitted

The **first** chronologically completed attempt that passes only the frozen acquisition-integrity checks becomes the immutable admitted take.

After admission, do not replace it because of:

- orphan MIDI note-on/off;
- same-key overlap;
- missed/extra sensor note;
- musical imperfection;
- reference/model disagreement;
- Basic Pitch/V6 behavior;
- apparent difficulty;
- poor V6 correctness.

Those are not retake grounds.

### 9.3 Structural anomaly consequence

Semantic reference anomalies discovered later in the reference-blind audit are handled by the frozen audit outcome, not by retaking/replacing individual admitted performances.

Under the current preferred fail-closed design, any violation of required zero-anomaly semantics makes the preregistered scoring population structurally unsuitable and prevents correctness, rather than silently dropping/replacing the bad take/event.

Exact corpus-level structural decision rule: `TBD/FREEZE BEFORE CAPTURE`.

---

## 10. Capture-stage QA — model blind

Allowed capture QA is only what is frozen in Section 9 and basic identity/completeness checks.

Capture personnel must not run or inspect:

- Basic Pitch;
- V6;
- any transcription model;
- any automatic onset detector on admitted DI to decide whether to keep/retake;
- any correctness matcher;
- any per-take precision/recall.

The raw reference stream may be archived automatically, but semantic event-cleanliness evaluation should occur only under the later preregistered reference-blind structural audit unless an exact pre-admission check has been explicitly frozen and scientifically justified here.

---

## 11. Raw-file immutability / manifest

For every attempt, preserve enough metadata to prove chronology even if an acquisition-failure attempt is excluded.

For every admitted take retain/have manifest entries for:

- player pseudonymous ID;
- exercise ID/category;
- attempt number;
- UTC/local timestamp;
- evaluated DI source path;
- evaluated DI SHA-256;
- raw reference/MIDI source path;
- raw reference SHA-256;
- hardware configuration identity;
- calibration identity;
- recording software/session identity;
- source format metadata;
- acquisition QA outcome/reason code.

Freeze manifest serialization and sorting rules: `TBD`.

No admitted source byte may be edited in place.

---

## 12. Reference event semantics

Freeze parser before capture/audit:

- MIDI parser/library/version: `TBD`
- note-on velocity zero treatment: `TBD`
- channel policy: `TBD`
- sustain/controller handling: `TBD`
- pitch-bend handling for selected integer MIDI truth: `TBD`
- repeated same-key semantics: `TBD`
- unmatched note-on/off semantics: `TBD`
- event ordering tie-break: `TBD`
- time conversion precision: `TBD`

For V6 onset+pitch scoring, reference offsets/durations remain non-authoritative unless separately approved; do not let note-off cleanup create onset authority changes.

No individual event may be manually deleted/inserted/repitched/shifted based on DI listening or model output.

---

## 13. Reference-blind structural/alignment audit contract

Before any Basic Pitch/V6 invocation on admitted holdout audio, freeze and run a separate audit.

At minimum audit:

- exact source hashes and full population completeness;
- one-to-one DI/reference pairing;
- finite nonempty audio;
- declared audio format/sample metadata;
- deterministic reference parsing;
- reference event counts;
- zero orphan note-ons;
- zero orphan note-offs;
- zero same-key overlaps under frozen semantics;
- expected channel/string mapping;
- no silent take/file/event dropping;
- deterministic reference-blind transport/alignment outcome;
- immutable package/population/alignment manifest hashes.

Audit code/checkpoint path: `TBD`.
Audit code commit/blob: `TBD`.

Possible outcomes must be frozen before running audit, e.g.:

- `A_STRUCTURALLY_SUITABLE_ZERO_OFFSET`
- `B_STRUCTURALLY_SUITABLE_FROZEN_TRANSPORT_OFFSET`
- `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`

Exact A/B/C criteria: `TBD`.

Outcome C means **no Basic Pitch, no V6, no correctness** and no post-hoc repair/drop/retake rescue.

---

## 14. Canonical audio construction

The eventual binding must preserve the already-frozen external scoring audio preparation, not invent a new model path from this holdout.

For each admitted DI source, record exact source hash, then apply the frozen canonical isolated-guitar preparation used by the external framework (including 44.1 kHz canonicalization and deterministic shared waveform construction) exactly as bound in the final execution contract.

No normalization, denoising, source separation, amp simulation, Demucs or reference-piezo substitution may be introduced as a holdout-specific rescue.

Exact binding text/path: `TBD AFTER STRUCTURAL AUDIT, BEFORE CORRECTNESS`.

---

## 15. No-real-correctness harness stage

Before the one official real-holdout run:

- build final harness against synthetic/contract-only fixtures;
- test event preservation;
- test parser/matcher boundary conditions;
- test Wilson statistic;
- test identity guards;
- test failure behavior;
- do not expose any admitted holdout correctness during harness development.

Harness commit/blob/run identity: `TBD`.

---

## 16. Official correctness execution contract

Only after a structurally suitable audit and immutable binding:

Phase 1 — reference blind:
- verify all identities;
- canonicalize every admitted DI;
- run Basic Pitch exactly once per performance;
- preserve all decoded events;
- run frozen V6 exactly once per decoded event;
- persist classifications;
- emit no correctness metrics.

Phase 2 — one reveal:
- load immutable reference events/alignment;
- run frozen one-to-one matcher;
- calculate aggregate/stratum metrics/gates once;
- write one immutable result artifact before interpretation.

Official runtime/run mechanism: ordinary GitHub CPU unless separately authorized otherwise.

No rerun after correctness exposure to seek a better result.

---

## 17. Policy boundary after result

Even if all frozen scientific gates pass, retain until separate policy review:

- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`
- `protectedSongUsed:false`
- `separatePolicyReviewRequired:true`

---

## 18. Sign-off / freeze checklist

The corpus-specific preregistration cannot be declared frozen until every box is satisfied:

- [ ] explicit user authorization for the purpose-built route/spend/contact/capture already exists
- [ ] exact rights contract frozen
- [ ] protected songs excluded
- [ ] hardware model/revision/serials frozen
- [ ] firmware/settings/config hashes frozen
- [ ] evaluated magnetic DI path frozen
- [ ] independent reference sensing path frozen
- [ ] clock/timing topology frozen
- [ ] non-holdout calibration protocol frozen
- [ ] calibration data permanently excluded
- [ ] exercise manifest/category assignments frozen
- [ ] player assignment/randomization frozen
- [ ] objective acquisition-failure/retake rules frozen
- [ ] first-transport-valid-attempt rule frozen
- [ ] raw-file hashing/manifest format frozen
- [ ] MIDI/reference parser semantics frozen
- [ ] structural/alignment audit method/outcomes frozen
- [ ] no Basic Pitch/V6/model output used in population construction
- [ ] all `TBD` placeholders removed
- [ ] corpus-specific preregistration committed before first admitted take

If any item is false, do not start admitted holdout capture.

---

## Current authority

This template itself authorizes **nothing** beyond paper/design work.

No product purchase/deposit, manufacturer/rightsholder/performer contact, hiring, recording, data acquisition, Basic Pitch/V6 holdout execution, protected-song execution, GPU use or Production promotion is authorized by this file.
