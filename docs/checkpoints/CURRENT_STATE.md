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
Complete measures 1–113; 577 playable onset objects; 925 playable note entries; completeness verifier passed.

Old scored freeze must not be rescored: 358 attacks / 1,017 notes / 112 populated measures, missing 101 / event SHA `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e` / PDF fidelity 1.0.

Old professional holdout FAILED:
- pitchContentF1 `0.2626158599382081`
- pitchTimingTolerantF1 `0.07209062821833163`
- stringFretTimingTolerantF1 `0.030895983522142123`
- chordPitchSetTolerantF1 `0.0`
- exactVoicingTolerantF1 `0.0`
- measureCoverageRecall `0.9911504424778761`
- critical mismatches `1653`

General failure classes only: attack under-selection/measure loss; polyphony/harmonic inflation; broad pitch-position-timing mismatch. No song-specific runtime rules from scorer/reference.

## Boundary-grid fix — GREEN

Carrier `analyzer/v143_contextual_prune_reference_free_carrier.py`, commit `9b0adba5cda329cccbee0b7eed58cd4f75277ee0`.
Approved audio legitimately contains 1,788 timing slots because it starts inside measure 1 and ends inside measure 113. No synthetic pre/post-audio timing slots. Interior measures remain full 16-step grids; first/last partial boundaries must be contiguous suffix/prefix shapes.

`debug/v143-contextual-prune/boundary-grid.json` GREEN:
- m1 steps 12–15, m2–112 full, m113 steps 0–7
- grid count 1,788
- protected blob exact; anti-leakage pass; Production unchanged

## Approved reference-free attack/pitch correction — GREEN

Approved action/report:
- `debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`
- `debug/v143-contextual-prune/shadow-correction-approved-audio.json`

Result:
- carrier rows 5,484; raw detections 143,902
- contextual selector 1,116 base → 949 candidate attacks
- strict physical rescue 949 → 979 attacks (+30 observed local peaks)
- all 113 measures populated before/after
- observed pitch hypotheses 10,686 → supported 2,055
- mean pitches/attack 10.915 → 2.099; max 33 → 8
- 959 attacks changed only by pitch suppression; 8,631 unsupported pitches removed
- >=5 pitches 884 → 41; >=6 pitches 833 → 14
- no event relocation; no invented pitch; protected/live/Production untouched

Timing is diagnostic-only: tempo `129.19921875`, first beat in measure 3, downbeat mod4 1. Current four-way phase is the label-free winner but confidence is low `0.08797339512490407`; phase was not selected/changed. Strict residual median ~27.3 ms; ~99.65% within 60 ms; ~15.97% strict rows have <=20 ms nearest-vs-runner ambiguity.

## Independent real physical review — GREEN

`debug/v143-contextual-prune/approved-shadow-physical-review.json` validates the real approved correction:
- base 949 / corrected 979 / rescued 30 / suppressed 8,631
- all 113 measures populated
- 959 pitch changes reconcile; suppression-only
- no phase mutation
- professional reference not used
- protected exact; Production unchanged

This proves physical/internal consistency only, not professional correctness.

## Reference-free semantics + sustain — approved audio GREEN

`debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow-action.json` and report are GREEN.
On the old production-compatible 358-attack assembly:
- semantic guard 1,020 notes; technique events 82 → 22; secondary-technique events 53 → 0; bends 40 → 13; legato sources 42 → 9
- event/timing/pitch/string/fret identity unchanged
- sustain shadow annotated 652/1,020; no attack/pitch invention; no tie/let-ring inference
- protected/live/Production unchanged

## Corrected candidate event adapter — CPU GREEN

`analyzer/v143_contextual_prune_candidate_events.py`
- creation commit `ce240773ed3f95bf4989853a7e10a215f180f0fa`
- green source blob `175db5dbbdf77e2be9113ba16f2413a3993aebb2`

`analyzer/check_v143_contextual_prune_candidate_events.py`
- creation commit `b7f650da6dbe1c02c675f2716898cfb3474cbfd3`
- green checker blob `e831b36e5a5b5f06c941e29349646ac70eea7804`

`debug/v143-contextual-prune/candidate-events.json` GREEN:
- every corrected attack rendered
- emitted pitches are subsets of accepted physical pitch sets only
- legal six-string joint voicing; >6-pitch sets reduce only through physical/playability constraints
- no relocation/reference/Production change; protected exact

## FIRST corrected Jimmy PAIge professional freeze/PDF — GREEN

Isolated candidate runner:
`analyzer/v143_contextual_prune_candidate_product_modal.py`
commit `2bacb894bbdb0555acfcd5c75363a78200f95e35`

Freeze preparer:
`validation/rhythm_holdout/prepare_corrected_candidate_freeze_payload.mjs`
commit `0565b16a649a490cc9ee34940f486696159055b7`

Pre-holdout workflow:
`.github/workflows/v143-corrected-rhythm-candidate-preholdout.yml`
commit `ec63baa13870ec357934f0530409bb04ccb4dc73`

Green immutable diagnostic:
`debug/v143-contextual-prune/corrected-candidate-preholdout.json`
Bot commit: `345cb4ed4d6d6f545e00c5642e6814ef1f8b3066`
Trigger SHA: `ec63baa13870ec357934f0530409bb04ccb4dc73`

Freeze/PDF identity:
- corrected attacks: **979**
- rendered authenticated notes: **2,009**
- supported physical pitches before six-string voicing: 2,055
- voicing-only drops: 46
- unique measures: **113**
- event SHA256: `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`
- snapshot SHA256: `15490767571f0ba96f77c20cfc8c8bcef7fab72988e1c87d3d130b9b8dc7e1d8`
- PDF event SHA256: `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`
- **PDF-event fidelity = 1.0**
- renderer projection exact = true
- full PDF bytes 1,767,161
- preview PDF bytes 1,712,052
- full pages 4; preview pages 4
- professional reference opened = false
- protected pipeline exact; live endpoint and Production unchanged

Presentation:
- 979 unique onsets
- 2,009 rendered notes
- average notes/measure 17.779
- min/max notes per populated measure 3 / 50
- max chord size 6
- 569 multi-note onsets
- 37 technique events; hammer-on/pull-off/slide-up/slide-down
- 7 reference-free sections
- no one-note-per-measure collapse

Semantic guard on this corrected candidate:
- 2,009 events; 979 primary / 1,030 secondary
- stripped 101 secondary legato links + 10 invalid primary-to-secondary links
- event/timing/pitch/string/fret identity unchanged

Candidate sustain:
- 1,498/2,009 events received two-view sustain evidence
- all 1,498 were longer than the old fallback detector because this candidate path had not populated production sustain first
- no attack/pitch change; no tie/let-ring inference

All pre-holdout checks passed. This is the first corrected candidate that is eligible for a professional scorer-only holdout.

## Traceable workflow diagnostic

Added race-safe candidate diagnostic workflow:
`.github/workflows/v143-corrected-candidate-approved-audio.yml`
commit `a6ea1526c6ce40a894f42654aeb7042b9c38206a`
It always commits an action diagnostic, includes GitHub `runId`/attempt/source blobs, and never opens the professional reference. Its result may still be pending; it is diagnostic only and does not replace the already-green freeze above.

## Scorer/reference availability

The complete human reference is intentionally absent from GitHub; the repository reference folder contains only `.gitignore`, `reference-inventory.json`, and `reference.schema.json`.
The prior complete scorer JSON was temporary/local and is not present in the current ChatGPT Library as a JSON file. The Library does contain the user's supplied/proof tablature images, including multiple `Are You Gonna Go My Way` rhythm-tab pages. Do not reconstruct/open scorer labels until using the now-immutable green freeze.

## Immediate next steps

1. Make the successful freeze artifact traceable/downloadable by GitHub Actions run ID (the first green workflow diagnostic did not record its run ID).
2. Download the exact `v143-corrected-rhythm-professional-freeze` artifact containing the immutable freeze, preview/full PDF and event evidence.
3. Recover/materialize the provided complete human reference into a **local scorer-only** workspace without committing it.
4. Verify its SHA256 is `4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd` and completeness still passes.
5. Run `score_rhythm_holdout.py` only against this new immutable freeze.
6. Use any failures only as broad/general diagnostics; no song-specific runtime rule. Every accepted correction requires another brand-new approved-audio freeze/PDF before another score.
7. Rhythm complete only at >=0.99, zero critical mismatches and PDF-event fidelity 1.0.
