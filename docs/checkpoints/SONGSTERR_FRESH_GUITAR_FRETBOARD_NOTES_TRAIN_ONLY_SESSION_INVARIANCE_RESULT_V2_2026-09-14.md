# Songsterr Fresh — Guitar Fretboard Notes Train-Only Session-Invariance Result V2

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN RESULT — NON_HOLDOUT FEASIBILITY ONLY

## Authority and preregistration

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_FRETBOARD_NOTES_TRAIN_ONLY_SESSION_INVARIANCE_PREREGISTRATION_V2_2026-09-14.md`

Preregistration commit:
`e528ebd1279ec883da0b786d73dd25e03aa47890`

The V2 method was frozen before any V2 real-audio result execution or observation.

## Implementation and CI identity

Implementation:
`scripts/songsterr-fresh/guitar_fretboard_notes_train_session_invariance_v2.py`
blob `6340ef9cfc6c8fc59d6caf83eca6a1db020a2c1b`

Synthetic tests:
`scripts/songsterr-fresh/test_guitar_fretboard_notes_train_session_invariance_v2.py`
blob `348ff567d7a5c0f88657d306be8c50a32f2682b2`

Workflow:
`.github/workflows/songsterr-fresh-gfn-train-session-invariance-v2.yml`
blob `510946af72f07aedf33e475c8f8ca06ae79d30ae`

Workflow head:
`fb9e391477e77e0e9d3dee42243d0e812a33d581`

GitHub Actions run:
- run ID `34915518842`;
- job ID `104212166273`;
- conclusion `success`;
- 18/18 synthetic contract tests passed before real-audio execution;
- real train-only V2 study step succeeded;
- result-print step succeeded;
- artifact upload succeeded.

Artifact:
- artifact ID `10375219509`;
- artifact name `songsterr-fresh-gfn-train-session-invariance-v2`;
- artifact size `2867` bytes;
- uploaded ZIP SHA-256 `2ed0080474a57810b7fcd4f1babccd0c33e9db97340aed94fae653f5f6b333cc`.

Canonical result JSON SHA-256:
`0a1f39e33a791371e2f7aa6f1ccc7a25d476052be08b8eb80645129bf01869f7`

## Corpus integrity / access result

Pinned dataset revision:
`a33a26243e88e7ccd4893bee30eac3219ec8bef8`

Pinned train parquet SHA-256 verified:
`86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`

Observed source set exactly:
- `ele`;
- `eqm`;
- `eqm2`.

Rows:
- `ele`: 78;
- `eqm`: 78;
- `eqm2`: 78;
- total: 234.

Integrity:
- complete position grid per source: true;
- identity uniqueness: true;
- feature extraction failures: 0;
- normalization finite checks: pass.

Reserved access remained false:
- `reservedSplitsAccessed:false`;
- `reservedSourcesAccessed:false`.

Therefore `deb` and `ele_natural` remain untouched by this study.

## Frozen V2 primary result

### `eqm` prototypes -> `eqm2` queries

- eligible same-pitch ambiguous-position queries: 68;
- correct exact physical positions: 36;
- exact-position accuracy: `0.5294117647058824` = `52.94%`;
- chance baseline: `0.3970588235294117` = `39.71%`;
- lift over chance: `0.13235294117647067` = `+13.24` percentage points.

### `eqm2` prototypes -> `eqm` queries

- eligible queries: 68;
- correct exact physical positions: 33;
- exact-position accuracy: `0.4852941176470588` = `48.53%`;
- chance baseline: `0.3970588235294117` = `39.71%`;
- lift over chance: `0.08823529411764713` = `+8.82` percentage points.

### Pooled

- eligible queries: 136;
- correct exact physical positions: 69;
- exact-position accuracy: `0.5073529411764706` = `50.74%`;
- chance baseline: `0.3970588235294117` = `39.71%`;
- lift over chance: `0.11029411764705888` = `+11.03` percentage points.

Absolute directional accuracy gap:
`0.04411764705882354` = `4.41` percentage points.

## Frozen comparison with V1

V1 pooled exact-position accuracy:
`0.5367647058823529` = `53.68%`.

V2 pooled exact-position accuracy:
`0.5073529411764706` = `50.74%`.

Change:
`-0.02941176470588236` = `-2.94` percentage points.

V1 absolute directional gap:
`0.13235294117647056` = `13.24` percentage points.

V2 absolute directional gap:
`0.04411764705882354` = `4.41` percentage points.

Gap change:
`-0.08823529411764702` = `-8.82` percentage points.

Under the frozen preregistered interpretation rule:
- pooled accuracy improvement condition: **false**;
- directional-gap improvement condition: **true**;
- frozen classification: `MIXED`.

## Interpretation

The frozen source-wise median/MAD normalization substantially reduced the directional asymmetry between the two acoustic train sessions, from 13.24 percentage points to 4.41 percentage points. That is evidence that a material part of the V1 directional asymmetry was session-distribution related.

However, the same normalization reduced pooled exact-position accuracy from 53.68% to 50.74%, a drop of 2.94 percentage points. Therefore this V2 transformation is not an overall improvement under the frozen rule and must not replace V1 as a superior physical-position discriminator on the basis of this experiment.

The appropriate result is `MIXED`: better session symmetry, worse pooled discrimination.

This remains train-only, transductive, NON_HOLDOUT feasibility evidence. Query-source distribution statistics were intentionally used by the frozen normalization contract. It must not be represented as untouched external validation.

The result does not establish behavior for chords, simultaneous same-pitch notes, bends, slides, hammer-ons, pull-offs, rearticulation, overlapping sustain, full-song performance, noisy deployment audio, or the frozen V6 correctness objective.

No tuning or V2 rerun is authorized from this observed result. Any later V3-style experiment would require a separately frozen preregistration before execution and must continue to keep reserved `deb` and `ele_natural` untouched unless separately authorized in advance.

## Downstream state — unchanged / fail closed

- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Duration authority remains paused. Policy C remains `UNENROLLED`. Protected-song execution remains embargoed. Archived V143/Gomyway and other closed lines remain closed.
