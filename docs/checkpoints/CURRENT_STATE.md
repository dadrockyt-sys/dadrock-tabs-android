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

## Boundary-grid fix — GREEN

The first hardened approved correction run failed safely because the research carrier required `113 * 16 = 1808` slots even though the approved audio begins inside measure 1 and ends inside measure 113. The physically valid timing grid has 1788 slots.

Carrier fix:
- `analyzer/v143_contextual_prune_reference_free_carrier.py`
- commit `9b0adba5cda329cccbee0b7eed58cd4f75277ee0`
- no synthetic boundary timing slots
- full 16-step interior measures remain mandatory
- first partial boundary must be a contiguous suffix ending step 15
- last partial boundary must be a contiguous prefix starting step 0

Dedicated proof is now GREEN:
`debug/v143-contextual-prune/boundary-grid.json`
- trigger/checkout `5840db2af5e8cfe230ff09f364f1616d57fd57a0`
- carrier blob `99866aa8af14dc243d226c6fb28d68af14d003ac`
- checker blob `422efbc4c9eac8bd78b67e23102e97d8801491f1`
- exact approved shape: measure 1 steps 12–15, measures 2–112 full, measure 113 steps 0–7
- grid count 1788
- no synthetic boundary slots
- token scan passed; protected pipeline exact; Production unchanged

## Attack + pitch correction shadow — approved audio GREEN

Files:
- `analyzer/v143_contextual_prune_shadow_correction.py`
- `analyzer/check_v143_contextual_prune_shadow_correction.py`
- `analyzer/v143_contextual_prune_shadow_correction_modal.py`
- `.github/workflows/v143-contextual-prune-shadow-correction-cpu.yml`
- `.github/workflows/v143-contextual-prune-shadow-correction-approved-audio.yml`

Conservative uncertainty rule remains: if the strongest pitch candidate fails independent two-view attack/body floors, preserve the entire observed pitch set; suppress secondaries only after the strongest pitch itself has positive physical support.

CPU proof remains GREEN with correction blob `3bcad86b67116cc6d50295f2937a7bf3602b41dd` and checker blob `bfe37235938b33d2f36f4f9d6ef39ebabeeb57e7`.

Fresh approved-audio action is GREEN:
`debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`
- trigger/checkout `9b0adba5cda329cccbee0b7eed58cd4f75277ee0`
- schema 3
- approved SHA exact
- protected pipeline exact
- reference-token scan passed
- Modal credentials present
- shadow attempted; exit code 0
- report exists
- no professional reference/runtime labels/live deployment/Production modification

Fresh approved report:
`debug/v143-contextual-prune/shadow-correction-approved-audio.json`

Physical/reference-free result:
- carrier rows 5,484; grid 1,788; raw detector events 143,902
- contextual base selector: 1,116 base events → 949 candidate attacks
- correction: 949 → 979 attacks via 30 strict physically observed local-peak rescues
- all 113 measures populated before and after correction
- original observed pitch hypotheses: 10,686 total, mean 10.915/event, max 33
- corrected supported pitch hypotheses: 2,055 total, mean 2.099/event, max 8
- 959 events changed only by suppression; 8,631 candidate pitches suppressed
- events with >=5 pitches: 884 → 41
- events with >=6 pitches: 833 → 14
- base events preserved; no event relocation; no invented pitch
- timing diagnostics do not mutate tempo/phase/attacks/pitch

Timing evidence:
- tempo `129.19921875`
- first beat in measure `3`; downbeat index mod4 `1`
- current four-way phase is the label-free winner but confidence is low: `0.08797339512490407`
- strict residual median ~27.3 ms; ~99.65% within 60 ms
- strict grid ambiguity fraction within 20 ms ~15.97%
- phase was **not** selected/changed by the diagnostic

## Real approved correction physical review — GREEN

Reusable scorer-free reviewer:
- `analyzer/v143_approved_shadow_physical_review.py`
- reviewer source blob `c8025ee99596354d731628b57e42f69e0ca39c10`

Checker was extended to validate the real approved action/report in addition to synthetic tamper cases:
- commit `670fb25b9177f1483abe0efca2fd1781a89e3cb8`
- checker blob `e2facac5a63d49af05bd85f4bcf05625113284cf`

Current diagnostic:
`debug/v143-contextual-prune/approved-shadow-physical-review.json`
- trigger/checkout `670fb25b9177f1483abe0efca2fd1781a89e3cb8`
- passed true
- real metrics: base 949 / corrected 979 / rescued 30 / suppressed pitches 8,631
- all 113 measures remain populated
- 959 pitch-changed events reconcile exactly
- phase winner matches current; no phase mutation
- professional reference not used
- protected pipeline exact; Production unchanged

This establishes internal physical/safety consistency. It is **not** yet a professional score and does not claim musical correctness.

## Semantic primary-note guard + sustain — approved audio GREEN

Approved action:
`debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow-action.json`
- schema 3; exit 0; report exists
- approved SHA exact; protected exact; token scan passed
- no live/Production modification

Approved report:
`debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow.json`

Semantic guard on the current 358-attack production-compatible assembly:
- 1,020 rendered notes
- before guard: 82 technique events, 53 on secondary/polyphonic notes, 40 bends, 42 legato sources
- after guard: 22 technique events, zero secondary technique events, 13 bends, 9 legato sources
- stripped 27 secondary bends, 48 secondary legato annotations, 7 invalid primary→secondary legato links, 80 audio-derived technique labels
- event/timing/pitch/string/fret identity unchanged

Sustain shadow:
- 652/1,020 notes received two-view harmonic-persistence sustain evidence
- 587 were longer than the current detector sustain; 56 shorter
- no attacks/pitches moved or invented
- no tie/let-ring inferred from duration alone
- current production sustain is not overwritten

Both are reference-free and physically safe, but they are not yet integrated into the new corrected candidate freeze.

## Current architecture gap

The green correction shadow currently stops at corrected `(measure, step)` attacks + supported pitch sets. It does **not** yet produce the final mapped guitar events, semantic/sustain annotations, authenticated event freeze, or Jimmy PAIge professional preview/full PDF.

Next work is to build an **isolated candidate path** that consumes the accepted physical correction and reuses the existing professional mapping/render contracts without touching the protected live pipeline. Then freeze a brand-new approved-audio identity and only after that run the scorer-only professional holdout.

Relevant existing workflow families discovered for reuse:
- `rhythm-final-preholdout-lock.yml`
- `rhythm-final-render-relock*.yml`
- `rhythm-professional-preholdout-real-audio.yml`
- `rhythm-professional-holdout-self-test-v2.yml`
- `v143-jimmy-professional-pdf-bridge-check.yml`
- `v143-jimmy-upload-to-professional-pdf-integration-v2.yml`
- `rhythm-render-presentation-proof.yml`

## Immediate next steps

1. Inspect the existing preholdout/final-render/Jimmy PDF workflows and their referenced scripts to reuse the exact professional rendering contract.
2. Build an isolated corrected-candidate event adapter: physical corrected attacks + supported pitch sets → mapped string/fret events, without modifying `v143_reference_free_rhythm_pipeline.py`.
3. Apply only independently green reference-free semantics/sustain handling in that candidate path.
4. Create a **brand-new approved-audio analysis/freeze/PDF identity** and prove PDF-event fidelity `1.0`.
5. Only after the freeze is immutable, open the scorer-only professional human reference and run the new holdout.
6. Use any new failure only as broad/general diagnostics; never add song-specific runtime rules.
7. Require >=0.99, zero critical mismatches, PDF-event fidelity 1.0 before Rhythm completion.
