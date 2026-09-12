# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-12 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT, reference/pro scoring, training/fine-tuning, broad threshold/optimizer sweeps and duration work remain closed unless explicitly reopened.
- Never silently alter/drop MIDI or event identity.
- Preserve `/ai-tab` UX flow.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP work stays under `scripts/songsterr-fresh/`.

Authority remains fail-closed:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged / duration research paused
- persistent Policy C `UNENROLLED`.

## CLOSED HISTORICAL LINES

V1/V2 are rejected research diagnostics. Historical protected-song outcomes may not tune successors.

V3 is closed after frozen GuitarSet validation failed. GuitarSet is historical/contaminated for successor holdout use.

V4 is closed/rejected after IDMT external validation:
- 568/568 files
- 7,619 decoded
- 1,644 positives
- 1,292 correct
- precision `0.7858880778588808`
- one-sided 95% Wilson LB `0.7687844934184139` vs required `0.9900` → FAIL
- immutable artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`
- immutable result commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`
- policy rejection commit `01a276045d32b643aa17013b959e89e41b0f305e`.

IDMT is historical/contaminated for successor holdout use.

## V5 — ACTIVE SUCCESSOR / SYNTHETIC CONTRACT GREEN

User explicitly authorized V5 on 2026-09-12 to address the prior failure mechanism.

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`
commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.

Contract:
`songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.

V5 is not a V4 threshold retune. It is a reference-blind polyphony-aware harmonic dictionary + selected-pitch leave-one-out NNLS necessity test.

Actual frozen implementation constants at current source:
- mono isolated guitar 44,100 Hz
- existing onset + selected integer MIDI 40..88 only
- three 8,192-sample post-onset windows at offsets `2048`, `8192`, `14336`
- FFT `32768`
- playable MIDI dictionary 40..88
- harmonics 1..8, `1/h` weighting, normalized candidate templates
- deterministic NNLS
- minimum demeaned RMS `1e-4`
- necessity fraction minimum `0.01`
- selected fundamental / own max harmonic ratio minimum `0.05`
- all three views must pass; no voting/fallback
- NumPy `1.26.4`, SciPy `1.15.3`
- no reference truth, duration/end, next onset, Basic Pitch confidence/activation, performer/style/dataset/bit-depth identity, or event rewriting.

Implementation:
`scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`
commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.

Synthetic fixtures:
`docs/checkpoints/SONGSTERR_FRESH_V5_SYNTHETIC_FIXTURES.json`
commit `efca2994efdce2c5a3b35d6e12fb9dc82096a268`.

Controlled V5 CI is green on the 20-case synthetic contract (`13 corroborated / 4 not / 3 insufficient`), including true-note retention in dyads/triads/six-note mixture/close dyad/dominant-harmonic cases and rejection of wrong octave, adjacent semitone, temporal pitch change, silence/truncation.

Method record:
`docs/checkpoints/SONGSTERR_FRESH_POLYPHONIC_HARMONIC_NECESSITY_V5.md`.

This is structural/synthetic progress only, not admission evidence.

## V5 EXTERNAL HOLDOUT — FLGD SELECTED

Selected untouched candidate: François Leduc Guitar Dataset (FLGD).

Frozen source:
- Hugging Face `xavriley/FrancoisLeducGuitarDataset`
- canonical origin `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- exact revision `a38306c244b3ea81496ad58b4514622185e58211`
- selected release card declares MIT
- release describes audio + aligned MIDI for 79 solo-guitar performances.

Dataset media stays outside this repository and must not be redistributed/shipped.

## FLGD STAGE A — REAL INVENTORY COMPLETE / NO SCORING

Inventory preregistration:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`.

Frozen inventory tool:
`scripts/songsterr-fresh/inventory_flgd_v5_external_validation.py`.
It requires exact revision + canonical HF origin and performs hashing/metadata/header/pairing only; no sample-domain pitch analysis or model scoring.

One-shot real Stage A workflow:
`.github/workflows/songsterr-fresh-flgd-v5-real-inventory.yml`
source commit `77a0c8fddeecaf6e361e4c95772e2e80378258b9`.

Real run:
- workflow run `34719034991`
- job `103621353045`
- SUCCESS.

Immutable Stage A record:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`
commit `b536f5c5eb479689fdd0d4d949b2715175d712aa`.

Stage A report:
- report SHA-256 `f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`
- uploaded report-only artifact ID `10305947650`
- artifact ZIP digest `a7ea158d81c66589b24433991cb1effff8560c8decf44523e139b846bfbcce07`.

Observed selected checkout:
- 281 regular files
- 281,515,466 bytes
- `.csv` 1 / `.json` 79 / `.mid` 106 / `.mp3` 88 plus implementation/support files
- canonical `audio/`: 79 MP3
- canonical `midi/`: 79 MIDI
- exact canonical audio/MIDI leaf-stem pairs: 79
- ambiguous canonical pairs: 0
- unpaired canonical audio: 0
- unpaired canonical MIDI: 0.

`metadata.csv`:
- SHA-256 `05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b`
- 79 rows
- columns exactly `split,midi_filename,audio_filename,guitar_type,slice_id,artist,name`
- split domain `test,train,validate`
- guitar-type domain `acoustic,electric,electric-band,nylon`.

The checkout also contains noncanonical `test_set/` duplicates/model-output material. That material is forbidden as reference truth.

Stage A policy boundary remained exactly false/zero. **No FLGD correctness result exists yet.**

## FLGD STAGE B — MANIFEST / ANNOTATION SEMANTICS FROZEN GREEN

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MANIFEST_PREREGISTRATION.md`
commit `41b49d5f911ce27c6f1ca4834d56d4242a0e8b75`.

Frozen Stage B population rule:
- all and only the 79 root `metadata.csv` rows;
- every row binds exactly one canonical `audio/` + one canonical `midi/` file;
- `split` and `guitar_type` are strata metadata only, never inclusion/exclusion criteria;
- no row may be silently dropped;
- `test_set/` and model-output MIDI are forbidden as reference truth;
- syncpoint JSON is structural/timing metadata only and pairs mechanically by canonical stem;
- canonical MIDI only may be parsed for structural reference timing/event statistics;
- deterministic standard SMF PPQ + global tempo-map conversion is preregistered;
- note-on velocity zero is note-off; same-key overlap pairs FIFO; unmatched events fail closed;
- annotation duration statistics do not grant duration authority;
- no model inference, V5 classification, estimate/reference matching or correctness metric is authorized.

Implementation:
`scripts/songsterr-fresh/prepare_flgd_v5_stage_b_manifest.py`
commit `390916ca0df20b2163ac68f19ea595f3834a9b18`.

Synthetic contract test:
`scripts/songsterr-fresh/test_prepare_flgd_v5_stage_b_manifest.py`
commit `1713caf1aceaa0894bf3b4c19b2fdb089431aff9`.

Controlled workflow:
`.github/workflows/songsterr-fresh-flgd-v5-stage-b-ci.yml`
source commit `e050f42a2666ae9251b749ba678626abfa4499da`.

Controlled Stage B CI:
- run `34719339613`
- job `103622186675`
- SUCCESS.

The green contract verified compile, metadata/path bijection, canonical-only population, `test_set/` exclusion, syncpoint arities, MIDI running status, explicit/default tempo handling, overlapping same-key FIFO pairing, exact tick-to-second conversion, provenance/clean-worktree guards, malformed MIDI fail-closed behavior, frozen production identities, stdlib/non-scoring source boundary, and absence of real FLGD from CI.

Stage B output contract must contain exact population/reference-event hashes, metadata strata counts, syncpoint structure, MIDI timing semantics and event-count/range diagnostics with the same false/zero policy boundary.

## NEXT ALLOWED ACTION

Run **one real Stage B non-scoring manifest/timing pass** on the exact FLGD revision using the frozen Stage B tool. It may inspect metadata, file identities, syncpoint structure and canonical reference-MIDI annotation timing only.

It must not invoke Basic Pitch, V5, Demucs, audio-sample pitch analysis, estimate/reference matching or correctness metrics. Preserve the report outside repo initially, capture its SHA-256, and then write an immutable Stage B result record.

Only after real Stage B is immutably bound may a **separate final scoring preregistration** freeze Basic Pitch runtime/settings, V5 hashes, matching, uncertainty, minimum positives, pooled/stratum pass gates and provenance before any FLGD correctness run.

Then: controlled scoring-harness CI with no real correctness access → one official FLGD V5 correctness run → immutable result → separate policy review.

Until a later policy review explicitly approves V5:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration paused
- protected song embargoed.

## FRESH-CHAT RESUME

Read this file first and work only on `songsterr-fresh-pipeline-v1`.

V1–V4 are closed. V5 is active. V5 synthetic contract is green. FLGD Stage A real inventory is complete with no scoring. Stage B manifest/annotation-semantics implementation and controlled CI are frozen green. The next operation is one real Stage B non-scoring manifest/timing pass.

Do not rerun/tune GuitarSet or IDMT; do not use FLGD `test_set/` model outputs as truth; do not touch the protected song; do not resume duration, archived V143/Gomyway, GOAT, reference scoring, broad threshold sweeps or training/fine-tuning.

Keep this checkpoint updated at real Stage B result, scoring preregistration, scoring-harness CI, external result and policy review boundaries.

## STILL FORBIDDEN

- any FLGD V5 correctness run before separate final scoring preregistration + green scoring contract CI
- any post-hoc FLGD row selection based on correctness
- IDMT V4/GuitarSet rerun/tuning
- protected-song execution before future V5 external validation + policy approval
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps
- training/fine-tuning
- customer promotion without passing preregistered external validation and separate policy approval.
