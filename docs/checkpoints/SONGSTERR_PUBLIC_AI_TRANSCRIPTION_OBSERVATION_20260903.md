# Songsterr public AI-transcription observation — 2026-09-03

Branch: `v143-contextual-prune-lobo`

Status: **PUBLIC-OBSERVATION ONLY / NO SONGSTERR PRIVATE OR PAID DATA / NO REFERENCE SCORE CALLS**

## Why this work is admissible now

V168 remains blocked on missing authorized GOAT assets. GuitarSet V3/V4/V5, SplitMySong, and prospective GuitarSet players remain frozen under the existing checkpoints. This observation pass does not read any frozen reference, does not score a candidate, does not retune an existing family, and does not alter V168.

The purpose is to identify independently visible product/architecture clues that could motivate a future reference-blind candidate family before any new reference-facing evaluation is considered.

## Public sources observed

- Songsterr AI new-tab page: https://www.songsterr.com/new
- Songsterr Help: https://www.songsterr.com/help
- Songsterr Plus: https://www.songsterr.com/plus
- Songsterr Terms: https://www.songsterr.com/terms
- Public r/Songsterr discussions indexed by search, including an August 2026 reply stating current focus on improving existing instruments and `measure structure`.

No login, Plus feature bypass, private endpoint access, hidden API probing, tab downloading, or automated modification/interference with Songsterr was performed.

## Directly observed current Songsterr AI controls

Songsterr's public `/new` form exposes these transcription inputs/settings:

1. YouTube URL or uploaded audio.
2. `First bar time signature` — Auto or user-specified.
3. `Pickup bar duration` — Auto or user-specified.
4. `First bar tempo (BPM)` — Auto or user-specified.
5. `Triplet feel` — Auto or user-specified.
6. `Instruments` — Auto or Adjust.
7. Separate instrument targets including:
   - Vocals
   - Rhythm guitar
   - Lead guitar
   - Bass
   - Drums
8. Guitar track configuration visibly includes an instrument sound/type, standard 6-string tuning `(E A D G B E)`, and capo fret.
9. Bass track configuration visibly includes an instrument sound/type, standard 4-string tuning `(E A D G)`, and capo fret.
10. Generated output is described as a draft/editable tab and remains private until the user chooses to share it.

## Important public behavioral clues

- Songsterr Help describes AI as generating a **draft tab** which then opens in the Songsterr Editor for correction and publication.
- A public August 2026 r/Songsterr reply attributed to the Songsterr team says recent work has focused on improving existing instruments and **measure structure**, while broader instrument support remains in progress.
- A July 2026 r/Songsterr thread reports that tuning can be specified in instrument settings before transcription/re-transcription.
- Public user reports show common failure modes include wrong instrument assignment, missing/merged guitars, wrong tuning, and measure/audio alignment errors. These are observations only and are not treated as ground truth accuracy measurements.

## Architecture hypotheses — ranked by confidence

### H1 — HIGH confidence: structure is a first-class stage, not merely presentation

Evidence: time signature, pickup, BPM, triplet feel are explicit pre-transcription controls; Songsterr staff publicly mention `measure structure` as a current improvement focus.

Implication for DadRock research: a future family should consider a dedicated reference-blind meter/tempo/downbeat/pickup representation before final tab quantization, rather than letting raw note onset timing implicitly define tab spacing.

### H2 — HIGH confidence: transcription is instrument-conditioned

Evidence: separate rhythm guitar, lead guitar, bass, drums, vocals controls, plus per-track tuning/capo controls.

Implication: a single generic pitch detector followed only by fret assignment is unlikely to match the product architecture exposed by Songsterr. Instrument-conditioned candidate generation and/or explicit stem/role routing is independently motivated.

### H3 — MEDIUM confidence: there is likely a source-separation or source-routing stage

Evidence: distinct simultaneous instrument targets and public failure reports about instrument confusion/merged guitars. This does **not** prove a specific separator or vendor/model.

Implication: separation/routing can be considered as an architecture family, but no claim should be made that Songsterr uses Demucs, MDX, Moises, Basic Pitch, or any particular model without direct evidence.

### H4 — HIGH confidence: tuning/fingering is constrained before or during transcription

Evidence: tuning and capo are pre-transcription instrument settings, and public users report re-transcription with explicit tuning.

Implication: fret/string assignment should be conditioned on the requested tuning/capo and ideally solved jointly/contextually rather than as a final stateless pitch-to-fret map.

### H5 — MEDIUM confidence: AI output is intentionally a draft plus structured editor loop

Evidence: Songsterr Help explicitly frames AI generation as a draft that can be edited and submitted.

Implication: product quality can be improved by exposing uncertainty/corrections instead of requiring the first pass to be final. This is product architecture, not a benchmark claim.

## Comparison with current DadRock baseline path

The original `analyzer/modal_analyzer.py` path:

- normalizes to 44.1 kHz stereo PCM;
- calls Basic Pitch directly on the complete normalized audio;
- assigns strings/frets after MIDI-pitch detection with a local continuity heuristic;
- returns no tempo or time-signature estimate;
- does not expose pickup/downbeat/triplet structure in the core result;
- does not perform separate instrument/stem routing inside this baseline file.

This makes Songsterr's public structure controls a genuinely independent architectural clue, not a threshold tweak derived from GuitarSet outcomes.

## Frozen boundary

This document does **not** reopen GuitarSet development and does not authorize a V6 threshold sweep. No reference-facing scoring is authorized by this observation alone.

Before any new reference score call, a future checkpoint must freeze a genuinely new reference-blind candidate hypothesis and implementation motivated by independent evidence such as the public structure/instrument-conditioned architecture documented here.

## Next safe research actions

1. Inventory existing DadRock experimental code for already-built reference-blind tempo/downbeat/meter, stem-routing, and tuning-aware modules so we do not duplicate prior work.
2. Separate what already exists from what Songsterr's public control surface newly suggests.
3. If there is a genuinely new architecture gap, define it **before** reading any frozen reference result.
4. CPU-only unless the user gives fresh explicit GPU/CUDA/Modal authorization.
5. Continue awaiting explicit GOAT owner approval/denial; this work does not substitute for GOAT.
