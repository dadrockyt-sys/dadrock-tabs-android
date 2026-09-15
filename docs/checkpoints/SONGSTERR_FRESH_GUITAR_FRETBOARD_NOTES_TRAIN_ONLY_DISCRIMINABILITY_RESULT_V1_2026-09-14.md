# Songsterr Fresh — Guitar Fretboard Notes Train-Only Physical-Position Discriminability Result V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: COMPLETED — NON_HOLDOUT DESCRIPTIVE FEASIBILITY ONLY

## Authority / preregistration

Frozen before audio retrieval/analysis:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_FRETBOARD_NOTES_TRAIN_ONLY_DISCRIMINABILITY_PREREGISTRATION_V1_2026-09-14.md`
Preregistration commit: `ff62869274bd509802f5c4b3e565422eb23741f3`

Implementation/workflow integration head: `7ab93ec73848b9f0fee366cbf19f1dc13b39930f`

Dataset: `collegefishiesd/guitar-fretboard-notes`
Pinned dataset revision: `a33a26243e88e7ccd4893bee30eac3219ec8bef8`
Declared dataset license: `CC-BY-SA-4.0`

## Frozen split boundary honored

Only the 234-row `train` split was retrieved and decoded.
Observed train sources were exactly:
- `ele`: 78 rows
- `eqm`: 78 rows
- `eqm2`: 78 rows

Reserved sources were not accessed:
- `deb` / `test`: NOT ACCESSED
- `ele_natural` / `validation`: NOT ACCESSED

Integrity checks passed:
- row count exactly 234;
- each train source contained the complete six-string x fret-0..12 grid;
- `(source,string,fret)` identities unique;
- no reserved source identifier present;
- feature extraction failure count `0`.

Pinned downloaded train parquet SHA-256:
`86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`

## Implementation / CI

Implementation:
`scripts/songsterr-fresh/guitar_fretboard_notes_train_discriminability_v1.py`
Repository blob at integration head: `7d62fc354d8667742f796af5145b0a04203f4f7a`

Synthetic tests:
`scripts/songsterr-fresh/test_guitar_fretboard_notes_train_discriminability_v1.py`
Repository blob at integration head: `2e039d0ce3c83e6bb7d5097ca5ea31202ca96042`
13/13 tests passed in GitHub Actions.

Workflow:
`.github/workflows/songsterr-fresh-gfn-train-position-discriminability-v1.yml`
Repository blob: `efd64ba1575789c0a2311b412823c94822aea21e`

GitHub-hosted ordinary CPU run:
- run: `34914789254`
- job: `104209961023`
- head: `7ab93ec73848b9f0fee366cbf19f1dc13b39930f`
- status: `completed`
- conclusion: `success`

Canonical result artifact:
- name: `songsterr-fresh-gfn-train-position-discriminability-v1`
- artifact ID: `10375479293`
- uploaded artifact ZIP SHA-256: `580b08c329459b94e6a000c51f66dc59cabc893f642d6713f9e8bf55d35e57ec`

## Frozen primary result

Primary comparison used only the two acoustic train sessions from the same declared player and conditioned every decision on the exact corpus-labeled MIDI pitch. Therefore this was not a pitch-recognition test; each query was compared only with physically different string/fret candidates capable of the same pitch.

### `eqm` prototypes -> `eqm2` queries
- eligible same-pitch ambiguous-position queries: `68`
- correct physical `(string,fret)` positions: `41`
- exact-position accuracy: `0.6029411764705882` (60.29%)
- chance baseline: `0.3970588235294117` (39.71%)
- lift over chance: `0.20588235294117652` (+20.59 percentage points)

### `eqm2` prototypes -> `eqm` queries
- eligible queries: `68`
- correct positions: `32`
- exact-position accuracy: `0.47058823529411764` (47.06%)
- chance baseline: `0.3970588235294117` (39.71%)
- lift over chance: `0.07352941176470595` (+7.35 percentage points)

### Pooled descriptive result
- eligible queries: `136`
- correct positions: `73`
- exact-position accuracy: `0.5367647058823529` (53.68%)
- chance baseline: `0.3970588235294117` (39.71%)
- absolute lift over chance: `0.13970588235294124` (+13.97 percentage points)

## Interpretation

The frozen, very small deterministic feature set recovered physical string/fret identity above chance while pitch was held constant. That is evidence that these isolated-note recordings contain repeatable physical-position timbral information.

The direction asymmetry is material: 60.29% one way versus 47.06% in reverse. Therefore this result does **not** support a claim that audio-alone physical-position recovery is solved or robust across sessions. It instead justifies continued zero-cost NON_HOLDOUT research into session normalization, invariant feature design, and controlled train-only diagnostics while keeping the reserved external sources untouched.

This corpus still consists only of isolated single notes over frets 0–12 and cannot establish behavior for chords, simultaneous same-pitch notes, bends, slides, hammer-ons, pull-offs, rearticulation, overlapping sustain, techniques, full-song performance, or noisy deployment audio.

## Authorization boundary remains closed

This result is not Songsterr Fresh correctness evidence and does not replace independent physical-reference validation.

Required state remains:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Reserved `deb` / `ele_natural` audio must remain untouched unless a later separate preregistration explicitly authorizes a reserved-source evaluation.
