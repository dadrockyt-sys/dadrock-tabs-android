# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-12 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT, reference/pro scoring, duration research, broad threshold/optimizer sweeps, training/fine-tuning remain closed unless explicitly reopened.
- Never silently alter/drop MIDI or event identity. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP work stays under `scripts/songsterr-fresh/`.
- Authority remains fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, persistent Policy C `UNENROLLED`.
- Protected song remains embargoed until a future V5 external-validation pass plus separate policy approval.

## HISTORICAL CLOSED LINES

V1/V2 are rejected research diagnostics. V3/GuitarSet and V4/IDMT are closed and contaminated for future untouched-holdout use. Do not rerun/tune them.

V4 final: 568/568 files, 7,619 decoded, 1,644 positive, 1,292 correct, precision `0.7858880778588808`, Wilson LB `0.7687844934184139` vs required `0.9900` → FAIL. Artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`. Result commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`; policy rejection `01a276045d32b643aa17013b959e89e41b0f305e`.

## V5 — ACTIVE / SYNTHETIC CONTRACT GREEN

User explicitly authorized V5 on 2026-09-12.

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`, commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.
Contract: `songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.

Implementation: `scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`, commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.
Frozen constants: mono 44.1 kHz; MIDI 40..88; 8192-sample windows at offsets 2048/8192/14336; FFT 32768; 8 harmonics; NNLS; RMS min `1e-4`; necessity fraction min `0.01`; fundamental/max-harmonic ratio min `0.05`; all 3 views required; NumPy 1.26.4; SciPy 1.15.3. No duration/end, confidence/activation, reference truth, performer/style/dataset identity or event rewriting.

20-case synthetic contract is green (`13 corroborated / 4 not / 3 insufficient`), including dyads/triads/six-note mixture/close dyad/dominant-harmonic cases and rejecting octave/semitone/temporal traps.

## FLGD HOLDOUT — FROZEN SOURCE

Selected untouched holdout: François Leduc Guitar Dataset.
- HF `xavriley/FrancoisLeducGuitarDataset`
- canonical origin `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- exact revision `a38306c244b3ea81496ad58b4514622185e58211`
- selected release declares MIT
- media stays outside app repo / must not be redistributed.

### Stage A — COMPLETE / NO SCORING

Real inventory run `34719034991`, job `103621353045`: SUCCESS.
Immutable Stage A record: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`, commit `b536f5c5eb479689fdd0d4d949b2715175d712aa`.
Report SHA-256 `f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`.

Observed: 79 canonical `audio/` MP3 + 79 canonical `midi/`, 79 exact pairs, zero ambiguous/unpaired. `metadata.csv` SHA `05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b`, 79 rows, columns `split,midi_filename,audio_filename,guitar_type,slice_id,artist,name`; split domain train/validate/test; guitar types acoustic/electric/electric-band/nylon. `test_set/` duplicates/model outputs are forbidden as reference truth. No correctness result exists.

### Stage B core — PREREGISTERED / CONTROLLED GREEN

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MANIFEST_PREREGISTRATION.md`, commit `41b49d5f911ce27c6f1ca4834d56d4242a0e8b75`.
Core tool: `scripts/songsterr-fresh/prepare_flgd_v5_stage_b_manifest.py`, commit `390916ca0df20b2163ac68f19ea595f3834a9b18`.
Controlled CI run `34719339613`, job `103622186675`: SUCCESS.

Population is all and only 79 root metadata rows; split/guitar_type are strata metadata only; no row may be silently dropped; canonical MIDI + syncpoints may be parsed structurally/timing-only; no Basic Pitch/V5/matching/correctness.

### First real Stage B attempt — FAIL-CLOSED STRUCTURAL ONLY

Workflow source `43b8ed6a15fe1fee792db9a20ed36d6baa08c5a6`; run `34719399752`, job `103622351601`.
It failed before producing any Stage B report:
`MIDI_UNMATCHED_NOTE_OFF:midi/Fp24c.mid:(0, 48):65091`.
No model inference or correctness result was produced.

### MIDI edge audit — COMPLETE / NO SCORING

Audit preregistration: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MIDI_EDGE_AUDIT_AMENDMENT.md`, commit `429d78ee222906a352bc2fccf720d08caa19ee76`.
Audit tool: `scripts/songsterr-fresh/audit_flgd_v5_midi_edges.py`, commit `4fb7c80b682ca9a3757b785c2e2ee3b3a81212f5`.
Controlled audit CI run `34719493782`, job `103622594786`: SUCCESS.
Real audit run `34719520796`, job `103622678813`: SUCCESS.
Audit report SHA `111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`; edge identity SHA `375029c7a0e2d80f25083743aa2d65c24c0de061f0e476db68987f218fcedef6`.

Audit result across all 79 canonical MIDIs:
- note messages `152808`
- note-ons `76392`
- note-offs `76416`
- valid FIFO pairs `76392`
- unmatched note-offs `24` in 7 files
- unmatched note-ons `0`
- same-key overlap `0`.
Every unmatched off occurs after the same `(channel,MIDI)` already completed a valid onset/release pair; none is a leading boundary release. These are structurally duplicate-release edges.

### Stage B pairing amendment — FROZEN / CONTROLLED GREEN

Pairing amendment: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MIDI_PAIRING_AMENDMENT.md`, commit `14ce641552d1d4304187299463fe7bf47a82593e`.
Official adapter: `scripts/songsterr-fresh/prepare_flgd_v5_stage_b_manifest_amended.py`, commit `26f38648634a1138da492e86e29af8084c705158`.
Controlled amendment CI run `34719672583`, job `103623078740`: SUCCESS.

Frozen amended pairing rule:
1. note-on velocity>0 opens FIFO;
2. note-off with active onset closes oldest onset and creates one event;
3. note-off with no active onset is ignored only if the same key already completed >=1 valid pair earlier in the same file;
4. such edges are identity-bound `ignored-duplicate-release` diagnostics and create no event;
5. leading orphan note-off still hard-fails;
6. unmatched note-on at EOF still hard-fails;
7. real frozen release must reproduce exactly `24` ignored duplicate releases or fail closed.

No file/metadata row is excluded. Audit report SHA is bound into Stage B output. This amendment is structural only and used no audio/model correctness.

## NEXT ALLOWED ACTION

Run one amended real Stage B non-scoring manifest/timing pass on exact FLGD revision. It must reproduce 79 performances and exactly 24 ignored duplicate releases, then output population/reference-event hashes and annotation/timing statistics with all policy flags false/zero.

After real Stage B is immutably bound, write a separate final scoring preregistration BEFORE any FLGD correctness run. That prereg must freeze Basic Pitch runtime/settings, V5 implementation/runtime hashes, exact matching, uncertainty, minimum positives, pooled/stratum gates and provenance. Then controlled scoring-harness CI (no real correctness) → one official FLGD V5 correctness run → immutable result → separate policy review.

## STILL FORBIDDEN

- any FLGD V5 correctness run before final scoring preregistration + green scoring contract CI
- post-hoc FLGD row selection based on correctness
- `test_set/` model outputs as truth
- GuitarSet/IDMT rerun/tuning
- protected-song execution before V5 passes external validation + policy approval
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps / training / fine-tuning
- customer promotion without passing preregistered external validation and separate policy approval.
