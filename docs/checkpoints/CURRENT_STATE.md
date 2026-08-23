# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Professional human reference is scorer-only. Runtime may never read/train/tune/select from it. Any musical improvement after a holdout failure must stay general/reference-free. After accepting any such product correction, create a **brand-new approved-audio run/freeze/PDF identity before another professional score**.

**Save this checkpoint frequently.**

## Completion gate

Rhythm is complete only when all are true:
- professional score >= `0.99`
- critical mismatches = `0`
- PDF-event fidelity = `1.0`

**Rhythm is NOT complete. No completion claim is authorized.**

## Protected runtime boundary

Protected file:
`analyzer/v143_reference_free_rhythm_pipeline.py`

Required exact Git blob:
`7f72f8ed9b14af8bc93e95544195204d99c6bec1`

Restore commit:
`4ff233346b8dc7b80d8f4316fe1317338b5be718`

Current correction CPU gate again proves this blob is unchanged and Production is unmodified.

## Approved audio / old frozen identity

Approved fixture:
`public/gomywayfullaitest.m4a`

SHA256:
`215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

Old frozen candidate that was scored:
- 358 attacks
- 1,017 rendered notes
- 277 polyphonic attacks
- 112 populated measures of 1–113
- missing generated measure 101
- event SHA256 `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- frozen/PDF event hashes identical
- PDF-event fidelity exactly `1.0`

Final-presentation run:
- run `32643978196`
- artifact `9494412019`
- digest `sha256:5ab309e1c86826cb8b5c6ef9c6e3a8edbad334d99d55c07538475c7b61ba519b`

This old freeze may be inspected for diagnosis but must **not** be rescored after tuning.

## Professional scorer-only human reference

Source:
- `main/public/Professionalexample.jpg` at commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577`
- recovery run `32624327056`, artifact `9489261810`
- source SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- title `Are You Gonna Go My Way`, artist `Lenny Kravitz`, tempo 129
- panels 1–8 contain complete notation; panel 9 is redundant overlap

Temporary structured scorer-only reference:
`/mnt/data/scorer_workspace/validation/rhythm_holdout/reference/professional-rhythm-complete.json`

Reference SHA256:
`4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd`

Reference state:
- measures 1–113 contiguous
- 577 playable onset objects
- 925 playable note entries
- 104 measures with playable attacks
- uncertain duration/tie/technique/rest data omitted rather than invented
- muted/dead `X` attacks were not invented as pitched notes
- completeness verifier PASSED

**Never commit this reference.**

## Real professional holdout — FAILED

The mandatory holdout was run on the exact old frozen `a089...` stream only after freeze/PDF validation.

Results:
- `pitchContentF1 = 0.2626158599382081`
- `pitchTimingTolerantF1 = 0.07209062821833163`
- `stringFretTimingTolerantF1 = 0.030895983522142123`
- `chordPitchSetTolerantF1 = 0.0`
- `exactVoicingTolerantF1 = 0.0`
- `measureCoverageRecall = 0.9911504424778761`
- `pdfEventFidelity = 1.0`
- `criticalMismatchCount = 1653`
  - unmatched generated notes 872
  - unmatched reference notes 780
  - missing reference measures 1

General failure classes only:
1. attack under-selection / measure loss
2. polyphony / harmonic inflation
3. broad pitch-position-timing mismatch

Do not derive song-specific runtime rules from the professional source or score.

## Correction shadow — attack rescue + pitch support

Files:
- `analyzer/v143_contextual_prune_shadow_correction.py`
- `analyzer/check_v143_contextual_prune_shadow_correction.py`
- `analyzer/v143_contextual_prune_shadow_correction_modal.py`
- `.github/workflows/v143-contextual-prune-shadow-correction-cpu.yml`
- `.github/workflows/v143-contextual-prune-shadow-correction-approved-audio.yml`

The earlier empty-measure-only rescue was too conservative for the general under-selection class. It is now expanded, still reference-free, to rescue **strict local physical onset peaks in already-populated measures too**.

Current generic rescue requirements:
- observed carrier/grid slot only
- two separated guitar-view support
- >=3 historical detector sweeps
- >=4 detections
- cross-view CQT attack/body consensus
- at least median strict evidence strength within its own measure
- local evidence maximum within a small step neighborhood
- separated from already-selected attacks
- empty measures retain one strict physical fail-safe
- no attack relocation
- every base event preserved

Secondary pitch suppression remains based only on two-view attack/body CQT support relative to the locally strongest pitch. No hard song-specific chord templates exist.

Latest GitHub CPU/static diagnostic:
`debug/v143-contextual-prune/shadow-correction-cpu.json`

PASSED:
- base event preserved
- populated-measure local-peak rescue proven
- empty-measure rescue proven
- weak single-stem row rejected
- unsupported fifth harmonic suppressed
- `correctedEventCount=3` from synthetic `baseEventCount=1`
- `rescuedEventCount=2`
- protected pipeline blob exact `7f72...`
- reference token scan passed
- Production modified false

The exact approved-audio Modal correction report is still pending at:
`debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`

Do not claim approved-audio musical success until that file exists and its invariants pass.

## Professional PDF semantic bug investigation

Important correction to an earlier assumption: the old raw/frozen candidate is **not** technique-empty.

Recovered old raw product output contains:
- 82 rendered events with audio-derived technique annotations
- technique counts:
  - bend 41
  - bend-release 27
  - slide-down 18
  - slide-up 16
  - hammer-on 4
  - pull-off 3
- duration evidence is also present; most notes are short, but some quantize beyond one step

The renderer and freeze contract already carry technique and sustain fields. Therefore the central PDF bug is upstream musical semantics/ownership, not drawing alone.

### Concrete general semantic ownership bug found

`analyzer/v143_rhythm_guitar_note_mapper.py` explicitly marks each polyphonic mapped note with:
`noteMapping.primaryTechniqueNote`

The mapper also intentionally clears inherited attack-level technique fields from secondary chord tones.

However the post-selection audio bend and legato enrichers currently iterate over **all rendered polyphonic notes**. The recovered raw output confirms audio-derived bends can be applied to a note where `primaryTechniqueNote` is false. Harmonic/secondary chord tones can therefore be misread as bend/legato semantics.

This is a general bug independent of the professional reference.

New isolated guard files:
- `analyzer/v143_rhythm_semantic_primary_note_guard.py`
- `analyzer/check_v143_rhythm_semantic_primary_note_guard.py`
- `.github/workflows/v143-rhythm-semantic-primary-note-guard.yml`

Guard behavior:
- preserves event count/order
- preserves attack timing, MIDI, string and fret
- preserves valid primary-note audio semantics
- strips audio-derived bend/legato annotations from secondary chord tones
- removes primary legato links whose target is a secondary chord tone instead of silently redirecting them
- removes orphan legato continuation markers
- preserves unrelated explicit primary technique evidence
- no labels/reference input
- Production unchanged

The semantic guard CPU workflow result is pending. Do not integrate it into live/product routing until its safety gate is green and a new approved-audio shadow validates it.

## Existing production semantic path discovered

`analyzer/v143_modal_live_endpoint.py` already injects post-selection enrichers:
1. `enrich_router_assembly_with_consensus_bends`
2. `enrich_router_assembly_with_legato`

So semantic enrichment was not disabled in the old run.

Current bend logic uses two-view harmonic CQT contour consensus. Current legato logic uses two-view pitch-path plus re-attack evidence. The next semantic work should improve their **general evidence/ownership**, not add song-specific markings.

## Sustain/duration issue

`analyzer/v143_rhythm_sustain_technique_enricher.py` derives duration mainly from Basic Pitch `bestOnsetTime/bestOffsetTime` or `maxDuration`, then quantizes at four subdivisions per beat.

On the old raw output these detector durations are mostly very short. A professional tab needs sustain evidence that can survive detector note fragmentation.

Next safe design: an isolated two-view reference-free sustain shadow using persistent harmonic energy after each authenticated note, bounded by subsequent authenticated attacks/measure structure. It may annotate duration only; it must never move an attack or invent pitch. Tie/let-ring labels must require explicit physical continuity evidence and must not be inferred merely because a duration is long.

## Timing issue

The old run tempo is `129.19921875`, very close to source tempo 129, so tempo alone is not the main failure.

Current timing pipeline:
- full-mix reference-free onset envelope
- autocorrelation/IOI tempo
- dynamic beat path
- four-way 4/4 bar phase from beat accents
- 16-step subdivision grid
- Basic Pitch attacks mapped to nearest grid slot

Professional timing F1 remains very poor, but that metric is also strongly affected by incorrect pitch/attack selection. Do not tune bar phase against the human reference.

Next safe timing work: isolated label-free diagnostics for cross-stem onset residuals, four-way bar-phase confidence, repeated-structure consistency, and grid ambiguity. Any phase correction must be selected from audio/structural evidence only.

## Immediate next steps

1. Wait for/read exact approved-audio correction shadow report and semantic-primary-note CPU report.
2. If attack correction invariants pass, evaluate only label-free counts/coverage/strict-evidence behavior; do not score against the human reference yet.
3. Build isolated two-view sustain/duration diagnostics and primary-note technique ownership validation on approved audio.
4. Build label-free timing phase/residual diagnostics; do not use the human reference to select phase or thresholds.
5. Only after general corrections are independently accepted, integrate them on this branch and create a **brand-new** approved-audio analysis/freeze/PDF identity.
6. Then, and only then, open the professional scorer reference and run a new holdout.
7. Add only clearly visible/high-confidence professional technique/duration/tie markings to the scorer-only human reference; never invent uncertain semantics and never commit it.
8. Require >=0.99, zero critical mismatches and PDF-event fidelity 1.0 before Rhythm completion.
