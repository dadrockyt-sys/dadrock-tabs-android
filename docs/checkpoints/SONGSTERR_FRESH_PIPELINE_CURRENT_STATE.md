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

20-case synthetic contract is green (`13 corroborated / 4 not / 3 insufficient`). Synthetic success is not admission evidence.

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

Observed: 79 canonical `audio/` MP3 + 79 canonical `midi/`, 79 exact pairs, zero ambiguous/unpaired. `metadata.csv` SHA `05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b`, 79 rows, columns `split,midi_filename,audio_filename,guitar_type,slice_id,artist,name`; split domain train/validate/test; guitar types acoustic/electric/electric-band/nylon. `test_set/` duplicates/model outputs are forbidden as reference truth. No correctness result exists at Stage A.

### Stage B first attempt — FAILED CLOSED / STRUCTURAL ONLY

Original preregistration: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MANIFEST_PREREGISTRATION.md`, commit `41b49d5f911ce27c6f1ca4834d56d4242a0e8b75`.
Original controlled CI run `34719339613`, job `103622186675`: SUCCESS.

First real Stage B source `43b8ed6a15fe1fee792db9a20ed36d6baa08c5a6`; run `34719399752`, job `103622351601`. It failed before any report at `MIDI_UNMATCHED_NOTE_OFF:midi/Fp24c.mid:(0, 48):65091`. No model inference or correctness result was produced.

### Structural MIDI edge audit — COMPLETE / NO SCORING

Audit preregistration: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MIDI_EDGE_AUDIT_AMENDMENT.md`, commit `429d78ee222906a352bc2fccf720d08caa19ee76`.
Audit tool: `scripts/songsterr-fresh/audit_flgd_v5_midi_edges.py`, commit `4fb7c80b682ca9a3757b785c2e2ee3b3a81212f5`.
Controlled audit CI run `34719493782`: SUCCESS.
Real audit run `34719520796`, job `103622678813`: SUCCESS.
Audit report SHA `111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`; edge identity SHA `375029c7a0e2d80f25083743aa2d65c24c0de061f0e476db68987f218fcedef6`.

Audit totals across all 79 canonical MIDIs:
- note messages `152808`
- note-ons `76392`
- note-offs `76416`
- valid FIFO pairs `76392`
- unmatched note-offs `24` in 7 files
- unmatched note-ons `0`
- same-key overlap `0`.

Every unmatched off occurred only after the same `(channel,MIDI)` had already completed a valid pair; none was a leading-boundary release. No audio/model/correctness work occurred.

### Stage B pairing amendment — FROZEN / CONTROLLED GREEN

Authoritative pairing amendment: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MIDI_PAIRING_AMENDMENT.md`, commit `14ce641552d1d4304187299463fe7bf47a82593e`.
Official adapter: `scripts/songsterr-fresh/prepare_flgd_v5_stage_b_manifest_amended.py`, commit `26f38648634a1138da492e86e29af8084c705158`.
Controlled amendment CI run `34719672583`, job `103623078740`: SUCCESS.

Frozen rule: close FIFO normally when active; an off with no active onset is `ignored-duplicate-release` only after that exact key has already completed a valid pair; leading orphan off and trailing unmatched on still fail. Exact real release is required to reproduce 24 such diagnostics. No file/metadata row is excluded.

### Stage B official real result — COMPLETE / IMMUTABLE / NO SCORING

Official one-shot workflow: `.github/workflows/songsterr-fresh-flgd-v5-real-stage-b-attempt2.yml`.
Source commit `ac57c6c5379f00ad97c292415efec90c9ed32860`.
Run `34719744595`, job `103623274603`: SUCCESS.

Immutable result record:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_RESULT.md`
commit `0bc647b112745953464f24eb0980e49ff348ebb2`.

Frozen Stage B identities:
- report SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`
- included-population SHA-256 `def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02`
- reference-event identity SHA-256 `e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a`
- ignored-duplicate-release identity SHA-256 `8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3`
- bound edge-audit report SHA `111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`
- report-only artifact ID `10305323053`
- artifact ZIP digest `138ce6006e7391d65729be0d83758d6f033156336938c985e55142f91d96aa18`.

Frozen population/annotation structure:
- all 79 metadata rows included; no post-hoc exclusions
- split counts: train 62 / validate 8 / test 9
- guitar types: nylon 40 / electric 35 / acoustic 3 / electric-band 1
- reference note events `76392`
- ignored audited duplicate releases exactly `24`
- all MIDI format 1, two tracks, PPQ 220
- tempo domain 500000 us/qn only
- channel domain `[0]`
- same-key overlap `0`
- MIDI range `38..88`
- onset range `0.03409090909090909..408.5068181818182` s
- offset range `0.33636363636363636..413.84090909090907` s
- annotation-duration range `0.004545454545450411..14.513636363636351` s
- syncpoint arity-2 points `1832`; arity-3 points `20543`.

All Stage B policy fields were false/zero. No Basic Pitch, V5 classification, estimate/reference matching, correctness metric, duration-authority change, or protected-song use occurred. **FLGD correctness remains unseen.**

### Post-result parity hardening — NON-AUTHORITATIVE FOR THE FROZEN STAGE B RESULT

A concurrent workstream landed after official Stage B source `ac57c6c...`:
- `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_DUPLICATE_RELEASE_RULE_AMENDMENT.md`, commit `2a2946df10611e90ca7b3839dbd2922cbded09b4`;
- core Stage B V2 parity implementation commit `06503a273eb739acc5769c20be233838e46ba294`;
- synthetic parity test commit `1528353982a85e0b8995a9d0d45b9d90541c54c3`;
- controlled CI run `34719785171`, job `103623386765`: SUCCESS.

Those later commits independently encode the same audit-derived duplicate-release principle and are useful hardening, but they landed after the official real Stage B execution. They **do not retroactively redefine, replace, or require rerunning** the immutable Stage B result above. The authoritative Stage B result remains the adapter/run/report identities frozen in `SONGSTERR_FRESH_FLGD_V5_STAGE_B_RESULT.md`.

## NEXT ALLOWED ACTION — FINAL SCORING PREREGISTRATION ONLY

Do **not** rerun Stage B. The next permitted work is a separate final FLGD V5 scoring preregistration, written and frozen before any FLGD Basic Pitch/V5 correctness execution.

That preregistration must bind the exact Stage B result/population identities above and freeze, before correctness is observed:
- exact audio decoding/resampling/mono contract;
- exact Basic Pitch package/model/runtime/settings and raw estimate identity representation;
- exact V5 implementation/runtime/settings and which estimates are eligible for V5 evaluation;
- exact estimate-to-reference matching rule using onset + MIDI only (no duration authority leakage);
- uncertainty/abstention handling;
- minimum evaluated/positive sample requirements;
- pooled and preregistered stratum pass/fail gates;
- deterministic provenance/output hashes;
- one-off official execution semantics and fail-closed policy boundary.

After preregistration: implement scoring harness → controlled synthetic/contract CI with no real FLGD correctness access → one official FLGD V5 correctness run → immutable result → separate policy review.

Until the separate policy review explicitly approves V5:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration remains paused
- protected song remains embargoed.

## STILL FORBIDDEN

- another FLGD Stage B real run unless a new explicit structural amendment requires it
- any FLGD V5 correctness run before final scoring preregistration + green scoring contract CI
- post-hoc FLGD row selection based on correctness
- `test_set/` model outputs as truth
- GuitarSet/IDMT rerun/tuning
- protected-song execution before V5 passes external validation + policy approval
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps / training / fine-tuning
- customer promotion without passing preregistered external validation and separate policy approval.
