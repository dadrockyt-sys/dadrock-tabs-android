# V145 Rhythm Decoder — Frozen CPU Preregistration

Date: 2026-08-26 (America/Montreal)
Branch: `v143-contextual-prune-lobo`
Status: **CPU architecture experiment only; no Modal/L4/GPU execution authorized.**

## Purpose

V145 is a separate Rhythm architecture experiment intended to get beyond the diminishing returns of V144 post-hoc event rewrite/prune families. It does not replace, retune, replay, or reinterpret any consumed V144 family.

The immutable safety fallback remains accepted V144 family #10:
- Pitch Content F1: 0.35406698564593303 (35.4%)
- Pitch + timing: 0.06698564593301436 (6.7%)
- String/fret + timing: 0.05454545454545454 (5.5%)
- Chord/voicing: 0.0580511402902557 (5.8%)
- Measure coverage: 1.0
- PDF event fidelity: 1.0
- Event count: 1144
- Generated measures: 113
- Event/PDF SHA256: `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`

## Protected front end

V145 consumes Rhythm output from the existing V5 three-way separation benchmark as evidence. V5 remains immutable.

Current V5 separation policy:
- bass MIDI 28–51
- rhythm MIDI 52–63
- lead MIDI 64–76

V5 is a register-gated event separation benchmark, not neural waveform/stem separation. V145 therefore treats V5 events as uncertain evidence rather than final musical truth.

## Frozen architecture

`V5 Rhythm-separated events -> normalized evidence -> timing/onset lattice -> pitch lattice -> constrained guitar-state decoder -> candidate event stream -> existing scorer/render/PDF gates`

### Stage A — normalized evidence

The adapter may read only generated/runtime event fields. It must not read a human reference, gold label, FIT/validation/canary membership, or scorer output.

Pitch aliases accepted by the adapter are frozen to:
- `midi`
- `midiPitch`
- `pitch`

Onset aliases accepted by the adapter are frozen to:
- `onset`
- `time`
- `start`
- `startTime`

Duration aliases accepted by the adapter are frozen to:
- `duration`
- `durationSeconds`
- `length`

Confidence aliases accepted by the adapter are frozen to:
- `confidence`
- `score`
- `probability`

Missing duration defaults to 0.0. Missing confidence defaults to 1.0. Events without a finite pitch and finite non-negative onset are rejected from V145 evidence rather than invented.

### Stage B — timing/onset lattice

V145 must preserve the original generated onset as evidence and may additionally propose nearby timing-grid positions. Timing proposals are runtime-derived only.

The first CPU implementation must support:
- deterministic normalization and ordering;
- explicit grid quantum supplied by the caller;
- nearest-grid candidate plus immediate neighboring grid candidates within a frozen maximum shift;
- a non-negative timing cost proportional to displacement from the generated onset;
- no reference-derived timing correction.

Automatic tempo/quantum estimation is intentionally deferred until the deterministic lattice contract is proven.

### Stage C — pitch lattice

The first CPU implementation does not invent new MIDI pitches. Each normalized evidence event carries its generated MIDI pitch into every timing candidate.

Future pitch proposals may be added only in a new preregistered experiment after the timing lattice is proven.

### Stage D — constrained guitar-state decoder

Standard guitar tuning is frozen initially to MIDI `(40, 45, 50, 55, 59, 64)` for strings 6->1. Maximum fret is 24.

The decoder must:
- map every selected MIDI pitch to a physically valid string/fret position;
- never assign two simultaneous pitches to the same string;
- preserve exact MIDI equality between evidence pitch and selected string/fret;
- prefer compact fret spans and smaller inter-onset hand movement;
- be deterministic under equal scores;
- allow an onset to remain undecoded rather than fabricate an invalid guitar state.

The first CPU implementation may use bounded exhaustive/beam search because this is benchmark-only.

### Stage E — candidate safety wrapper

V145 output is never accepted merely because the decoder ran. Any later live benchmark must pass the existing independent scoring/render/PDF invariants. Until those gates are explicitly authorized and run, family #10 remains the accepted output.

## Runtime/reference isolation

The V145 core module must contain no parameter or API for:
- gold events;
- reference events;
- FIT labels;
- validation labels;
- canary labels;
- score-derived correction rules.

Human-reference data may be used only by the external benchmark scorer after a complete runtime candidate has been produced and locked.

## Initial CPU proof targets

1. Normalize V5-style Rhythm events deterministically.
2. Construct timing lattice candidates without reference input.
3. Enumerate only physically valid guitar positions.
4. Construct deterministic simultaneous-note guitar states with unique strings.
5. Demonstrate continuity cost can distinguish equally valid fingerings without changing pitch.
6. Demonstrate invalid/unplayable evidence fails closed instead of inventing notes.
7. Demonstrate the original input objects are not mutated.
8. Demonstrate no Modal/GPU dependency exists in the core module or unit tests.

## Explicit non-goals for this first proof

- No Modal execution.
- No L4/GPU execution.
- No waveform stem separation.
- No V5 analyzer edits.
- No automatic tempo estimation.
- No new pitch generation or octave correction.
- No score comparison against gold.
- No changes to `/ai-tab`, Bass, Lead, `freezeReady`, main, or Production.
- No V144 Family #15 search.

## Promotion rule

This preregistration only authorizes CPU implementation and CPU unit testing of the frozen contract above. Any live audio/Modal/GPU benchmark requires a separate explicit user authorization after the implementation and CPU proof are checkpointed.
