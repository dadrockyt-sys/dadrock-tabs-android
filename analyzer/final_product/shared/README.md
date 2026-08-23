# Shared Final-Product Core

This folder is reserved for instrument-agnostic DadRock AI Tab infrastructure.

Allowed responsibilities include:

- audio normalization and validation;
- request/response adapters;
- common timing-grid utilities;
- common authenticated event schema;
- metadata transport and serialization;
- generic evidence/diagnostic helpers;
- safety/fail-closed helpers;
- reusable quality-report primitives;
- reusable PDF-layout primitives that do not assume a specific instrument/string count.

Do **not** put instrument-specific Hz ranges, fretboard rules, technique heuristics, training data, model weights, candidate-selection logic, string counts/tunings, or professional engine identities here.

The shared core must never manufacture missing measure/step/timing data for an instrument engine.
