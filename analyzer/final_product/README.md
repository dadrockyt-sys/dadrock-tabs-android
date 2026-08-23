# DadRock AI Tab Final Product Engines

This directory is the inactive construction home for the final `dadrocktabs.com/ai-tab` analyzer architecture.

It deliberately separates shared infrastructure from instrument-specific musical intelligence:

```text
final_product/
  shared/
  rhythm/
  lead/
  bass/
```

## Shared-core rule

Only genuinely instrument-agnostic behavior belongs in `shared/`, such as audio normalization, request adaptation, timing/grid utilities, common event schema, metadata transport, evidence helpers, safety helpers, and reusable quality-report primitives.

## Instrument-engine rule

Each instrument owns its own Hz/frequency features, candidate selection, fretboard behavior, techniques, model/training artifacts, quality gate, output identity, and instrument-specific rendering contract.

- `rhythm/` is modeled from the proven reference-free V143 Rhythm pipeline and remains the reference architecture.
- `lead/` may reuse deterministic separated Guitar views but must develop Lead-specific melodic/solo analysis, Hz/pitch trajectory evidence, techniques, training, and quality gating.
- `bass/` uses a true Bass separation path plus four-string G-D-A-E playability, Bass-specific Hz/training, techniques, quality gating, and rendering.

## Activation boundary

Nothing in this directory is active merely because it exists. New Lead/Bass code must remain fail-closed until independently proven with approved real audio, authenticated timing/playability, quality evidence, professional preview/full-PDF evidence, and explicit routing decisions.

Do not import these construction modules into the live customer route until the relevant instrument track has earned its own professional identity.
