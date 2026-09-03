# Songsterr-inspired architecture gap inventory — 2026-09-03

Branch: `v143-contextual-prune-lobo`

Status: **REFERENCE-BLIND INVENTORY COMPLETE / NO SCORE AUTHORIZATION**

## Scientific boundary

This inventory is admissible while V168 is blocked because it uses only:

- public Songsterr product/help/hiring information;
- existing DadRock source on this branch;
- no GOAT restricted bytes;
- no GuitarSet/SplitMySong reference reads or score calls;
- no prospective players `00/01/03`;
- no GPU/CUDA/Modal execution;
- no Production or `main` changes.

It does **not** reopen GuitarSet and does not authorize a new reference-facing evaluation.

## Public Songsterr clues fixed before any new DadRock score call

Publicly observable Songsterr behavior currently exposes:

1. pre-transcription musical-structure controls:
   - first-bar time signature;
   - pickup-bar duration;
   - first-bar tempo/BPM;
   - triplet feel;
2. instrument selection/adjustment with distinct targets including vocals, rhythm guitar, lead guitar, bass and drums;
3. guitar/bass track configuration including tuning and capo;
4. a generated **draft** tab that is opened in an editor for correction/publishing;
5. a public 2026 Songsterr ML-engineer listing saying its production automatic-transcription system uses `our models` and listing a training stack including Python, PyTorch, Accelerate/DeepSpeed and W&B;
6. a public August 2026 Songsterr-team reply stating recent work has focused on improving existing instruments and `measure structure`.

Public URLs used:

- https://www.songsterr.com/new
- https://www.songsterr.com/help
- https://www.songsterr.com/plus
- https://www.songsterr.com/terms
- publicly indexed Songsterr/Reddit and job-listing pages described in the companion observation checkpoint.

No claim is made that Songsterr uses Demucs, Basic Pitch, MDX, Moises, Whisper, or any other specific separator/transcriber architecture. No hidden endpoint, paid feature, private tab, or protected implementation was probed.

## Existing DadRock capabilities already present

### A. Whole-audio Basic Pitch baseline

`analyzer/modal_analyzer.py` already:

- normalizes uploaded audio;
- runs Basic Pitch on the normalized full mix;
- converts MIDI pitches into guitar/bass string/fret positions after note inference;
- uses fixed standard guitar or bass tuning;
- includes local fret-continuity heuristics;
- returns no first-class meter/pickup/triplet estimate and originally returns `tempo=None`, `timeSignature=None`.

Therefore `run a pitch model and map notes to frets` is not a new architecture.

### B. Historical rhythm/tempo inference already exists

`analyzer/modal_analyzer_v34.py` already contains a conservative `estimate_beat_interval()` over onset-group spacing, pulse-aware harmonic windows, and rhythm diagnostics that expose estimated beat seconds and tempo BPM. When an estimate exists, V34 writes it to `result["tempo"]`.

Therefore `add a generic tempo estimator` is not a sufficiently new independent candidate family.

### C. Historical measure-grid projection already exists

`analyzer/build_v7_measure_grid_projection.py` already projects events onto a measure/beat/sixteenth-note representation using a BPM, beats-per-measure value and quantization grid.

Therefore `quantize to measures` alone is not new.

### D. Separation/carrier research already exists

The branch history/research already contains six-source Demucs separation and V143 carrier work involving direct Demucs6s Guitar and BS-RoFormer Instrumental -> Demucs6s Guitar. Backing Track Studio also contains a Demucs six-source separator configuration.

Therefore `add Demucs/source separation` is not new and should not be presented as a Songsterr-derived breakthrough.

### E. Current `/ai-tab` request contract is much thinner

The current public DadRock `/ai-tab` UI/request path principally chooses `lead`, `rhythm`, or `bass` and sends the audio plus transcription type to the analyzer. It does not currently carry the Songsterr-like structure/tuning configuration as an explicit end-to-end contract.

## Genuine architecture gap identified

The independent gap is **not an individual algorithm already tried in isolation**. It is a missing end-to-end conditioning contract that lets musical structure and physical instrument configuration constrain the transcription pipeline before final tab rendering.

Working name: **`STRUCTURE_INSTRUMENT_CONDITIONING_V1`**.

### Proposed reference-blind input contract

```text
StructurePriorV1
  firstBarTimeSignature:
    auto | { numerator, denominator }
  pickupDurationBeats:
    auto | number
  firstBarTempoBpm:
    auto | number
  tripletFeel:
    auto | straight | triplet

InstrumentConfigV1
  role:
    lead | rhythm | bass
  tuningMidi:
    ordered list of open-string MIDI pitches
  capoFret:
    integer >= 0
```

The exact serialization/API shape is intentionally not frozen here; this is an architecture inventory, not an implementation checkpoint.

## Reference-blind pipeline hypothesis

```text
audio ingest
  -> optional existing carrier/separation path
  -> structure estimate and/or explicit StructurePriorV1 override
  -> role-conditioned event inference/routing
  -> structure-aware onset/duration quantization
  -> tuning/capo-conditioned contextual string/fret decoding
  -> tab result + structure/config provenance + uncertainty/editability metadata
```

### What `role-conditioned` means at this stage

This does **not** require claiming or immediately training separate deep models. The first admissible implementation can condition routing, priors, decoding and output constraints on the selected role while preserving the current reference-free model boundary. A future independently motivated learned role-specific model would require its own freeze and methodology.

## Why this is materially different from the exhausted V3/V4/V5 work

The frozen GuitarSet families chiefly explored correction/post-processing behaviors against already generated candidate events. `STRUCTURE_INSTRUMENT_CONDITIONING_V1` changes what information is explicitly available **before and during** interpretation/quantization/fret assignment:

- bar/meter context;
- pickup context;
- tempo context;
- straight-vs-triplet context;
- selected instrument role;
- actual tuning;
- capo.

That architecture is independently motivated by Songsterr's public configuration surface before any new GuitarSet reference-facing score call, rather than being chosen to rescue a prior near-signal.

## Important unknowns

Public evidence does **not** reveal:

- Songsterr's exact neural architecture;
- model count or parameter sizes;
- whether source separation is a separate neural stage;
- exact loss functions/training data;
- exact beat/downbeat estimator;
- exact guitar fingering solver;
- whether tuning/capo condition the neural model itself, a decoder, or both;
- confidence thresholds/post-processing constants.

Those should remain unknown rather than guessed into DadRock's implementation.

## Safest next implementation boundary

If development continues while GOAT remains unavailable, the next scientifically clean step is a **reference-blind plumbing prototype** only:

1. freeze a schema for structure + instrument configuration;
2. thread it through `/ai-tab` -> API -> analyzer without reading any frozen reference;
3. make the fret/string solver accept caller-provided tuning and capo rather than fixed standard tuning;
4. expose structure/config provenance in output;
5. add deterministic synthetic/unit tests for custom tuning, capo, meter/pickup/triplet serialization and quantization behavior;
6. do not call GuitarSet/SplitMySong/GOAT scorers during this plumbing phase;
7. only after that prototype is independently frozen may a separate methodology checkpoint decide whether any reference-facing evaluation is scientifically admissible.

## Result

**Inventory conclusion: `NEW_INTEGRATION_GAP_IDENTIFIED`**.

Songsterr's public surface gives a useful hint: production-grade guitar-tab transcription appears to treat musical structure and instrument configuration as first-class inputs around the transcription system, rather than exposing only a generic audio-to-pitch pass. DadRock already has many component ideas separately; the genuinely new research direction is integrating those inputs as explicit conditioning and provenance across the whole pipeline.

This conclusion authorizes **no score call, no GuitarSet V6 threshold sweep, no GOAT substitution, no GPU/CUDA/Modal run, and no Production/main change**.
