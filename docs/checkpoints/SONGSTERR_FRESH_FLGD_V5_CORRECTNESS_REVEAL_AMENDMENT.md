# Songsterr Fresh — FLGD V5 Deferred Correctness-Reveal Amendment

Status: **FROZEN BEFORE ANY FLGD BASIC PITCH / V5 CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

The final FLGD V5 scoring method, population, Basic Pitch settings, V5 method, matcher, tolerances, uncertainty statistic and admission gates are already frozen. This amendment changes **execution order only** so an infrastructure/model failure on a later file cannot expose a partial holdout correctness result and create ambiguity about whether a retry remains scientifically clean.

No FLGD correctness result existed when this amendment was frozen.

## Frozen execution rule

The one official 79-performance FLGD run MUST execute in two phases.

### Phase 1 — reference-blind inference/classification for all 79 files

For every frozen Stage B performance, in the frozen order:
- verify source/audio identity;
- create the already-preregistered canonical 44.1-kHz mono FLOAT WAV;
- invoke frozen Basic Pitch exactly once;
- validate and preserve every decoded `(noteId,startSeconds,midi)` identity;
- invoke frozen V5 exactly once for every decoded event;
- record decoded-event/classification identities and counts.

Phase 1 MUST NOT perform estimate/reference matching or compute any correctness metric.

Phase-1 progress output may report file index/stem, decoded count and V5 classification counts because those are reference-blind. It MUST NOT report matched/correct counts, precision, recall, Wilson statistics, nearest-reference diagnostics or any other correctness-derived value.

If any of the 79 files fails Phase 1, the official execution fails closed **before correctness is revealed**.

### Phase 2 — correctness scoring only after Phase 1 completes 79/79

Only after all 79 frozen performances have completed Phase 1 successfully may the harness:
- reconstruct/use the already-bound canonical reference events;
- perform the already-frozen per-performance deterministic maximum-cardinality onset/pitch matcher;
- compute baseline diagnostics and V5-positive correctness;
- aggregate pooled/split/guitar-type metrics, Wilson lower bound and frozen gates;
- write the one official result artifact.

The scoring method itself is unchanged:
- onset tolerance <= 0.050 s inclusive;
- pitch tolerance <= 50 cents inclusive;
- `1e-12` only as the previously frozen binary64 boundary representation tolerance;
- durations/offsets ignored;
- pooled positives >=1000;
- pooled one-sided 95% Wilson lower bound >=0.9900;
- mandatory split/guitar-type strata with >=100 positives require point precision >=0.9500.

## Implementation requirement

The official entrypoint may be a thin adapter over the already-green core scoring harness, but it must make the phase boundary explicit and auditable. The Phase-1 processing function must not accept reference-note arguments. References may be supplied only to a separate Phase-2 scoring function after the 79/79 Phase-1 completion guard passes.

A controlled synthetic test must verify:
- Phase-1 processing/classification is reference-blind by API shape;
- Phase-1 completion logs contain no correctness value;
- scoring functions preserve the existing frozen matcher/gate semantics;
- a simulated Phase-1 failure prevents the scoring phase from being entered;
- no real FLGD or Basic Pitch model inference is used by CI.

## Single-run and policy boundary

This amendment does not authorize an extra holdout run. It is part of the same single official FLGD V5 validation preregistration.

After any Phase-2 correctness result is observed:
- no V5/Basic Pitch tuning;
- no threshold/tolerance/gate changes;
- no file/stratum exclusions;
- no rerun under this preregistration to seek a better result.

Authority remains unchanged:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged/paused;
- protected song unused;
- separate post-result policy review required.
