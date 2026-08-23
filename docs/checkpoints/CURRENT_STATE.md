# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Professional human reference is scorer-only. Runtime may never read/train/tune/select from it. Corrections after a holdout failure must remain general/reference-free. After accepting any correction, create a **brand-new approved-audio analysis/freeze/PDF identity before another professional score**.

Rhythm completion requires professional score >= `0.99`, critical mismatches = `0`, PDF-event fidelity = `1.0`.

**Rhythm is NOT complete.**

## Locked identities

Protected runtime: `analyzer/v143_reference_free_rhythm_pipeline.py`
Required blob: `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
Restore commit: `4ff233346b8dc7b80d8f4316fe1317338b5be718`

Approved audio: `public/gomywayfullaitest.m4a`
SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

Scorer-only professional reference (never commit):
`/mnt/data/scorer_workspace/validation/rhythm_holdout/reference/professional-rhythm-complete.json`
SHA256: `4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd`
Complete 1–113; 577 playable onset objects; 925 playable note entries; verifier passed.

Old scored freeze must not be rescored: 358 attacks / 1,017 notes / 112 populated measures, missing 101 / event SHA `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e` / PDF fidelity 1.0.

Old professional holdout FAILED: pitchContentF1 `0.2626158599382081`; pitchTimingTolerantF1 `0.07209062821833163`; stringFretTimingTolerantF1 `0.030895983522142123`; chord/exact-voicing F1 `0`; coverage recall `0.9911504424778761`; critical mismatches `1653`.
General failure classes only: attack under-selection/measure loss; polyphony/harmonic inflation; broad pitch-position-timing mismatch. No song-specific runtime rules from scorer/reference.

## Boundary-grid fix — GREEN

Carrier `analyzer/v143_contextual_prune_reference_free_carrier.py`, commit `9b0adba5cda329cccbee0b7eed58cd4f75277ee0`.
The approved audio legitimately contains 1788 timing slots because it begins inside measure 1 and ends inside measure 113. No synthetic pre/post-audio slots are added. Interior measures remain full 16-step grids; first/last partial boundaries must be contiguous suffix/prefix shapes.

`debug/v143-contextual-prune/boundary-grid.json` GREEN:
- 1788 slots: m1 steps 12–15, m2–112 full, m113 steps 0–7
- no synthetic slots
- protected blob exact; anti-leakage pass; Production unchanged

## Approved reference-free attack/pitch correction — GREEN

Fresh approved action/report:
- `debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`
- `debug/v143-contextual-prune/shadow-correction-approved-audio.json`

Result:
- research carrier rows 5,484; grid 1,788; raw detections 143,902
- contextual selector 1,116 base → 949 attacks
- strict physical rescue 949 → 979 attacks, +30 observed local peaks
- all 113 measures populated before/after
- observed pitch hypotheses 10,686 → supported 2,055
- mean pitches/attack 10.915 → 2.099; max 33 → 8
- 959 events changed only by suppression; 8,631 unsupported pitches removed
- events >=5 pitches 884 → 41; >=6 pitches 833 → 14
- no event relocation; no invented pitch; protected/live/Production untouched

Timing remains diagnostic-only: tempo `129.19921875`, first beat in measure 3, downbeat mod4 1. Current phase is the reference-free four-way winner but low confidence `0.08797339512490407`; no phase selection/change. Strict residual median ~27.3 ms; ~99.65% within 60 ms; ~15.97% strict rows have <=20 ms nearest-vs-runner-up ambiguity.

## Independent real physical review — GREEN

`debug/v143-contextual-prune/approved-shadow-physical-review.json` now validates the **real** approved report:
- trigger/checkout `670fb25b9177f1483abe0efca2fd1781a89e3cb8`
- checker blob `e2facac5a63d49af05bd85f4bcf05625113284cf`
- base 949 / corrected 979 / rescued 30 / suppressed 8,631
- 113 populated measures
- all 959 pitch changes reconcile; suppression-only
- no phase mutation
- professional reference not used
- protected blob exact; Production unchanged

This proves safety/internal physical consistency, not professional correctness.

## Reference-free semantics + sustain — approved audio GREEN

`debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow-action.json` and report are GREEN.

On current production-compatible 358-attack assembly:
- semantic guard: 1,020 notes; 82 technique events → 22; secondary-technique events 53 → 0; bends 40 → 13; legato sources 42 → 9
- stripped invalid secondary/ownership semantics only; event/timing/pitch/string/fret identity unchanged
- sustain shadow annotated 652/1,020 notes; 587 longer and 56 shorter than old detector; no attack/pitch invention and no tie/let-ring inference
- reference-free; protected/live/Production unchanged

## Corrected candidate event adapter — CPU GREEN

New isolated adapter:
`analyzer/v143_contextual_prune_candidate_events.py`
commit `ce240773ed3f95bf4989853a7e10a215f180f0fa`

Checker:
`analyzer/check_v143_contextual_prune_candidate_events.py`
commit `b7f650da6dbe1c02c675f2716898cfb3474cbfd3`

Workflow:
`.github/workflows/v143-contextual-prune-candidate-events.yml`
commit `119a18cbff67ff04f9be663db23f3255fb592e7a`

Current report `debug/v143-contextual-prune/candidate-events.json` GREEN:
- adapter blob `175db5dbbdf77e2be9113ba16f2413a3993aebb2`
- checker blob `e831b36e5a5b5f06c941e29349646ac70eea7804`
- every corrected attack rendered
- output pitches are subsets of accepted physical pitch sets only
- deterministic legal six-string joint voicing; >6-pitch sets reduce only by physical/playability constraint
- no relocation; no reference; protected exact; Production unchanged

## New isolated corrected candidate → Jimmy PAIge PDF path

Created:
- `analyzer/v143_contextual_prune_candidate_product_modal.py`, commit `2bacb894bbdb0555acfcd5c75363a78200f95e35`
- `validation/rhythm_holdout/prepare_corrected_candidate_freeze_payload.mjs`, commit `0565b16a649a490cc9ee34940f486696159055b7`
- `.github/workflows/v143-corrected-rhythm-candidate-preholdout.yml`, commit `ec63baa13870ec357934f0530409bb04ccb4dc73`

Candidate runner is isolated and reference-free:
1. approved audio → research normalization → deterministic two-guitar views
2. 1788-slot carrier → contextual prune → accepted physical correction
3. corrected attack/pitch sets → legal joint guitar voicings
4. strict two-view bend + legato evidence
5. green primary-note semantic guard
6. green two-view sustain consensus, promoted **candidate-only** to `rhythmSustain`
7. Jimmy-compatible structured events, with protected live pipeline untouched

Pre-holdout workflow reuses the established exact production-quality contracts:
- runtime-isolation + forbidden-reference-token gate
- protected pipeline hash gate
- `buildJimmyPaigeAnalysisPayload`
- `freeze_rhythm_analysis.py`
- `createV143RhythmPdf`
- `render_frozen_rhythm_pdf.mjs`
- `verify_pdf_event_fidelity.py`
- structured presentation proof
- uploads full + preview professional PDF and immutable freeze artifact
- commits only compact `debug/v143-contextual-prune/corrected-candidate-preholdout.json`
- **does not open the professional human reference**

The new approved-audio corrected-candidate freeze/PDF run is currently pending. Do not score until its immutable freeze proves PDF-event fidelity 1.0.

## Immediate next steps

1. Read `debug/v143-contextual-prune/corrected-candidate-preholdout.json` when it lands; debug any runner/render failure reference-free.
2. Require: approved fixture exact, protected blob exact, 113 measures, authenticated event stream, professional preview/full PDF, renderer projection exact, PDF-event fidelity 1.0.
3. Download/inspect the resulting workflow freeze/PDF artifact.
4. Only after the new freeze is immutable, place/copy the provided complete human reference into the scorer-only holdout directory if needed and run `score_rhythm_holdout.py` against this **new** freeze.
5. Use scorer failures only as broad/general diagnostics; create a brand-new freeze after every accepted correction.
6. Rhythm complete only at >=0.99, zero critical mismatches, PDF-event fidelity 1.0.
