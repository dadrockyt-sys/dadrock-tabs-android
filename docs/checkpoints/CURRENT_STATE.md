# CURRENT STATE — V143 contextual-prune / fresh intro compatibility producer

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Producer implementation commit: `def3b90e28bc3c7585fe004d4a7c6750dcb1cb0e`
Historical source commit: `4d735846fbd834cc4c722f2cb48727e4629647f1`
Previous exhaustive compatibility checkpoint: this file at commit `4a8c6627aa88b953364beb4b8a433278ff87a1b4`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

The exact implementation task from the previous checkpoint is complete: the isolated fresh compatibility producer now exists, has been statically validated, and has been committed **without executing Modal/GPU**.

Stop here unless a future turn explicitly continues into fresh GPU compatibility capture.

A future fresh run is **compatibility evidence only**. It may classify against known current/research separator families, but it must never be described as recovered historical intro provenance or a bit-exact historical replay.

Production promotion remains disabled.

---

## Newly completed work

### Fresh compatibility producer

Created:

`analyzer/v143_intro_compatibility_fresh_capture.py`

Producer SHA-256:

`320364c8955577dacafab9fd19afae1b960d76fd81654a2eb67beaba1a5c35eb`

Implementation commit:

`def3b90e28bc3c7585fe004d4a7c6750dcb1cb0e` — `Add V143 intro compatibility fresh-capture producer`

The producer is research-only. It does not modify production routing, deployment behavior, frozen predictions, thresholds, or models.

### Static safety validator

Created:

`analyzer/v143_intro_compatibility_fresh_capture_static_check.py`

Committed validation result:

`debug/v143-contextual-prune/intro-compatibility-fresh-capture-static-validation.json`

Static result:

```text
passed: true
staticOnly: true
modalOrGpuExecuted: false
```

The source was also parsed/compiled locally without importing the producer or invoking Modal.

No Modal/GPU compatibility run was performed during this implementation phase.

---

## Producer provenance architecture

### 1. Source and checkout identity are pinned

The local entrypoint refuses to run unless the checkout branch is exactly:

`v143-contextual-prune-lobo`

It records the current Git commit and verifies the source bytes for:

`public/gomywayfullaitest.m4a`

against the pinned source Git blob:

`5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

It also records the source file SHA-256 and verifies that the same source bytes arrive remotely.

### 2. Exactly one fresh separator graph is allowed

The producer contains exactly one call to:

`build_deterministic_v143_stems(...)`

That single call runs the frozen seeded graph:

```text
seed 143
Demucs Guitar shifts=1 overlap=.10 segment=6
BS-RoFormer Instrumental batch=1
then Demucs Guitar shifts=1 overlap=.10 segment=6
```

The three underlying CLI commands are intercepted and recorded for provenance.

The canonical files returned by this **same one separator graph** are reused for both:

- WAV and decoded-PCM stem identity capture; and
- measures 1–16 Basic Pitch raw-attack evidence.

There is no second separator build for the intro cache.

### 3. Exact decoded-PCM convention is pinned

The producer uses:

```python
audio, sample_rate = sf.read(str(path), dtype="int16", always_2d=True)
pcm_sha256 = hashlib.sha256(audio.tobytes()).hexdigest()
```

Manifest method ID:

`soundfile-int16-always2d-numpy-tobytes-sha256-v1`

For direct and cascade stems it records:

- WAV SHA-256;
- decoded-PCM SHA-256;
- sample rate;
- frame count;
- channel count.

### 4. Historical measures 1–16 cache semantics are preserved

The archived first-party producer was recovered from:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/v143_intro_capture_raw_attack_cache.py`

The fresh producer reuses its ordering and semantics:

- reference-free timing;
- original bar phase;
- measures 1–16 only;
- exact **244-row** intro grid, with a fail-closed row-count guard;
- guitar MIDI 40..88;
- historical four wide-recall sweeps;
- 0.30 s wide-grid acceptance;
- 0.10 s production-grid annotation;
- canonical direct/cascade stem ordering and names;
- no professional reference;
- historical event-field ordering;
- historical JSON serialization using `json.dumps(..., indent=2) + "\n"`.

The historical producer's `sourceDurationSeconds` lookup behavior is intentionally preserved: it queried `source_metadata.get("duration")`, while `modal_analyzer` exposes `durationSeconds`, so this field remains `null` as in the archived producer.

### 5. Runtime/dependency/model identity is fail-closed

The producer records:

- Python/platform;
- `audio-separator` version;
- Torch/CUDA/cuDNN;
- ONNX Runtime and providers;
- GPU name and compute capability;
- NVIDIA driver;
- deterministic-algorithm/CuDNN flags;
- TF32 flags;
- complete installed package inventory and canonical digest;
- runtime fingerprint and canonical digest;
- `/tmp/audio-separator-models` file manifest with file size and SHA-256;
- canonical model-cache manifest digest;
- requested BS-RoFormer and Demucs model identifiers;
- best-effort Basic Pitch model path/hash identity.

`modelPayloadCaptureComplete` is set true only if both requested separator model identifiers are actually present in the captured model-cache manifest. Missing model identity is not guessed or filled in; it remains visibly incomplete and the comparator will fail closed.

### 6. Output writes are isolated and no-overwrite

Fresh artifacts may only be written under:

`debug/v143-contextual-prune/intro-compatibility-runs/<captureId>/`

The producer rejects path escape and rejects pre-existing run/artifact paths.

A successful future run is designed to save:

- `fresh-capture.json`
- `fresh-raw-attack-cache.json`
- `package-inventory.txt`
- `runtime-fingerprint.json`
- `model-cache-manifest.json`

It does not write the historical Codespace snapshot, evidence-gap artifact, design contract, public training/calibration paths, or production artifacts.

---

## Static validation that passed

The committed validator confirms, without importing Modal code or executing a separator:

- branch pin is present;
- decoded-PCM method is exact;
- measures 1–16 boundary is exact;
- 0.30/0.10 historical grid tolerances are unchanged;
- exactly one `build_deterministic_v143_stems` call exists;
- exactly one local-entrypoint `.remote` capture call exists;
- the 244-row guard exists;
- SoundFile int16/always-2D/tobytes hashing exists;
- reference-free and comparator safety attestations are literal;
- isolated debug/no-overwrite write guards exist;
- forbidden historical/production write paths are absent;
- professional-reference modules are not imported;
- deploy/retrain/fit calls are absent;
- historical Basic Pitch/timing helpers are reused;
- historical cache byte serialization is preserved;
- one-graph/three-command capture is guarded;
- package/runtime/model provenance digests are captured;
- the design still keeps the historical evidence gap open.

Validation artifact producer SHA matches the committed producer SHA-256 above.

---

## Historical baseline remains unchanged

Preserved cache:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/intro-raw-attack-cache.json`

SHA-256:

`698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9`

Fingerprint:

```text
rawEventCount: 22270
direct-demucs6s-guitar.wav:      11164
bsroformer-demucs6s-guitar.wav:  11106

o015_f010: 12776
o020_f012:  4979
o025_f015:  2830
o030_f020:  1685
```

Historical timing has `firstBeatInMeasure=3`; measure 1 contains only steps 12–15 and the measures 1–16 grid has 244 rows.

Historical separator-family provenance remains intentionally open because no surviving historical whole-song output identity binds this intro cache to Family A or Family B.

Authoritative gap artifact:

`debug/v143-contextual-prune/intro-separator-family-evidence-gap.json`

Status remains `EVIDENCE_GAP*`.

---

## Known current/research separator families

Family A decoded-PCM pair:

```text
direct:  30cffcc2e472abe6d613b3853295c47b71ae8c4318f8709c8c9d45d69d9351f8
cascade: 68a1c75e59bf45fbae340938e580575c043e7a94a70e7be2361e4c2d4621cb56
```

Family B decoded-PCM pair:

```text
direct:  1542856aca8275c727e6c77edd941588aa359b65b8b897c1b3ada2926f2d579e
cascade: e26f7a430b835adcd7a284db8a18c3aa93632b81e1c1a653eeffa16c02a62bc3
```

A future exact pair match may be labelled only:

- `CURRENT_RESEARCH_FAMILY_A_COMPATIBLE`, or
- `CURRENT_RESEARCH_FAMILY_B_COMPATIBLE`.

It must not be renamed to “historical intro Family A/B.”

---

## Existing comparator remains authoritative

Offline comparator:

`analyzer/v143_intro_compatibility_comparator.py`

Design contract:

`debug/v143-contextual-prune/intro-compatibility-comparator-design.json`

Fresh template:

`debug/v143-contextual-prune/intro-compatibility-fresh-capture.template.json`

The comparator:

- does not run Modal;
- verifies preserved baseline integrity;
- verifies source/recipe identity;
- recomputes package/runtime/model digests;
- requires complete model payload capture;
- requires the exact decoded-PCM hash convention for Family classification;
- verifies intro counts/cache digest;
- verifies safety attestations;
- never closes historical provenance from fresh compatibility evidence.

Allowed primary compatibility results remain:

- `INCOMPLETE_CAPTURE`
- `INCOMPATIBLE`
- `COUNT_COMPATIBLE_ONLY`
- `INTRO_CACHE_EXACT_COMPATIBLE`

Current/research Family A/B labels may additionally be emitted when the exact decoded-PCM pair matches.

---

## Non-negotiable constraints for the next turn

- Work only on `v143-contextual-prune-lobo`.
- Do not modify `main`.
- Do not modify production code/artifacts or live endpoints.
- Do not retrain/replace frozen V143 models.
- Do not change frozen predictions, thresholds, tolerances, timing phase, or 244-row intro geometry.
- Do not use a professional/reference transcription at runtime.
- Do not overwrite preserved historical evidence.
- Do not restart broad historical archaeology unless a genuinely new historical record appears.
- Do not call a fresh result historical provenance closure.

---

## Exact next safe action

**STOP BEFORE GPU EXECUTION unless a future user turn explicitly continues.**

If explicitly continued, the next phase is:

1. re-read this checkpoint and verify branch HEAD;
2. re-run/inspect the committed static validator if desired;
3. execute exactly one fresh compatibility capture with the committed producer;
4. preserve the newly created isolated run directory unchanged;
5. inspect `modelPayloadCaptureComplete` and all provenance fields before drawing conclusions;
6. pass `fresh-capture.json` through `analyzer/v143_intro_compatibility_comparator.py` offline;
7. report compatibility strength and any current/research Family A/B label while keeping historical intro provenance open;
8. checkpoint again before any production consideration.

No Modal/GPU execution has occurred in this checkpointed phase.
