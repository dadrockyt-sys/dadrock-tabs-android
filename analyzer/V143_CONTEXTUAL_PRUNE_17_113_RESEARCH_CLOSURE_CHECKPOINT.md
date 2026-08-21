# DadRock Tabs — V143 Contextual-Prune 17–113 Research Closure Checkpoint

**Date:** 2026-08-21  
**Repository:** `dadrockyt-sys/dadrock-tabs-android`  
**Branch:** `v143-contextual-prune-lobo`

## Result

The historical/reference-free **research evidence chain for measures 17–113 is now closed**.

This is a research/provenance milestone only. It does **not** authorize production promotion or modification of the live V143 analyzer.

## Why the former 17–32 gap can now be superseded

The original 17–32 evidence-gap checkpoint was correct for the branch state inspected at the time and remains preserved as a historical record.

Its resume directive allowed reopening the gap only if genuinely new authoritative historical evidence later became available from an old branch/commit snapshot, retained artifact, backup, or similar source.

That condition was met by the historical calibration snapshot at:

`b25820ecde37dc87447a9366894bd8e4f7f21792`

The recovered historical generator:

`analyzer/v143_fresh_verse1_reference_free_capture.py`

explicitly defines the original target boundary as **measures 17–32**. Its Git blob is identical between the historical snapshot and the current research branch:

`c8ea8eca33819fb506f06105f87075dadd133214`

The original carrier lineage was independently recovered as:

1. direct Demucs6s Guitar;
2. BS-RoFormer Instrumental → Demucs6s Guitar.

The deterministic separator settings are also recovered:

- Demucs shifts: 1
- overlap: 0.10
- segment size: 6
- deterministic seed: 143

Most importantly, the historical freeze manifest fingerprints the old uncommitted Verse1 cache with SHA-256:

`fbb2c6ca28e1e142ea5fdbc8e55dd7b67d1a55009c179fe4e8e3ec3a02251e15`

Regenerating Verse1 through the recovered historical generator repeatedly reproduces that SHA-256 exactly.

## Frozen scoring semantics replay

The historical/current scoring-core Git blob is identical:

`ee62a86adc5f60119d00b5b57a25ee8f0b06f4fe`

A detached historical snapshot replay reported:

- target 17–96 professional reference opened: false;
- measures 97–113 opened: false;
- production modified: false;
- **sequence replay exact match: true (1051 events)**.

The sealed contextual runtime replay on the byte-identical recovered historical carrier further reproduces:

- base threshold: **0.27**;
- prune fraction: **0.15**;
- base event count: **765**;
- contextual selected event count: **651**;
- contextual selected event keys: **exact**;
- base score for every frozen selected event: **exact**;
- sequence score for every frozen selected event: **exact**;
- sequence-evidence flag for every frozen selected event: **exact**.

No tolerance fallback was introduced.

## Floating-point metadata disclosure

A dedicated arithmetic-reproducibility probe tested the remaining contextual keep-probability metadata.

Of 651 retained probabilities:

- **649 are bit-identical**;
- two differ only in the final IEEE-754 bits;
- maximum observed distance is **3 ULPs**;
- neither difference changes event ordering or the selected event set.

The two values are:

- measure 96, step 14: frozen `0.10314110104888881`, replayed `0.10314110104888885` (3 ULPs);
- measure 96, step 15: frozen `0.2609129927730226`, replayed `0.26091299277302255` (1 ULP).

This checkpoint therefore **does not claim byte-identical JSON serialization** of the frozen contextual artifact. It claims unchanged frozen scoring semantics and exact discrete predictions on the exact recovered historical carrier. No comparison tolerance was weakened or used to manufacture a pass.

## Consolidated research scope

- **17–32:** historical/reference-free provenance gap resolved by newly recovered authoritative historical evidence;
- **33–96:** existing strict reference-free replay/freeze closure retained;
- **97–113:** existing one-shot reserve closure retained;
- **17–113:** consolidated research evidence closure passed.

Supporting artifacts:

- `debug/v143-contextual-prune/measure-17-32-evidence-gap-resolution.json`
- `debug/v143-contextual-prune/research-evidence-closure-17-113.json`
- `debug/v143-contextual-prune/contextual-numeric-repro-diagnostic.json`
- `debug/v143-contextual-prune/research-evidence-closure.json`

## Production boundary

The existing contextual-prune promotion checkpoint remains authoritative for production integration.

This research closure does not make contextual-prune output a direct drop-in replacement for the live selected-row ranker. A separate shadow/canary integration path remains required before production can be considered.

Preserved invariants:

- professional reference opened by replay: false;
- runtime labels required: false;
- thresholds modified: false;
- comparison tolerances weakened: false;
- frozen model modified: false;
- frozen predicted event set modified: false;
- live endpoint deployed or modified: false;
- production modified: false;
- production promotion allowed: false.

## Next authorized research step

Build a continuous **1–113 research-only execution/replay harness** by joining the existing frozen intro machinery to this closed 17–113 chain.

The intro's historical roles must remain explicit:

- measures 1–8: training;
- measures 9–12: validation;
- measures 13–16: diagnostics.

The 1–113 runner must not retrain any model or reinterpret those measures as a single untouched holdout set. It must validate clean handoffs, including 16→17 and 96→97, and preserve all frozen model/threshold/reference-free/production constraints.
