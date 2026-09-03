# Songsterr public-clue dual-context topology hypothesis — 2026-09-03

Branch: `v143-contextual-prune-lobo`

Status: **REFERENCE-BLIND HYPOTHESIS / NO SCORE AUTHORIZATION**

## Boundary

This checkpoint records an independently motivated architecture hypothesis before any new frozen-reference score call. It does not read GOAT, GuitarSet, SplitMySong, or prospective player references; does not run GPU/CUDA/Modal; does not alter Production or `main`; and does not reopen the frozen GuitarSet V3/V4/V5 families.

## New public clue

A January 2026 publicly indexed r/Songsterr reply, in a thread explicitly asking Songsterr's developer how the AI works, states that:

- the system does not use third-party transcription services and uses `our models`;
- source separation is performed `under the hood`;
- supplying already-separated tracks can make **measure-structure prediction harder** and may add little because the system performs separation itself.

This Reddit evidence is treated as a **public behavioral clue, not source-code proof**. Its exact author identity was not independently authenticated in this work.

It is materially strengthened by independent public evidence:

- Songsterr's own `/new` form takes a full YouTube/audio mix and exposes structure controls (time signature, pickup, tempo, triplet feel) alongside instrument targets;
- a current public Songsterr ML-engineer listing says its production automatic-transcription system uses `our models` and names Python/PyTorch/Accelerate/DeepSpeed/W&B;
- an August 2026 public r/Songsterr reply says improving `measure structure` is an active focus.

No hidden API, private implementation, paid feature bypass, or protected data was accessed.

## Strongest architecture inference

The separation clue argues against a naive pipeline that discards the mixture immediately:

```text
full mix
  -> separator
  -> isolated stem only
  -> all later inference
```

A more plausible topology is a **dual-context / parallel-context pipeline** in which the original mix remains available for global musical structure while separated/role-conditioned representations help local note inference:

```text
                         +-> FULL-MIX STRUCTURE CONTEXT
                         |     tempo / pulse / meter / downbeat
                         |     pickup / triplet or swing context
AUDIO FULL MIX ----------+
                         |
                         +-> INTERNAL SEPARATION / ROLE ROUTING
                               guitar role(s) / bass / drums / vocals
                                      |
                                      v
                              NOTE / TECHNIQUE EVENTS

FULL-MIX STRUCTURE CONTEXT + NOTE EVENTS
  -> bar/beat-aware alignment and quantization
  -> role + tuning + capo-conditioned string/fret decoding
  -> score/tab assembly
  -> editable draft + provenance/uncertainty
```

This diagram is **our hypothesis**, not a claim that it reproduces Songsterr's private implementation.

## Confidence ranking

### High confidence — structure and instrument configuration are first-class product inputs

Directly visible on Songsterr `/new`.

### High confidence — Songsterr uses production ML models rather than only a rules engine

Direct public ML-engineer listing describes `our models` turning audio into tablature and a PyTorch training stack.

### Medium confidence — internal source separation is part of the production transcription system

Supported by the January 2026 r/Songsterr reply, but not independently proven from Songsterr source code or a technical paper.

### Medium confidence — mixture context is deliberately preserved for structure prediction

The Reddit statement that pre-separated tracks can make measure-structure prediction harder strongly suggests the full mixture contributes useful structure evidence. It does not reveal whether Songsterr implements this as a separate branch, shared encoder, multi-task model, late fusion, or another design.

### Unknown — exact model topology

No public evidence establishes whether Songsterr uses one multitask network, multiple networks, a shared encoder, a beat/downbeat model, a dedicated separator, a language/sequence model, a graph/beam fingering solver, or specific model families.

## DadRock impact

Existing DadRock research already has:

- Basic Pitch full-mix note inference in the original baseline;
- historical onset-gap tempo/rhythm logic in V34;
- historical measure-grid projection;
- Demucs/BS-RoFormer carrier paths in V143 research.

The independent gap is therefore more precise than `add separation` or `add tempo`:

> **Do not throw away the original mix when using a separated guitar carrier. Preserve a reference-blind full-mix structural context in parallel and fuse it with role-specific note evidence before measure quantization and fret decoding.**

This can live inside the previously identified `STRUCTURE_INSTRUMENT_CONDITIONING_V1` architecture as a **dual-context topology**.

## Candidate shape before any reference use

A future implementation freeze may define two explicit inputs to the structure/tab assembly stage:

```text
MixtureStructureContextV1
  tempo estimate/prior
  meter estimate/prior
  downbeat/bar phase
  pickup/anacrusis
  triplet/straight feel
  confidence + provenance

InstrumentEventContextV1
  role
  note events + confidences
  source/carrier provenance
  tuning
  capo
```

The merger must be deterministic and reference-blind during implementation/testing.

## Safest first implementation

Before any reference-facing evaluation:

1. preserve both normalized full-mix audio identity and any existing separated-carrier identity in the analyzer request/result provenance;
2. implement/adapter-test a mixture-structure context interface without changing frozen thresholds;
3. accept explicit user structure overrides and custom tuning/capo as higher-priority inputs where present;
4. make measure projection consume the structure context rather than a hard-coded/default BPM alone;
5. make fret decoding consume tuning/capo config rather than fixed standard tuning alone;
6. use deterministic synthetic audio/event fixtures and unit tests only;
7. freeze implementation/version/hashes before considering a new reference-facing methodology checkpoint.

## Result

**`DUAL_CONTEXT_TOPOLOGY_INDEPENDENTLY_MOTIVATED`**.

This is a stronger and more specific architecture clue than simply copying Songsterr's visible settings. It suggests that global mixture information and separated instrument evidence solve different subproblems and should coexist through transcription.

No score call, GuitarSet V6 threshold sweep, GOAT substitution, GPU/CUDA/Modal run, or Production/main change is authorized by this checkpoint.
