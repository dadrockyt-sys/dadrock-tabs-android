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
- 568/568 files; 7,619 decoded; 1,644 positives; 1,292 correct;
- precision `0.7858880778588808`;
- one-sided 95% Wilson LB `0.7687844934184139` vs required `0.9900` → FAIL;
- immutable artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`;
- result commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`;
- policy rejection commit `01a276045d32b643aa17013b959e89e41b0f305e`.

IDMT is historical/contaminated for successor holdout use.

## V5 — ACTIVE SUCCESSOR / SYNTHETIC CONTRACT GREEN

User explicitly authorized V5 on 2026-09-12 to address the prior failure mechanism.

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`
commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.

Contract:
`songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.

Actual frozen implementation constants:
- mono isolated guitar 44,100 Hz;
- existing onset + selected integer MIDI 40..88 only;
- three 8,192-sample post-onset windows at offsets `2048`, `8192`, `14336`;
- FFT `32768`;
- playable MIDI dictionary 40..88;
- harmonics 1..8, `1/h` weighting, normalized candidate templates;
- deterministic NNLS;
- minimum demeaned RMS `1e-4`;
- necessity fraction minimum `0.01`;
- selected fundamental / own max harmonic ratio minimum `0.05`;
- all three views must pass; no voting/fallback;
- NumPy `1.26.4`, SciPy `1.15.3`;
- no reference truth, duration/end, next onset, Basic Pitch confidence/activation, performer/style/dataset/bit-depth identity, or event rewriting.

Implementation:
`scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`
commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.

Synthetic fixtures:
`docs/checkpoints/SONGSTERR_FRESH_V5_SYNTHETIC_FIXTURES.json`
commit `efca2994efdce2c5a3b35d6e12fb9dc82096a268`.

Controlled V5 CI is green on the 20-case synthetic contract (`13 corroborated / 4 not / 3 insufficient`). This remains structural/synthetic progress only, not admission evidence.

Method record:
`docs/checkpoints/SONGSTERR_FRESH_POLYPHONIC_HARMONIC_NECESSITY_V5.md`.

## V5 EXTERNAL HOLDOUT — FLGD SELECTED

Frozen FLGD source:
- Hugging Face `xavriley/FrancoisLeducGuitarDataset`;
- canonical origin `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`;
- exact revision `a38306c244b3ea81496ad58b4514622185e58211`;
- selected release card declares MIT;
- 79 solo-guitar performances with aligned MIDI.

Dataset media stays outside this repository and must not be redistributed/shipped.

## FLGD STAGE A — REAL INVENTORY COMPLETE / NO SCORING

Inventory preregistration:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`.

Frozen inventory tool:
`scripts/songsterr-fresh/inventory_flgd_v5_external_validation.py`.

One-shot real workflow source commit `77a0c8fddeecaf6e361e4c95772e2e80378258b9`.
Real run `34719034991`, job `103621353045`: SUCCESS.

Immutable result:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`
commit `b536f5c5eb479689fdd0d4d949b2715175d712aa`.

Stage A report:
- report SHA-256 `f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`;
- artifact ID `10305947650`;
- artifact ZIP digest `a7ea158d81c66589b24433991cb1effff8560c8decf44523e139b846bfbcce07`.

Observed checkout:
- 281 regular files / 281,515,466 bytes;
- 79 canonical `audio/` MP3;
- 79 canonical `midi/` files;
- 79 exact canonical audio/MIDI pairs;
- zero ambiguous/unpaired canonical pairs;
- 79 `syncpoints/` JSON files.

`metadata.csv`:
- SHA-256 `05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b`;
- 79 rows;
- columns exactly `split,midi_filename,audio_filename,guitar_type,slice_id,artist,name`;
- split domain `test,train,validate`;
- guitar-type domain `acoustic,electric,electric-band,nylon`.

Noncanonical `test_set/` duplicates/model outputs exist and are forbidden as truth. Stage A policy remained false/zero. No FLGD correctness result exists.

## FLGD STAGE B — ORIGINAL CONTRACT GREEN, REAL PASS FAILED CLOSED

Original Stage B preregistration:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MANIFEST_PREREGISTRATION.md`
commit `41b49d5f911ce27c6f1ca4834d56d4242a0e8b75`.

Population remains all and only the 79 metadata rows; no row may be silently dropped. `split` and `guitar_type` are strata metadata only. `test_set/` and model-output MIDI are forbidden as truth. Syncpoints are structural/timing metadata only. Canonical MIDI uses deterministic standard SMF PPQ + global tempo-map conversion, note-on velocity zero as off, and FIFO same-key pairing.

Original implementation:
`scripts/songsterr-fresh/prepare_flgd_v5_stage_b_manifest.py`
commit `390916ca0df20b2163ac68f19ea595f3834a9b18`.

Original controlled Stage B CI:
- workflow source `e050f42a2666ae9251b749ba678626abfa4499da`;
- run `34719339613`;
- job `103622186675`;
- SUCCESS.

It verified synthetic metadata/path bijection, canonical-only population, `test_set/` exclusion, syncpoint arities, running status, explicit/default tempo, same-key FIFO pairing, exact tick-to-second conversion, provenance guards, malformed MIDI fail-closed behavior, stdlib/non-scoring source boundary, and absence of real FLGD.

First real Stage B attempt:
- one-shot workflow source `43b8ed6a15fe1fee792db9a20ed36d6baa08c5a6`;
- run `34719399752`;
- job `103622351601`;
- FAILED CLOSED before report output at `MIDI_UNMATCHED_NOTE_OFF:midi/Fp24c.mid:(0, 48):65091`.

No report was uploaded and no Basic Pitch/V5/audio analysis/matching/correctness result occurred.

## FLGD STAGE B — STRUCTURAL MIDI EDGE AUDIT COMPLETE

First amendment:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MIDI_EDGE_AUDIT_AMENDMENT.md`
commit `429d78ee222906a352bc2fccf720d08caa19ee76`.
It authorized structural MIDI edge audit only and explicitly required a second parser amendment before any real Stage B retry.

Audit tool:
`scripts/songsterr-fresh/audit_flgd_v5_midi_edges.py`
commit `4fb7c80b682ca9a3757b785c2e2ee3b3a81212f5`.

Controlled audit CI:
- source `d0409071a9e2a6a3f6f0830c5ea2cdaa29a1c177`;
- run `34719493782`;
- SUCCESS.

Real audit:
- workflow source `77ac002c34555ee35279bbdef2acb2bb1c7c1f56`;
- run `34719520796`;
- job `103622678813`;
- SUCCESS;
- report SHA-256 `111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`;
- edge identity SHA-256 `375029c7a0e2d80f25083743aa2d65c24c0de061f0e476db68987f218fcedef6`;
- artifact ID `10305342788`;
- artifact ZIP digest `3c140423b3e9add74d37d3f6d6b6be0f75efdd3d2c83ecff2e3a0c29e83f9355`.

Observed structural totals across all 79 canonical MIDI files:
- note messages `152808`;
- note-ons `76392`;
- note-offs `76416`;
- FIFO matched pairs `76392`;
- same-key overlaps `0`;
- unmatched note-ons `0`;
- unmatched note-offs `24` across exactly 7 files.

The seven files are:
`midi/Fp24c.mid`, `midi/SM54c.mid`, `midi/YNC4c.mid`, `midi/3H74c.mid`, `midi/hwC4c.mid`, `midi/LDC4c.mid`, `midi/MDC4c.mid`.

All 24 unmatched releases were structurally classified as duplicate-release candidates after earlier valid same-key on/off history; none were leading-boundary release candidates. No audio/model/correctness work occurred.

## FLGD STAGE B — DUPLICATE-RELEASE PARSER RULE FROZEN

Second amendment:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_DUPLICATE_RELEASE_RULE_AMENDMENT.md`
commit `2a2946df10611e90ca7b3839dbd2922cbded09b4`.

Frozen rule:
- same merged order `(tick, trackIndex, eventOrder)` and FIFO pairing remain;
- maintain a completed-pair count for each exact `(channel, MIDI)` key;
- an off with an active onset pairs normally and increments that key’s completed-pair count;
- an off with no active onset is accepted only if that exact key already has at least one completed pair, and is classified as an explicit `duplicateReleaseEdge`;
- such an edge creates no second reference note and alters no paired note identity;
- every accepted duplicate edge must remain explicitly represented with exact message identity and deterministic per-file/global SHA-256 identity hashes;
- an unmatched release before any completed pair remains fatal `MIDI_UNMATCHED_NOTE_OFF_BEFORE_MATCHED_PAIR`;
- any unmatched onset at EOF remains fatal `MIDI_UNMATCHED_NOTE_ON`;
- all 79 rows remain mandatory; no correctness-based row exclusion is authorized.

This amendment is structural only and was frozen before any FLGD correctness result.

## NEXT ALLOWED ACTION

Implement the frozen duplicate-release rule in the Stage B parser, extend the synthetic contract so it proves:
- valid pair + extra release is retained explicitly as one `duplicateReleaseEdge` while producing only the original paired note event;
- leading unmatched release still fails closed;
- trailing unmatched onset still fails closed;
- existing tempo/running-status/FIFO/canonical-population/provenance/non-scoring guards remain green.

Then run controlled Stage B CI **without real FLGD correctness access**. Only if that amended synthetic contract is green may one new real Stage B non-scoring manifest/timing pass be attempted on the exact FLGD revision.

Do not rerun the real Stage B pass until the amended parser + synthetic CI are green.

Only after a successful real Stage B report is immutably bound may a separate final scoring preregistration freeze Basic Pitch runtime/settings, V5 hashes, estimate/reference matching, uncertainty, minimum positives, pooled/stratum gates and provenance before any correctness run.

Until a later policy review explicitly approves V5:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration paused;
- protected song embargoed.

## FRESH-CHAT RESUME

Read this file first and work only on `songsterr-fresh-pipeline-v1`.

V1–V4 are closed. V5 is active. V5 synthetic contract is green. FLGD Stage A is complete. Original Stage B real pass failed closed on an unmatched release before producing a report. A preregistered structural audit found 24 duplicate-release edges across 7 files, zero unmatched onsets and zero same-key overlaps. The deterministic duplicate-release parser amendment is frozen. The next work is **implementation + controlled synthetic CI only**; no real Stage B retry yet.

Do not rerun/tune GuitarSet or IDMT; do not use FLGD `test_set/` model outputs as truth; do not touch the protected song; do not resume duration, archived V143/Gomyway, GOAT, reference scoring, broad threshold sweeps or training/fine-tuning.

Keep this checkpoint updated at amended Stage B CI, successful real Stage B result, scoring preregistration, scoring-harness CI, external result and policy-review boundaries.

## STILL FORBIDDEN

- real FLGD Stage B retry before amended synthetic CI is green;
- any FLGD V5 correctness run before separate final scoring preregistration + green scoring contract CI;
- any post-hoc FLGD row selection based on correctness;
- IDMT V4/GuitarSet rerun/tuning;
- protected-song execution before future V5 external validation + policy approval;
- duration research;
- archived V143/Gomyway / GOAT / reference scoring;
- broad threshold sweeps;
- training/fine-tuning;
- customer promotion without passing preregistered external validation and separate policy approval.
