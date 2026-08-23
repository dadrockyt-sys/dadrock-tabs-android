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

Current correction, semantic-guard, and sustain CPU gates prove this blob is unchanged and Production is unmodified.

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

Generic rescue requirements:
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

CPU/static diagnostic:
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

Approved-audio correction report is still absent:
`debug/v143-contextual-prune/shadow-correction-approved-audio-action.json`

Do not claim approved-audio musical success until that file exists and its invariants pass.

## Professional PDF semantic ownership bug

The old raw/frozen candidate is not technique-empty. Recovered old raw output contains 82 rendered events with audio-derived technique annotations, including bend, bend-release, slide, hammer-on and pull-off. Duration evidence is also present.

General ownership bug: `analyzer/v143_rhythm_guitar_note_mapper.py` marks each polyphonic mapped note with `noteMapping.primaryTechniqueNote`, but post-selection bend/legato enrichers had been able to annotate secondary chord tones.

Isolated guard files:
- `analyzer/v143_rhythm_semantic_primary_note_guard.py`
- `analyzer/check_v143_rhythm_semantic_primary_note_guard.py`
- `.github/workflows/v143-rhythm-semantic-primary-note-guard.yml`

Guard behavior:
- preserves event count/order
- preserves attack timing, MIDI, string and fret
- preserves valid primary-note audio semantics
- strips audio-derived bend/legato annotations from secondary chord tones
- removes primary legato links whose target is a secondary chord tone
- removes orphan legato continuation markers
- preserves unrelated explicit primary technique evidence
- no labels/reference input
- Production unchanged

### Semantic guard CPU gate — PASSED

Committed report:
`debug/v143-contextual-prune/rhythm-semantic-primary-note-guard.json`

Result:
- `passed=true`
- reference token scan passed
- protected pipeline blob exact `7f72...`
- event count/timing/pitch/string/fret unchanged
- synthetic proof stripped 1 secondary bend, 1 secondary legato, 1 invalid primary legato and 2 audio technique labels
- Production modified false

Do not integrate into product routing until approved-audio shadow also validates it.

## Sustain/duration shadow

Files:
- `analyzer/v143_rhythm_sustain_consensus_shadow.py`
- `analyzer/check_v143_rhythm_sustain_consensus_shadow.py`
- `.github/workflows/v143-rhythm-sustain-consensus-shadow.yml`

Design:
- isolated two-view reference-free harmonic persistence after each authenticated note
- bounded by next authenticated attack on the same string and a max sustain window
- annotates only `rhythmSustainShadow`
- does not overwrite production `rhythmSustain`
- does not move attacks or invent pitch
- does not infer tie/let-ring labels

### Sustain CPU gate — PASSED

Committed report:
`debug/v143-contextual-prune/rhythm-sustain-consensus-shadow.json`

Result:
- `passed=true`
- two-view proof annotates physical sustain longer than the short detector duration
- event count, attack timing and pitch unchanged
- no tie/let-ring inference
- reference token scan passed
- protected pipeline blob exact `7f72...`
- Production modified false

## Approved-audio semantics + sustain shadow

Modal runner added:
`analyzer/v143_rhythm_semantics_sustain_approved_shadow_modal.py`

Commit:
`cd0fec62bdd3b4da9ce7645db4d3582d528a2164`

It runs the current reference-free rhythm assembly on the approved fixture, then bend + legato enrichment, semantic primary-note guard, and two-view sustain shadow. It records before/after technique counts and sustain histograms while requiring core event identity to remain unchanged.

New GitHub Actions workflow added:
`.github/workflows/v143-rhythm-semantics-sustain-approved-shadow.yml`

Workflow commit:
`c4077eff19e1e720719fc0147c1625df49c5c32a`

The workflow:
- SHA-gates the exact approved fixture
- uses existing Modal GitHub secrets only when available
- runs the isolated Modal shadow
- commits action/report diagnostics back to this branch
- enforces reference-free, event-identity, semantic-guard and sustain invariants
- does not deploy or modify the live endpoint/Production

Expected outputs:
- `debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow-action.json`
- `debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow.json`

These approved-audio outputs are **pending**. Do not integrate semantics or sustain into product routing until they exist and are green.

## Existing production semantic path

`analyzer/v143_modal_live_endpoint.py` already injects post-selection enrichers:
1. `enrich_router_assembly_with_consensus_bends`
2. `enrich_router_assembly_with_legato`

Semantic enrichment was therefore not disabled in the old run. Current bend logic uses two-view harmonic CQT contour consensus. Current legato logic uses two-view pitch-path plus re-attack evidence. Any improvements must remain general/reference-free.

## Timing issue

The old run tempo is `129.19921875`, close to source tempo 129, so tempo alone is not the main failure.

Current timing pipeline:
- full-mix reference-free onset envelope
- autocorrelation/IOI tempo
- dynamic beat path
- four-way 4/4 bar phase from beat accents
- 16-step subdivision grid
- Basic Pitch attacks mapped to nearest grid slot

Professional timing F1 remains poor, but the metric is also strongly affected by incorrect pitch/attack selection. Do not tune bar phase against the human reference.

Next safe timing work remains isolated label-free diagnostics for cross-stem onset residuals, four-way bar-phase confidence, repeated-structure consistency, and grid ambiguity. Any phase correction must be selected from audio/structural evidence only.

## Immediate next steps

1. Read the new approved-audio semantics/sustain action/report as soon as the workflow commits them.
2. Continue checking for the still-missing approved-audio attack-correction action/report.
3. If approved-audio invariants pass, evaluate only label-free counts/coverage/evidence behavior; do not score against the human reference yet.
4. Build/finish label-free timing phase/residual diagnostics; do not use the human reference to select phase or thresholds.
5. Only after general corrections are independently accepted, integrate them on this branch and create a **brand-new** approved-audio analysis/freeze/PDF identity.
6. Then, and only then, open the professional scorer reference and run a new holdout.
7. Add only clearly visible/high-confidence professional technique/duration/tie markings to the scorer-only human reference; never invent uncertain semantics and never commit it.
8. Require >=0.99, zero critical mismatches and PDF-event fidelity 1.0 before Rhythm completion.
