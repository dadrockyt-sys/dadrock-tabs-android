# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Non-negotiable boundary

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Professional human reference is scorer-only. Runtime may never read/train/tune/select from it. Musical corrections after a holdout failure must remain general/reference-free. After accepting any correction, create a **brand-new approved-audio run/freeze/PDF identity before another professional score**.

Rhythm completion requires all of:
- professional score >= `0.99`
- critical mismatches = `0`
- PDF-event fidelity = `1.0`

**Rhythm is NOT complete. No completion claim is authorized.**

## Protected runtime boundary

Protected file:
`analyzer/v143_reference_free_rhythm_pipeline.py`

Required exact blob:
`7f72f8ed9b14af8bc93e95544195204d99c6bec1`

Restore commit:
`4ff233346b8dc7b80d8f4316fe1317338b5be718`

Current correction, semantic, sustain and timing CPU gates must continue proving this blob unchanged and Production unmodified.

## Approved audio / old frozen score identity

Approved fixture:
`public/gomywayfullaitest.m4a`

SHA256:
`215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

Old scored freeze:
- 358 attacks
- 1,017 rendered notes
- 277 polyphonic attacks
- 112 populated measures of 1–113
- missing generated measure 101
- event SHA256 `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- PDF-event fidelity `1.0`
- presentation run `32643978196`, artifact `9494412019`

Do **not** rescore this old freeze after tuning.

## Scorer-only human reference

Temporary local scorer reference:
`/mnt/data/scorer_workspace/validation/rhythm_holdout/reference/professional-rhythm-complete.json`

SHA256:
`4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd`

State:
- measures 1–113 contiguous
- 577 playable onset objects
- 925 playable note entries
- 104 measures with playable attacks
- uncertain semantics omitted rather than invented
- completeness verifier PASSED

**Never commit this reference.**

## Real professional holdout — FAILED

Old freeze results:
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

No song-specific runtime rule may be derived from this score/reference.

## Attack + pitch correction shadow

Files:
- `analyzer/v143_contextual_prune_shadow_correction.py`
- `analyzer/check_v143_contextual_prune_shadow_correction.py`
- `analyzer/v143_contextual_prune_shadow_correction_modal.py`
- `.github/workflows/v143-contextual-prune-shadow-correction-cpu.yml`
- `.github/workflows/v143-contextual-prune-shadow-correction-approved-audio.yml`

CPU/static proof is green:
`debug/v143-contextual-prune/shadow-correction-cpu.json`

It proves base-event preservation, strict physical rescue, unsupported-harmonic suppression, protected pipeline blob exact, reference token scan passed and Production unchanged.

Approved-audio correction output is still missing:
`debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`

Do not accept the correction musically until the exact approved-audio report exists and passes invariants.

## Semantic primary-note ownership guard

Files:
- `analyzer/v143_rhythm_semantic_primary_note_guard.py`
- `analyzer/check_v143_rhythm_semantic_primary_note_guard.py`
- `.github/workflows/v143-rhythm-semantic-primary-note-guard.yml`

General bug fixed in isolation: bend/legato semantics must belong to mapper-designated `noteMapping.primaryTechniqueNote`; secondary chord tones must not inherit audio-derived primary semantics.

CPU gate is green:
`debug/v143-contextual-prune/rhythm-semantic-primary-note-guard.json`

Result:
- `passed=true`
- event count/timing/pitch/string/fret unchanged
- secondary bend/legato and invalid primary legato stripped in synthetic proof
- reference token scan passed
- protected pipeline exact
- Production unchanged

Not integrated into product routing yet.

## Sustain/duration shadow

Files:
- `analyzer/v143_rhythm_sustain_consensus_shadow.py`
- `analyzer/check_v143_rhythm_sustain_consensus_shadow.py`
- `.github/workflows/v143-rhythm-sustain-consensus-shadow.yml`

Design:
- two independent guitar-view harmonic persistence
- bounded by next authenticated attack on the same string / max sustain
- annotates only `rhythmSustainShadow`
- never moves attacks or invents pitch
- never infers tie/let-ring labels
- does not overwrite production sustain

CPU gate is green:
`debug/v143-contextual-prune/rhythm-sustain-consensus-shadow.json`

Result:
- `passed=true`
- synthetic two-view proof recovers sustain longer than short detector duration
- event count/timing/pitch unchanged
- no tie/let-ring inference
- protected pipeline exact
- Production unchanged

## Approved-audio semantics + sustain shadow

Modal runner:
`analyzer/v143_rhythm_semantics_sustain_approved_shadow_modal.py`

Runner commit:
`cd0fec62bdd3b4da9ce7645db4d3582d528a2164`

Workflow:
`.github/workflows/v143-rhythm-semantics-sustain-approved-shadow.yml`

Workflow commit:
`c4077eff19e1e720719fc0147c1625df49c5c32a`

It SHA-gates the approved fixture, runs reference-free rhythm assembly → bends → legato → semantic guard → sustain shadow, commits diagnostics, and enforces core-event identity plus no Production/live-route mutation.

Expected outputs are still pending:
- `debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow-action.json`
- `debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow.json`

Do not integrate semantic guard or sustain shadow until these approved-audio outputs are green.

## Timing diagnostics

Existing observational timing consistency files:
- `analyzer/v143_rhythm_timing_consistency_shadow.py`
- `analyzer/check_v143_rhythm_timing_consistency_shadow.py`
- `.github/workflows/v143-rhythm-timing-consistency-shadow.yml`

CPU gate is green:
`debug/v143-contextual-prune/rhythm-timing-consistency-shadow.json`

It proves residual/repeated-structure diagnostics are label-free and do not change tempo, phase, attack timing, candidate selection, pitch or Production.

### New four-way phase + grid-ambiguity shadow

Added:
- `analyzer/v143_rhythm_timing_hypothesis_shadow.py` — commit `2774a0421bc7f6781b5263d355f852c6dcf0f411`
- `analyzer/check_v143_rhythm_timing_hypothesis_shadow.py` — commit `70dab327ffdedf216c18de8fb5eb5c7ffb131fcc`
- `.github/workflows/v143-rhythm-timing-hypothesis-shadow.yml` — commit `57754a31de69a061563a96c7623f2dfcc74cb59f`

New shadow behavior:
- exposes all four 4/4 accent hypotheses using the same reference-free beat-accent concept as timing
- reports winner/runner-up separation and confidence but **does not select/change phase**
- measures nearest-vs-runner-up grid-slot margins and strict-row ambiguity
- never changes tempo, phase, attacks, candidate selection or pitch
- no scorer/reference input
- Production unchanged

Expected CPU report is pending:
`debug/v143-contextual-prune/rhythm-timing-hypothesis-shadow.json`

Do not integrate this diagnostic into approved-audio timing evaluation until its CPU gate is green.

## Existing production semantic path

`analyzer/v143_modal_live_endpoint.py` already applies post-selection:
1. `enrich_router_assembly_with_consensus_bends`
2. `enrich_router_assembly_with_legato`

So old output was not technique-disabled. Any semantic improvement must remain general/reference-free.

## Immediate next steps

1. Read the pending timing-hypothesis CPU report when GitHub Actions commits it.
2. Read the pending approved-audio semantics/sustain action/report.
3. Continue checking the still-missing approved-audio attack-correction action/report.
4. If timing-hypothesis CPU is green, integrate **diagnostics only** into an approved-audio shadow so four-way phase confidence + grid ambiguity can be inspected without changing timing.
5. Evaluate all approved-audio corrections only by label-free invariants/counts/evidence before any new holdout.
6. Only after independently accepting general corrections, integrate them and create a **brand-new approved-audio analysis/freeze/PDF identity**.
7. Then, and only then, run a new scorer-only professional holdout.
8. Require >=0.99, zero critical mismatches and PDF-event fidelity 1.0 before Rhythm completion.
