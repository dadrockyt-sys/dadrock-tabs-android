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

### Conservative pitch-suppression safety fix

A general uncertainty bug was found by source inspection: `_supported_pitch_set()` could collapse an uncertain multi-pitch base event to one relative winner even when the strongest candidate itself failed independent two-view attack/body support.

Fixed behavior:
- if the strongest candidate fails the physical floors, preserve the entire original observed pitch set
- suppress secondary pitches only when the strongest pitch itself has positive independent two-view evidence
- no attack/timing/string/fret/Production behavior changes

Code commit:
`2544c1c6da446bb6eaeaf96b6745757fce0a54a4`

Checker commit:
`b682d5ed6574866ec2ac175d6c72be13f9fc8fbd`

### Current correction CPU gate — PASSED on the new source

Current source-stamped report:
`debug/v143-contextual-prune/shadow-correction-cpu.json`

Result:
- `schemaVersion=2`
- `passed=true`
- checked-out commit `d1a50efc2ffb640068f4c8bf72b4c0bb1f42b7ee`
- correction source blob `3bcad86b67116cc6d50295f2937a7bf3602b41dd`
- checker source blob `bfe37235938b33d2f36f4f9d6ef39ebabeeb57e7`
- Modal runner blob `1ee6b81c5cc61dfea7d6ed927948896770db3ac0`
- synthetic `baseEventCount=2`, confirming the new unsupported two-pitch preservation case actually ran
- `correctedEventCount=4`
- `rescuedEventCount=2`
- `suppressedPitchCount=1`
- reference token scan passed
- protected pipeline blob exact `7f72...`
- Production unchanged

So the conservative uncertainty fix is CPU-proven. Later workflow-only commits do not alter these source blobs.

### Diagnostic freshness / branch-race / anti-leakage hardening

Long-running workflows could previously fail their final diagnostic push when checkpoint/code commits advanced the branch during Modal execution. Diagnostic workflows are now source-stamped and use fetch/rebase-before-push so current work can continue without losing results.

CPU workflow:
- source stamping commit `d1a50efc2ffb640068f4c8bf72b4c0bb1f42b7ee`
- rebase-before-push commit `b7b0e7bb04923c54f37c2376b83776d5123be20c`

Approved correction workflow:
- `.github/workflows/v143-contextual-prune-shadow-correction-approved-audio.yml`
- race-safe/source-stamped commit `9d5315abc3e6535403059bb399e33437ee23c46b`
- hardened anti-leakage/protected-runtime commit `f088337bef0811187b87e93265186f80336d8c2d`
- action schema 3 records checked-out commit, correction/Modal/timing-hypothesis source blobs, protected pipeline blob, and reference-token-scan state
- refuses to run if the protected pipeline is not exact or if scorer/reference tokens are found in correction/timing sources
- fetches/rebases latest branch before diagnostic push
- still enforces approved fixture identity, non-mutating timing diagnostics, reference-free behavior and no Production/live changes

Approved-audio output remains pending:
`debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`

Do not accept the attack/pitch correction musically until the approved-audio report is present and green.

## Semantic primary-note guard

Files:
- `analyzer/v143_rhythm_semantic_primary_note_guard.py`
- `analyzer/check_v143_rhythm_semantic_primary_note_guard.py`
- `.github/workflows/v143-rhythm-semantic-primary-note-guard.yml`

Existing CPU report is green:
`debug/v143-contextual-prune/rhythm-semantic-primary-note-guard.json`

It proves event/timing/pitch/string/fret identity is preserved while secondary bend/legato ownership errors are removed. Protected pipeline exact; Production unchanged.

Not integrated into product routing yet.

## Sustain shadow

Files:
- `analyzer/v143_rhythm_sustain_consensus_shadow.py`
- `analyzer/check_v143_rhythm_sustain_consensus_shadow.py`
- `.github/workflows/v143-rhythm-sustain-consensus-shadow.yml`

Existing CPU report is green:
`debug/v143-contextual-prune/rhythm-sustain-consensus-shadow.json`

The shadow uses two guitar-view harmonic persistence, writes only `rhythmSustainShadow`, never moves attacks/invents pitch, never infers tie/let-ring, and leaves Production unchanged.

## Approved-audio semantics + sustain

Modal runner:
`analyzer/v143_rhythm_semantics_sustain_approved_shadow_modal.py`

Runner commit:
`cd0fec62bdd3b4da9ce7645db4d3582d528a2164`

Workflow:
`.github/workflows/v143-rhythm-semantics-sustain-approved-shadow.yml`

Original workflow commit:
`c4077eff19e1e720719fc0147c1625df49c5c32a`

Race-safe/source-stamped commit:
`a7af569758c50c68a2dea6d59bc0804ec66562db`

Hardened anti-leakage/protected-runtime commit:
`6443b78a2a593734726499186ba4eeb58da2317f`

Current workflow behavior:
- action schema 3 records trigger SHA, checked-out commit, runner/guard/sustain source blobs, protected pipeline blob, and reference-token-scan state
- refuses to run if approved fixture SHA changes, protected Rhythm pipeline blob changes, or scorer/reference tokens appear in the semantics/sustain shadow sources
- fetches/rebases latest branch before pushing diagnostics
- retains event-identity, semantic-ownership, sustain, reference-free and no-Production invariants

Expected outputs are pending:
- `debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow-action.json`
- `debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow.json`

Do not integrate semantics/sustain into routing until approved-audio invariants pass.

## Timing diagnostics

Existing timing consistency shadow is green:
`debug/v143-contextual-prune/rhythm-timing-consistency-shadow.json`

### Four-way phase + grid ambiguity shadow — CPU PASSED

Files:
- `analyzer/v143_rhythm_timing_hypothesis_shadow.py`
- `analyzer/check_v143_rhythm_timing_hypothesis_shadow.py`
- `.github/workflows/v143-rhythm-timing-hypothesis-shadow.yml`

Commits:
- module `2774a0421bc7f6781b5263d355f852c6dcf0f411`
- proof `70dab327ffdedf216c18de8fb5eb5c7ffb131fcc`
- workflow `57754a31de69a061563a96c7623f2dfcc74cb59f`
- green Actions diagnostic `1fcf86c55e90ddf1c33846e43c982461d0de7af3`

Report:
`debug/v143-contextual-prune/rhythm-timing-hypothesis-shadow.json`

It exposes all four 4/4 accent hypotheses and nearest-vs-runner-up grid ambiguity without selecting/changing phase, timing, attacks or pitches. Protected pipeline exact; no reference; Production unchanged.

Approved correction Modal runner includes these diagnostics only:
commit `d3639460ca54d7b8a5710978469cbe44bf1ac35e`

## Existing production semantic path

`analyzer/v143_modal_live_endpoint.py` already applies bends then legato post-selection. Old output was not technique-disabled. Any semantic changes must remain general/reference-free.

## Immediate next steps

1. Read the hardened race-safe approved-audio attack/pitch correction action/report when committed.
2. Read the hardened race-safe approved-audio semantics/sustain action/report when committed.
3. Inspect approved-audio four-way phase evidence + strict grid ambiguity only as label-free diagnostics; do not change phase from scorer information.
4. If approved-audio invariants pass, decide corrections using only physical/reference-free evidence.
5. Only after independent acceptance, integrate general corrections and create a **brand-new approved-audio analysis/freeze/PDF identity**.
6. Then, and only then, run a new scorer-only professional holdout.
7. Require >=0.99, zero critical mismatches and PDF-event fidelity 1.0 before Rhythm completion.
