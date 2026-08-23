# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Professional human reference is scorer-only. Runtime may never read/train/tune/select from it. Corrections after a holdout failure must stay general/reference-free. After accepting any correction, create a **brand-new approved-audio run/freeze/PDF identity before another professional score**.

Rhythm completion requires professional score >= `0.99`, critical mismatches = `0`, and PDF-event fidelity = `1.0`.

**Rhythm is NOT complete.**

## Protected runtime

Protected file: `analyzer/v143_reference_free_rhythm_pipeline.py`
Required exact blob: `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
Restore commit: `4ff233346b8dc7b80d8f4316fe1317338b5be718`

All shadow gates must prove this blob unchanged and Production unmodified.

## Approved fixture / old scored freeze

Approved audio: `public/gomywayfullaitest.m4a`
SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

Old scored freeze:
- 358 attacks; 1,017 rendered notes; 277 polyphonic attacks
- 112 populated measures of 1–113; missing measure 101
- event SHA256 `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- PDF-event fidelity `1.0`

Do **not** rescore this old freeze after tuning.

## Scorer-only reference / old holdout

Temporary local reference: `/mnt/data/scorer_workspace/validation/rhythm_holdout/reference/professional-rhythm-complete.json`
SHA256: `4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd`
Measures 1–113 contiguous; 577 playable onset objects; 925 playable note entries; 104 measures with playable attacks; completeness verifier passed. **Never commit it.**

Old holdout FAILED:
- pitchContentF1 `0.2626158599382081`
- pitchTimingTolerantF1 `0.07209062821833163`
- stringFretTimingTolerantF1 `0.030895983522142123`
- chordPitchSetTolerantF1 `0.0`
- exactVoicingTolerantF1 `0.0`
- measureCoverageRecall `0.9911504424778761`
- PDF-event fidelity `1.0`
- critical mismatches `1653`

General failure classes only: attack under-selection/measure loss; polyphony/harmonic inflation; broad pitch-position-timing mismatch. No song-specific runtime rule may come from the scorer/reference.

## Attack + pitch correction shadow

Files:
- `analyzer/v143_contextual_prune_shadow_correction.py`
- `analyzer/check_v143_contextual_prune_shadow_correction.py`
- `analyzer/v143_contextual_prune_shadow_correction_modal.py`
- `.github/workflows/v143-contextual-prune-shadow-correction-cpu.yml`
- `.github/workflows/v143-contextual-prune-shadow-correction-approved-audio.yml`

Conservative uncertainty fix: if the strongest pitch candidate itself fails independent two-view attack/body floors, preserve the entire observed pitch set; suppress secondaries only after the strongest pitch has positive physical support.
- code commit `2544c1c6da446bb6eaeaf96b6745757fce0a54a4`
- checker commit `b682d5ed6574866ec2ac175d6c72be13f9fc8fbd`

Current source-stamped CPU report `debug/v143-contextual-prune/shadow-correction-cpu.json` is GREEN:
- schema 2; passed true
- correction blob `3bcad86b67116cc6d50295f2937a7bf3602b41dd`
- checker blob `bfe37235938b33d2f36f4f9d6ef39ebabeeb57e7`
- synthetic base 2 / corrected 4 / rescued 2 / suppressed 1
- protected blob exact; token scan passed; Production unchanged

### First hardened approved-audio correction run — FAILED safely

Action now exists: `debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`

It proves the safety gates worked:
- schema 3
- trigger/checkout `f088337bef0811187b87e93265186f80336d8c2d`
- correction source blob `3bcad86b67116cc6d50295f2937a7bf3602b41dd`
- Modal runner blob `1ee6b81c5cc61dfea7d6ed927948896770db3ac0`
- timing-hypothesis blob `775a64aa5b561ddc643c5b970372298875451664`
- approved SHA exact
- protected pipeline exact
- reference-token scan passed
- Modal credentials available; shadow attempted
- Production/live endpoint unchanged

But `shadowExitCode=1` and `reportExists=false`.

Exact general failure:
`RuntimeError: Contextual-prune carrier grid incomplete: 1788 != 1808`

Diagnosis is label-free: the timing estimate starts inside measure 1 and ends inside measure 113. `1788` slots correspond to a valid first-measure suffix + full interior measures + last-measure prefix. The old carrier incorrectly required all 113 numbered measures to contain 16 slots, which would require inventing pre-audio/post-audio timing slots.

### Boundary-grid fix

`analyzer/v143_contextual_prune_reference_free_carrier.py` commit `9b0adba5cda329cccbee0b7eed58cd4f75277ee0`

New behavior:
- no synthetic boundary slots are added
- every interior requested measure must still contain all 16 steps
- first partial boundary must be a contiguous suffix ending at step 15
- last partial boundary must be a contiguous prefix starting at step 0
- all measures must exist; all steps valid/unique/contiguous
- single-measure partial captures remain allowed when internally contiguous
- protected runtime is untouched

This carrier change automatically retriggers the approved-audio correction shadow.

Dedicated proof:
- `analyzer/check_v143_contextual_prune_boundary_grid.py` commit `9dcda4aaa5871b29fa795448ed909653b8d37a6c`
- `.github/workflows/v143-contextual-prune-boundary-grid.yml` commit `649944ba729c396cfa2c3963147e3331cfba4883`
- synthetic approved-shape proof explicitly uses 1788 slots: measure 1 steps 12–15, measures 2–112 full, measure 113 steps 0–7
- malformed interior gap, invalid first/last boundary shape, and duplicate slot must fail
- CPU diagnostic pending

Do not accept the correction musically until a **new** approved-audio report is green.

## Approved-shadow physical review — CPU PASSED

Reusable scorer-free reviewer:
- `analyzer/v143_approved_shadow_physical_review.py` commit `68c13fb87b08b1eb949d4732650238d900e7fdfc`
- checker commit `2de96bca2f1298dff5221a761fb2c2602140088a`
- workflow commit `39263eedc06f7caffb42c4ca0917721c04586fb5`
- bot diagnostic commit `bc24a8aae6945fecfe9a7f63122836052a8b122b`
- report `debug/v143-contextual-prune/approved-shadow-physical-review.json` passed true
- protected blob exact; reference token scan passed; Production unchanged

It validates approved fixture/runtime/action safety, event-count reconciliation, unique observed rescues, non-decreasing coverage, no newly missing measures, suppression-only pitch changes, exact suppression counts, and non-mutating timing hypotheses. It deliberately does **not** decide musical correctness or use the professional reference.

## Semantic primary-note guard / sustain

Semantic CPU report `debug/v143-contextual-prune/rhythm-semantic-primary-note-guard.json` is green: event/timing/pitch/string/fret identity preserved while invalid secondary audio bend/legato ownership is removed; protected exact; Production unchanged.

Sustain CPU report `debug/v143-contextual-prune/rhythm-sustain-consensus-shadow.json` is green: two-view harmonic persistence writes only `rhythmSustainShadow`; no attack/pitch invention; no tie/let-ring inference; Production unchanged.

Approved semantics+sustain runner: `analyzer/v143_rhythm_semantics_sustain_approved_shadow_modal.py`, commit `cd0fec62bdd3b4da9ce7645db4d3582d528a2164`.

Approved workflow `.github/workflows/v143-rhythm-semantics-sustain-approved-shadow.yml`:
- race-safe/source-stamped `a7af569758c50c68a2dea6d59bc0804ec66562db`
- anti-leakage/protected-runtime hardened `6443b78a2a593734726499186ba4eeb58da2317f`

Expected action/report are still pending. Do not integrate semantics/sustain into routing until green.

## Timing diagnostics

Timing consistency shadow is green: `debug/v143-contextual-prune/rhythm-timing-consistency-shadow.json`.

Four-way phase + grid ambiguity shadow is green:
- module `2774a0421bc7f6781b5263d355f852c6dcf0f411`
- proof `70dab327ffdedf216c18de8fb5eb5c7ffb131fcc`
- workflow `57754a31de69a061563a96c7623f2dfcc74cb59f`
- Actions diagnostic `1fcf86c55e90ddf1c33846e43c982461d0de7af3`

It exposes four 4/4 phase hypotheses and grid ambiguity without selecting/changing phase, timing, attacks or pitch. Approved correction runner includes it as diagnostics only (`d3639460ca54d7b8a5710978469cbe44bf1ac35e`).

## Immediate next steps

1. Read the boundary-grid CPU diagnostic; require green.
2. Read the automatically retriggered approved correction action/report after the boundary-grid fix.
3. If green, run the scorer-free physical review against the real approved report and inspect only label-free correction/timing evidence.
4. Read the pending approved semantics+sustain action/report.
5. Accept only independently supported general/reference-free corrections.
6. Then create a **brand-new approved-audio analysis/freeze/PDF identity**.
7. Only then open the scorer-only professional reference for a new holdout.
8. Require >=0.99, zero critical mismatches, PDF-event fidelity 1.0 before Rhythm completion.
