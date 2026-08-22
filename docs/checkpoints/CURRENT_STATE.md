# CURRENT STATE — V143 contextual-prune / fresh intro compatibility producer

Updated: 2026-08-22 (detailed continuation plan added)
Branch: `v143-contextual-prune-lobo`
Branch HEAD before this documentation-only update: `f4ff8af9ad78abebb0aaaf0d48349a54fc640a8f`
Producer implementation commit: `def3b90e28bc3c7585fe004d4a7c6750dcb1cb0e`
Historical source commit: `4d735846fbd834cc4c722f2cb48727e4629647f1`
Previous exhaustive compatibility checkpoint: this file at commit `4a8c6627aa88b953364beb4b8a433278ff87a1b4`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

The implementation task from the earlier checkpoint is complete: the isolated fresh compatibility producer exists, has been statically validated, and is committed **without having executed Modal/GPU**.

The current stop condition is deliberate:

> Do not execute the fresh GPU compatibility capture merely because this checkpoint was updated. A future turn must explicitly continue into execution.

When execution is explicitly continued, the goal is **one fresh, fully fingerprinted compatibility capture** followed by the already-committed offline comparator. The result may classify compatibility with known current/research separator families, but it must never be described as recovered historical intro provenance or a bit-exact historical replay.

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

The producer source was also parsed/compiled without importing the producer or invoking Modal.

No Modal/GPU compatibility run has occurred in this phase.

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

That one call runs the frozen seeded graph:

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

`modelPayloadCaptureComplete` becomes true only if both requested separator model identifiers are actually present in the captured model-cache manifest. Missing model identity is not guessed or filled in; it remains visibly incomplete and the comparator fails closed.

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

The later offline comparator should additionally write:

- `comparison.json`

The producer does not write the historical Codespace snapshot, evidence-gap artifact, design contract, public training/calibration paths, or production artifacts.

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

Comparator exit behavior:

```text
0 = comparison completed and primary result is COUNT_COMPATIBLE_ONLY or INTRO_CACHE_EXACT_COMPATIBLE
1 = comparison completed but primary result is INCOMPLETE_CAPTURE or INCOMPATIBLE
2 = comparator could not complete because of input/file/schema/JSON error
```

An exit code is not itself a provenance conclusion; always inspect `comparison.json`.

---

## Non-negotiable constraints for every next turn

- Work only on `v143-contextual-prune-lobo`.
- Do not modify `main`.
- Do not modify production code/artifacts or live endpoints.
- Do not retrain or replace frozen V143 models.
- Do not change frozen predictions, thresholds, tolerances, timing phase, or 244-row intro geometry.
- Do not use a professional/reference transcription at runtime.
- Do not overwrite preserved historical evidence.
- Do not restart broad historical archaeology unless a genuinely new historical record appears.
- Do not run a second separator pass to “confirm” or replace the first capture.
- Do not edit a fresh run directory after capture merely to make the comparator pass.
- Do not call a fresh Family A/B match historical intro provenance.
- Do not treat intro compatibility as production authorization.

---

# Detailed next steps — authoritative continuation plan

## Phase 0 — Current stop point

**STOP BEFORE GPU EXECUTION unless the user explicitly continues into the fresh compatibility run.**

The current repository state is intentionally ready-but-unexecuted. Updating this checkpoint does not authorize Modal/GPU execution.

When a future turn explicitly says to continue, proceed through the phases below in order. Do not skip a failed gate.

---

## Phase 1 — Re-establish repository identity before doing anything expensive

1. Re-read `docs/checkpoints/CURRENT_STATE.md` from `v143-contextual-prune-lobo`.
2. Verify the active branch is still `v143-contextual-prune-lobo`.
3. Record the branch HEAD that will be captured in the fresh manifest.
4. Confirm these files still exist at that HEAD:
   - `analyzer/v143_intro_compatibility_fresh_capture.py`
   - `analyzer/v143_intro_compatibility_fresh_capture_static_check.py`
   - `analyzer/v143_intro_compatibility_comparator.py`
   - `debug/v143-contextual-prune/intro-compatibility-comparator-design.json`
   - `debug/v143-contextual-prune/intro-separator-family-evidence-gap.json`
   - `analyzer/v143-intro-1-16-evidence/codespace-snapshot/intro-raw-attack-cache.json`
5. Confirm the preserved historical raw-cache SHA-256 is still:

   `698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9`

6. Confirm the source audio Git blob is still:

   `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

**Stop immediately** if branch, source identity, historical baseline integrity, or expected files differ unexpectedly.

---

## Phase 2 — Re-run the static fail-closed validation

Before the first GPU call, execute the committed static validator locally/offline:

```bash
python analyzer/v143_intro_compatibility_fresh_capture_static_check.py
```

Expected high-level result:

```text
passed: true
staticOnly: true
modalOrGpuExecuted: false
```

Review failures rather than bypassing them.

Do **not** weaken or remove a static check just to get a green result. If a legitimate repository change caused a failure, understand and document it first.

If the producer source has changed since `def3b90e...`, recompute/review its SHA and checkpoint the reason before GPU execution.

---

## Phase 3 — Preflight the fresh-capture invariants

Immediately before execution, confirm all of the following are still true in the committed producer:

- only one `build_deterministic_v143_stems(...)` call exists;
- it uses seed 143;
- Demucs settings remain shifts=1, overlap=.10, segment=6;
- BS-RoFormer batch size remains 1;
- direct/cascade canonical names are unchanged;
- exactly the same returned direct/cascade files feed stem hashing and Basic Pitch intro capture;
- decoded PCM method remains `soundfile-int16-always2d-numpy-tobytes-sha256-v1`;
- measures remain 1–16;
- the 244-row guard is still active;
- historical wide-recall sweeps are unchanged;
- MIDI filter remains 40..88;
- wide tolerance remains 0.30 s;
- production annotation tolerance remains 0.10 s;
- professional reference is absent;
- run output is constrained to `debug/v143-contextual-prune/intro-compatibility-runs/<captureId>/`;
- no-overwrite checks remain active.

If any item fails, **do not execute Modal**.

---

## Phase 4 — Execute exactly one fresh compatibility capture

Only after Phases 1–3 pass, invoke the committed producer's `capture` local entrypoint **once** for the pinned source audio.

Important execution rules:

1. Use the committed producer unchanged.
2. Let it create a new unique capture ID/run directory unless there is a documented reason to supply a capture ID.
3. Do not reuse an existing capture directory.
4. Do not launch parallel duplicate captures.
5. Do not run a second separator build for comparison or confirmation.
6. Do not modify production or historical files before, during, or after the run.
7. Preserve the complete successful or failed fresh run evidence exactly as generated.

The producer itself should fail if the source audio, branch, 244-row geometry, separator graph shape, or output isolation invariants are violated.

---

## Phase 5 — Preserve and inventory the fresh run before interpreting it

After the fresh capture returns, identify the new directory:

`debug/v143-contextual-prune/intro-compatibility-runs/<captureId>/`

Expected files:

```text
fresh-capture.json
fresh-raw-attack-cache.json
package-inventory.txt
runtime-fingerprint.json
model-cache-manifest.json
```

Before running the comparator:

1. Confirm the directory is new and isolated.
2. Confirm no historical snapshot/training/evidence-gap file was overwritten.
3. Confirm `fresh-capture.json` and `fresh-raw-attack-cache.json` exist and are non-empty.
4. Confirm the raw cache SHA-256 in the manifest matches the actual fresh raw-cache bytes.
5. Keep the raw capture artifacts unchanged from this point forward.

If an execution log is available, preserve it with the run rather than relying only on terminal history.

---

## Phase 6 — Inspect capture completeness before compatibility claims

Read `fresh-capture.json` and explicitly inspect these groups.

### Capture identity

Require:

- non-empty `captureId`;
- UTC timestamp;
- expected branch/commit;
- source Git blob `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`;
- non-empty source SHA-256.

### Runtime identity

Require non-empty values for the comparator-required runtime fields, including:

- Python/platform;
- `audioSeparatorVersion` = `0.44.5`;
- Torch version;
- Torch CUDA version;
- cuDNN version;
- ONNX Runtime version/providers;
- GPU name;
- compute capability;
- NVIDIA driver;
- runtime fingerprint SHA-256.

Keep deterministic/TF32 flag values as observed. Do not normalize them to an expected answer after the fact.

### Dependency identity

Require:

- complete installed package inventory;
- non-empty package-inventory canonical digest.

### Model payload identity — hard gate

Inspect:

`modelPayloadCaptureComplete`

For a provenance-complete comparison it must be:

```text
true
```

Also verify the model-cache manifest contains the requested basename identities:

- `model_bs_roformer_ep_317_sdr_12.9755.ckpt`
- `htdemucs_6s.yaml`

If `modelPayloadCaptureComplete` is false, **stop classification at incomplete provenance**. Preserve the run and investigate why model-cache identity was not captured. Do not infer the missing hashes from filenames, package versions, Family A/B output equality, or later runs.

### Separator invocation

Require exact frozen recipe values and the recorded command graph. Confirm the producer observed exactly three underlying CLI commands belonging to one separator graph.

### Stem identity

Require direct/cascade:

- WAV SHA-256;
- decoded-PCM SHA-256;
- sample rate;
- frames;
- channels;
- exact pinned PCM hash method ID.

### Intro fingerprint

Require:

- raw cache SHA-256;
- raw event count;
- direct stem event count;
- cascade stem event count;
- all four sweep counts;
- grid row count of 244.

### Safety attestations

Require exactly:

```text
freshCompatibilityEvidenceOnly: true
historicalProvenanceClaimed: false
productionModified: false
liveEndpointModified: false
professionalReferenceUsedAtRuntime: false
historicalArtifactsOverwritten: false
```

Any violation is a stop condition.

---

## Phase 7 — Run the existing offline comparator

Only after preserving the run directory, run the comparator against the fresh manifest.

Canonical form:

```bash
python analyzer/v143_intro_compatibility_comparator.py \
  --capture debug/v143-contextual-prune/intro-compatibility-runs/<captureId>/fresh-capture.json \
  --output debug/v143-contextual-prune/intro-compatibility-runs/<captureId>/comparison.json
```

The comparator is authoritative for the compatibility classification. Do not hand-edit its output.

If it returns exit code 2, treat that as a comparator/input failure and fix only the underlying tooling/input issue; do not infer compatibility manually.

---

## Phase 8 — Interpret the comparator with the following decision table

### A. `INCOMPLETE_CAPTURE`

Meaning: required fresh provenance is missing.

Action:

- preserve the run;
- identify exactly which required fields/digests are missing;
- do not classify Family A/B unless the comparator itself emitted a valid family label under complete allowed conditions;
- do not rerun merely to search for a preferred output family;
- fix capture completeness only if there is a clear producer/environment cause, then checkpoint before deciding whether a second fresh run is justified.

Historical provenance remains open.

### B. `INCOMPATIBLE`

Meaning: at least one authenticated source/recipe/runtime/model/intro/safety invariant failed.

Action:

- preserve the run unchanged;
- identify the first/strongest failed check;
- separate environment/provenance mismatch from intro-event mismatch;
- do not weaken comparator expectations;
- do not promote anything to production.

Historical provenance remains open.

### C. `COUNT_COMPATIBLE_ONLY`

Meaning: authenticated intro event totals/per-stem/sweep counts agree, but fresh raw-cache bytes are not exact.

Action:

- report this as weaker compatibility evidence;
- inspect the cache difference before attributing it to separator family;
- keep any Family A/B label explicitly scoped to **current/research fresh output**;
- do not call this historical replay.

Historical provenance remains open.

### D. `INTRO_CACHE_EXACT_COMPATIBLE`

Meaning: fresh raw-attack cache bytes and authenticated intro fingerprint exactly match the historical cache.

Action:

- report this as strong intro compatibility evidence;
- report current/research Family A/B separately if the exact decoded-PCM pair matches;
- explicitly state that exact fresh cache compatibility still does **not** authenticate which separator family produced the historical intro cache because the historical whole-song identity link is missing.

Historical provenance remains open.

---

## Phase 9 — Interpret current/research Family A/B only from exact PCM pair equality

Family classification is allowed only if:

1. the manifest declares the exact pinned PCM hash method;
2. the provenance digest checks permit classification;
3. both decoded-PCM hashes equal one known pair.

Known pairs:

### Family A

```text
direct:  30cffcc2e472abe6d613b3853295c47b71ae8c4318f8709c8c9d45d69d9351f8
cascade: 68a1c75e59bf45fbae340938e580575c043e7a94a70e7be2361e4c2d4621cb56
```

Allowed wording:

`CURRENT_RESEARCH_FAMILY_A_COMPATIBLE`

### Family B

```text
direct:  1542856aca8275c727e6c77edd941588aa359b65b8b897c1b3ada2926f2d579e
cascade: e26f7a430b835adcd7a284db8a18c3aa93632b81e1c1a653eeffa16c02a62bc3
```

Allowed wording:

`CURRENT_RESEARCH_FAMILY_B_COMPATIBLE`

Forbidden wording includes:

- “historical intro Family A”;
- “historical intro Family B”;
- “historical family recovered”;
- “bit-exact historical raw-audio replay.”

If neither exact pair matches, report no known current/research family match. Do not invent Family C unless a separate research contract is created and proven.

---

## Phase 10 — Compare intro fingerprints in strength order

When summarizing the result, report evidence in this order:

1. provenance completeness/integrity;
2. source and frozen recipe equality;
3. decoded-PCM family classification, if any;
4. raw cache exact SHA equality;
5. rawEventCount equality;
6. direct/cascade filtered event-count equality;
7. four sweep-count equality;
8. 244-row grid preservation;
9. explicit statement that historical whole-song separator-family provenance remains open.

Historical reference values:

```text
raw cache SHA-256:
698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9

rawEventCount: 22270
direct:        11164
cascade:       11106

o015_f010:    12776
o020_f012:     4979
o025_f015:     2830
o030_f020:     1685

grid rows:       244
```

---

## Phase 11 — Do not jump from compatibility to production

Even a perfect outcome such as:

```text
INTRO_CACHE_EXACT_COMPATIBLE
+
CURRENT_RESEARCH_FAMILY_B_COMPATIBLE
```

would mean only:

- this fresh run is exact-compatible with the preserved historical intro raw cache; and
- this fresh run's separator PCM pair matches separately proven current/research Family B.

It would **not** prove that historical measures 1–16 were generated by Family B.

It also does **not** by itself authorize:

- production routing changes;
- endpoint deployment;
- model replacement;
- threshold changes;
- frozen-prediction changes;
- merging this research branch to `main`.

Any production consideration requires a separate explicit checkpoint and decision.

---

## Phase 12 — Checkpoint immediately after comparison

After the one fresh capture and offline comparison are complete, update this checkpoint again before doing anything else substantial.

That next checkpoint should record at minimum:

- branch HEAD used by the capture;
- capture ID;
- run directory;
- fresh-capture manifest SHA-256 if computed;
- fresh raw-cache SHA-256;
- direct/cascade WAV hashes;
- direct/cascade decoded-PCM hashes;
- model payload capture completeness;
- package/runtime/model digest integrity result;
- raw event/per-stem/four-sweep counts;
- grid row count;
- comparator primary classification;
- comparator Family A/B label, if any;
- comparator output path;
- whether any run or comparator failure occurred;
- explicit `historicalProvenanceClosed: false`;
- explicit `productionPromotionAllowed: false` unless separately authorized later.

Do not delete an inconvenient or incompatible run. Failed/incomplete runs are evidence and should remain auditable.

---

## Phase 13 — Only then decide whether further research is justified

After checkpointing the first fresh compatibility result:

- If exact-compatible: preserve as strong compatibility evidence and assess whether any remaining research question is actually actionable.
- If count-only compatible: localize byte/semantic differences without weakening the baseline.
- If incompatible: localize the first divergent provenance/fingerprint stage.
- If incomplete: repair evidence capture only when the missing provenance has a concrete fix.

A second fresh GPU run should **not** be automatic. It requires a specific reason such as validating a repaired provenance-capture defect, not fishing for a different separator family.

Broad historical archaeology should remain closed unless a genuinely new historical artifact appears.

---

## Compact next-turn instruction

If a future chat must resume quickly, use this sequence:

```text
1. Read docs/checkpoints/CURRENT_STATE.md on v143-contextual-prune-lobo.
2. Verify branch/source/historical-cache identity.
3. Run the static producer validator; require PASS.
4. If and only if the user explicitly authorized execution, run exactly one fresh compatibility capture.
5. Preserve the new isolated run directory unchanged.
6. Require modelPayloadCaptureComplete=true and inspect all provenance fields.
7. Run v143_intro_compatibility_comparator.py offline and save comparison.json in the same run directory.
8. Report the comparator classification and any CURRENT_RESEARCH_FAMILY_A/B_COMPATIBLE label without closing historical provenance.
9. Update CURRENT_STATE.md immediately.
10. Stop before any production action.
```

## Current bottom line

The compatibility producer is implemented and statically green. The historical measures 1–16 evidence gap is still preserved correctly. No fresh compatibility GPU execution has occurred yet.

**The next technical experiment is ready, but remains intentionally unexecuted until explicitly continued.**
