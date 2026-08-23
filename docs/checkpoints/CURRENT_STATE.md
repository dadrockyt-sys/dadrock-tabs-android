# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Non-negotiable boundary

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Professional human reference is scorer-only. Runtime may never read/train/tune/select from it. Any correction after a holdout failure must remain general/reference-free. After accepting any correction, create a **brand-new approved-audio run/freeze/PDF identity before another professional score**.

Rhythm completion requires:
- professional score >= `0.99`
- critical mismatches = `0`
- PDF-event fidelity = `1.0`

**Rhythm is NOT complete.**

## Protected runtime boundary

Protected file:
`analyzer/v143_reference_free_rhythm_pipeline.py`

Required exact blob:
`7f72f8ed9b14af8bc93e95544195204d99c6bec1`

Restore commit:
`4ff233346b8dc7b80d8f4316fe1317338b5be718`

All shadow gates must continue proving this blob unchanged and Production unmodified.

## Approved fixture / old scored freeze

Approved audio:
`public/gomywayfullaitest.m4a`

SHA256:
`215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

Old scored freeze:
- 358 attacks
- 1,017 rendered notes
- 277 polyphonic attacks
- 112 populated measures of 1–113
- missing measure 101
- event SHA256 `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- PDF-event fidelity `1.0`

Do **not** rescore this old freeze after tuning.

## Scorer-only reference

Local temporary reference:
`/mnt/data/scorer_workspace/validation/rhythm_holdout/reference/professional-rhythm-complete.json`

SHA256:
`4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd`

State:
- measures 1–113 contiguous
- 577 playable onset objects
- 925 playable note entries
- 104 measures with playable attacks
- completeness verifier PASSED

**Never commit this reference.**

## Real professional holdout — FAILED

Old freeze:
- `pitchContentF1 = 0.2626158599382081`
- `pitchTimingTolerantF1 = 0.07209062821833163`
- `stringFretTimingTolerantF1 = 0.030895983522142123`
- `chordPitchSetTolerantF1 = 0.0`
- `exactVoicingTolerantF1 = 0.0`
- `measureCoverageRecall = 0.9911504424778761`
- `pdfEventFidelity = 1.0`
- `criticalMismatchCount = 1653`

General failure classes only:
1. attack under-selection / measure loss
2. polyphony / harmonic inflation
3. broad pitch-position-timing mismatch

No song-specific runtime rules may come from the scorer/reference.

## Attack + pitch correction shadow

Files:
- `analyzer/v143_contextual_prune_shadow_correction.py`
- `analyzer/check_v143_contextual_prune_shadow_correction.py`
- `analyzer/v143_contextual_prune_shadow_correction_modal.py`
- `.github/workflows/v143-contextual-prune-shadow-correction-cpu.yml`
- `.github/workflows/v143-contextual-prune-shadow-correction-approved-audio.yml`

CPU proof is green:
`debug/v143-contextual-prune/shadow-correction-cpu.json`

Approved-audio output is still missing:
`debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`

Do not accept this correction musically until the approved-audio report is present and green.

## Semantic primary-note guard

Files:
- `analyzer/v143_rhythm_semantic_primary_note_guard.py`
- `analyzer/check_v143_rhythm_semantic_primary_note_guard.py`
- `.github/workflows/v143-rhythm-semantic-primary-note-guard.yml`

CPU report is green:
`debug/v143-contextual-prune/rhythm-semantic-primary-note-guard.json`

It proves event/timing/pitch/string/fret identity is preserved while secondary bend/legato ownership errors are removed. Protected pipeline exact; Production unchanged.

Not integrated into product routing yet.

## Sustain shadow

Files:
- `analyzer/v143_rhythm_sustain_consensus_shadow.py`
- `analyzer/check_v143_rhythm_sustain_consensus_shadow.py`
- `.github/workflows/v143-rhythm-sustain-consensus-shadow.yml`

CPU report is green:
`debug/v143-contextual-prune/rhythm-sustain-consensus-shadow.json`

The shadow uses two guitar-view harmonic persistence, writes only `rhythmSustainShadow`, never moves attacks/invents pitch, never infers tie/let-ring, and leaves Production unchanged.

## Approved-audio semantics + sustain

Modal runner:
`analyzer/v143_rhythm_semantics_sustain_approved_shadow_modal.py`

Runner commit:
`cd0fec62bdd3b4da9ce7645db4d3582d528a2164`

Workflow:
`.github/workflows/v143-rhythm-semantics-sustain-approved-shadow.yml`

Workflow commit:
`c4077eff19e1e720719fc0147c1625df49c5c32a`

Expected outputs still pending:
- `debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow-action.json`
- `debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow.json`

Do not integrate semantics/sustain into routing until approved-audio invariants pass.

## Timing diagnostics

Existing timing consistency shadow:
- `analyzer/v143_rhythm_timing_consistency_shadow.py`
- `analyzer/check_v143_rhythm_timing_consistency_shadow.py`
- `.github/workflows/v143-rhythm-timing-consistency-shadow.yml`
- green CPU report: `debug/v143-contextual-prune/rhythm-timing-consistency-shadow.json`

### Four-way phase + grid ambiguity shadow — CPU PASSED

Files:
- `analyzer/v143_rhythm_timing_hypothesis_shadow.py`
- `analyzer/check_v143_rhythm_timing_hypothesis_shadow.py`
- `.github/workflows/v143-rhythm-timing-hypothesis-shadow.yml`

Commits:
- module `2774a0421bc7f6781b5263d355f852c6dcf0f411`
- proof `70dab327ffdedf216c18de8fb5eb5c7ffb131fcc`
- workflow `57754a31de69a061563a96c7623f2dfcc74cb59f`
- GitHub Actions diagnostic `1fcf86c55e90ddf1c33846e43c982461d0de7af3`

Committed CPU report:
`debug/v143-contextual-prune/rhythm-timing-hypothesis-shadow.json`

Result:
- `passed=true`
- four phase hypotheses exposed without selecting/changing phase
- synthetic winner correctly matched current phase
- grid nearest-vs-runner-up ambiguity measured
- protected pipeline exact
- reference token scan passed
- Production unchanged

### Integrated into approved correction diagnostics only

`analyzer/v143_contextual_prune_shadow_correction_modal.py` now also computes:
- exact four-way reference-free beat-accent phase evidence
- current-winner match/separation/confidence
- strict grid-slot ambiguity margins

Integration commit:
`d3639460ca54d7b8a5710978469cbe44bf1ac35e`

No timing is changed. It is diagnostic-only.

Approved correction workflow was tightened to enforce timing-hypothesis invariants and `phaseSelectedOrChanged=false`:
commit `f9a89733c289ae7ad0943400a385817df41365c0`

This workflow push also retriggers the exact approved-audio correction shadow. Its report is pending.

## Existing production semantic path

`analyzer/v143_modal_live_endpoint.py` already applies bends then legato post-selection. Old output was therefore not technique-disabled. Any semantic changes must remain general/reference-free.

## Immediate next steps

1. Read the retriggered approved-audio attack/pitch correction action/report when committed.
2. Read the pending approved-audio semantics/sustain action/report.
3. Inspect approved-audio four-way phase evidence + strict grid ambiguity only as label-free diagnostics; do not change phase from scorer information.
4. If approved-audio invariants pass, decide corrections using only physical/reference-free evidence.
5. Only after independent acceptance, integrate general corrections and create a **brand-new approved-audio analysis/freeze/PDF identity**.
6. Then, and only then, run a new scorer-only professional holdout.
7. Require >=0.99, zero critical mismatches and PDF-event fidelity 1.0 before Rhythm completion.
