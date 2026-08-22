# CURRENT STATE — V143 contextual-prune / intro compatibility capture

Updated: 2026-08-22 02:30 CDT
Branch: `v143-contextual-prune-lobo`
Branch HEAD immediately before this checkpoint update: `5e91ef46eb906c86ff3988a2f4a09b0d8e91a440`
Historical source commit: `4d735846fbd834cc4c722f2cb48727e4629647f1`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

The historical measures 1–16 archaeology has reached its safe stop condition. Do not restart broad searches and do not reinterpret a fresh GPU run as recovered historical provenance.

The exact next implementation task is:

> Create the isolated, research-only fresh compatibility producer `analyzer/v143_intro_compatibility_fresh_capture.py`, statically validate it, and checkpoint it **without executing Modal/GPU yet**.

After that producer is reviewed and fail-closed, a later explicitly approved run may create new compatibility evidence. A fresh run can classify compatibility with known current/research separator families, but it cannot by itself close the missing historical intro-family provenance link.

---

## Non-negotiable safety constraints

- Work only on `v143-contextual-prune-lobo`.
- Do not modify `main`.
- Do not modify production code or production artifacts.
- Do not deploy or modify live endpoints.
- Do not retrain or replace the frozen V143 model.
- Do not modify frozen predictions.
- Do not weaken thresholds or score-comparison tolerances.
- Do not introduce professional/reference labels into runtime or provenance replay.
- Preserve historical median-onset behavior.
- Preserve the original historical measures 1–16 boundary and the **244-row** grid; do not synthesize a 256-row rectangle.
- Do not overwrite preserved historical caches or evidence files.
- Do not call fresh/current separator output a “bit-exact historical replay.”
- Do not call a fresh Family-B match “historical intro Family B.”
- Do not run Modal merely to recreate missing historical evidence.
- Codespaces are not required for the current path.

Production promotion remains disabled.

---

## Historical measures 1–16 evidence that is closed

### Historical source/artifact chain

The historical first-party measures 1–16 producer graph is archived and checksum-manifested under:

- `analyzer/v143-intro-1-16-evidence/historical-source-4d735846/`
- `analyzer/v143-intro-1-16-evidence/codespace-snapshot/`

Static source/artifact equivalence is PASSING.

Key historical dimensions:

```text
raw attack count:          22270
intro grid rows:             244
onset count:                 787
onset vector count:         4722
grid feature count:           36
sequence feature count:      260
contextual carrier count:     15
runtime reference dependency: none
```

Historical timing has `firstBeatInMeasure=3`, so measure 1 contains only steps 12–15.

### Source audio identity

`public/gomywayfullaitest.m4a` has the same Git blob at the historical source ref and the current research branch:

`5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

Changed source audio is therefore ruled out as an explanation for separator-family differences.

### Preserved intro raw-attack cache

Preserved cache:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/intro-raw-attack-cache.json`

SHA-256:

`698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9`

Historical measures 1–16 fingerprint:

```text
rawEventCount: 22270

direct-demucs6s-guitar.wav:      11164
bsroformer-demucs6s-guitar.wav:  11106

o015_f010: 12776
o020_f012:  4979
o025_f015:  2830
o030_f020:  1685
```

These per-stem counts are measured **after** Basic Pitch parsing, guitar-range filtering, wide-grid acceptance, and measures 1–16 filtering. They are not whole-song stem hashes.

### Frozen historical separator recipe

The source-proven two-view recipe is:

1. direct Demucs6s Guitar;
2. BS-RoFormer Instrumental -> Demucs6s Guitar.

Frozen settings:

```text
seed: 143
Demucs shifts: 1
Demucs overlap: 0.10
Demucs segment size: 6
RoFormer batch size: 1
Demucs model identifier: htdemucs_6s.yaml
BS-RoFormer identifier: model_bs_roformer_ep_317_sdr_12.9755.ckpt
audio-separator: 0.44.5
```

Canonical stem filenames:

- `direct-demucs6s-guitar.wav`
- `bsroformer-demucs6s-guitar.wav`

The original historical downloaded model payload hashes remain unauthenticated.

### Historical-era Modal execution existence

Historical Modal execution is **not** in doubt. Preserved Aug-16 Codespace-era evidence confirms Modal remote execution and a successful L4 dependency smoke.

Observed smoke fingerprint included:

```text
torch: 2.13.0+cu130
torch CUDA: 13.0
GPU: NVIDIA L4
audio-separator CLI exit: 0
ONNX providers included TensorRT, CUDA and CPU
```

The remaining evidence gap is not “did Modal run?”; it is the missing retained output identity that would bind the historical intro raw-attack cache to a whole-song separator PCM family.

---

## Historical intro separator-family evidence gap — KEEP OPEN

Authoritative gap artifact:

`debug/v143-contextual-prune/intro-separator-family-evidence-gap.json`

Status remains `EVIDENCE_GAP`.

Targeted archaeology did **not** recover:

- historical seeded repeatability pass-1 `carrierA` / `carrierB` output hashes;
- historical seeded repeatability pass-2 `carrierA` / `carrierB` output hashes;
- the historical cascade benchmark WAV file SHA for `public/separator-benchmark-v2/gomyway-bsroformer-demucs6s-guitar.wav`;
- a historical intro capture record containing the whole-song direct/cascade WAV or decoded-PCM hashes;
- an immutable original historical Modal image digest;
- authenticated original BS-RoFormer downloaded payload SHA-256;
- authenticated original Demucs downloaded payload/config SHA-256.

Therefore:

- do **not** claim the intro cache was Family B because later Section3 was Family B;
- do **not** claim historical intro Family A or Family B from a fresh run;
- do **not** use output-level agreement alone as raw provenance closure.

The broad archaeology is exhausted. Only a genuinely new surviving historical record would justify reopening it.

---

## Known research separator families

Later Section3 research proved two decoded-PCM families under nominally equivalent L4 execution.

### Family A

```text
direct decoded PCM SHA-256:
30cffcc2e472abe6d613b3853295c47b71ae8c4318f8709c8c9d45d69d9351f8

cascade decoded PCM SHA-256:
68a1c75e59bf45fbae340938e580575c043e7a94a70e7be2361e4c2d4621cb56
```

### Family B

```text
direct decoded PCM SHA-256:
1542856aca8275c727e6c77edd941588aa359b65b8b897c1b3ada2926f2d579e

cascade decoded PCM SHA-256:
e26f7a430b835adcd7a284db8a18c3aa93632b81e1c1a653eeffa16c02a62bc3
```

Section3 exact Family-B evidence reproduced the historical 49–64 carrier and exact frozen decisions/scores. This is valid Section3 provenance evidence, not an intro lineage bridge.

### Exact decoded-PCM hash convention — RECOVERED

The Family A/B hashes above were generated by:

```python
import hashlib
import soundfile as sf

audio, sample_rate = sf.read(
    str(path),
    dtype="int16",
    always_2d=True,
)
pcm_sha256 = hashlib.sha256(audio.tobytes()).hexdigest()
```

This exact convention is now part of the intro compatibility contract.

A fresh manifest must declare:

`SOUNDFILE_INT16_ALWAYS_2D_TOBYTES_SHA256`

The comparator must refuse Family A/B classification if the declared method differs.

---

## Compatibility work completed on this branch

Historical provenance remains open, so all new work is explicitly labelled **fresh compatibility evidence only**.

### Design contract

File:

`debug/v143-contextual-prune/intro-compatibility-comparator-design.json`

The contract defines:

- read-only historical baselines;
- required fresh source/runtime/dependency/model/stem identities;
- the recovered decoded-PCM hashing convention;
- exact intro fingerprint comparison;
- allowed compatibility labels;
- forbidden historical conclusions;
- production/reference-free invariants;
- fail-closed behavior when required provenance is missing.

Recent contract hardening commits include:

- `5ce0e15cd4e817f4d33cdc2d391677a701ca3099`
- `868adaed6dac29cd40429c7ac0a00fc2e664038a`

### Offline comparator

File:

`analyzer/v143_intro_compatibility_comparator.py`

The comparator itself does **not** run Modal or a separator.

It consumes a fresh-capture manifest and checks only authenticated historical invariants.

It now:

- verifies preserved historical cache integrity;
- verifies source Git blob and frozen recipe;
- requires the exact decoded-PCM hashing method for Family classification;
- verifies fresh safety attestations;
- recomputes package inventory/runtime/model-cache manifest digests instead of blindly trusting manifest-provided hashes;
- fails closed for missing required provenance;
- never closes historical provenance from fresh compatibility evidence.

Latest comparator hardening commit before this checkpoint:

`5e91ef46eb906c86ff3988a2f4a09b0d8e91a440` — `Verify V143 runtime and model capture digests`

Other recent comparator/safety commits:

- `80440fa55a7bbfeaa4382f170abc620e2fe86056`
- `93e3fca004e55e082e54ad4280fcf7507684033c`

### Fresh-capture template

File:

`debug/v143-contextual-prune/intro-compatibility-fresh-capture.template.json`

The template is intentionally incomplete/fail-closed until a producer supplies real captured evidence.

Latest template hardening commit:

`3ac883269caf52d195dc6417da19dd2fa9f33d38`

### Compatibility labels

Permitted labels include:

- `INCOMPLETE_CAPTURE`
- `INCOMPATIBLE`
- `COUNT_COMPATIBLE_ONLY`
- `INTRO_CACHE_EXACT_COMPATIBLE`
- `CURRENT_RESEARCH_FAMILY_A_COMPATIBLE`
- `CURRENT_RESEARCH_FAMILY_B_COMPATIBLE`

Downstream exact-compatibility classification remains disabled until expected historical downstream digests are independently authenticated and pinned.

Forbidden conclusions include:

- `historical-provenance-closed`
- `historical-intro-family-A-proven`
- `historical-intro-family-B-proven`
- `bit-exact-historical-raw-audio-replay`
- `production-ready-by-compatibility-alone`

---

## Current implementation state

The compatibility **design**, **offline comparator**, and **fresh-capture template** are committed.

The actual isolated producer is **not yet implemented**:

`analyzer/v143_intro_compatibility_fresh_capture.py`

No fresh compatibility GPU run has been performed in this phase.

No Modal execution should occur until the producer exists and has been statically reviewed against the contract.

---

## Exact next implementation steps

### Step 1 — Create the isolated fresh-capture producer

Create:

`analyzer/v143_intro_compatibility_fresh_capture.py`

The producer must be research-only and must not import or mutate production routing/deployment behavior.

### Step 2 — Use one separator pass for all fresh identities

One fresh separator execution must provide the canonical direct/cascade stems used for **both**:

- stem WAV/decoded-PCM identity capture; and
- the measures 1–16 Basic Pitch raw-attack cache.

Do not run one separation for hashes and another separation for the intro fingerprint; that would break the provenance chain.

Use the frozen seeded recipe:

```text
seed 143
Demucs Guitar shifts=1 overlap=.10 segment=6
BS-RoFormer Instrumental batch=1
then Demucs Guitar shifts=1 overlap=.10 segment=6
```

### Step 3 — Capture source and execution identity before downstream analysis

The fresh run must record at minimum:

- capture ID and UTC timestamp;
- branch/commit;
- source Git blob SHA;
- source file SHA-256;
- Python version;
- `audio-separator` version;
- Torch / CUDA / cuDNN;
- ONNX Runtime version and providers;
- GPU name / compute capability / NVIDIA driver;
- deterministic algorithm flags and TF32 flags;
- complete installed package inventory plus independently recomputable inventory digest;
- model-cache file manifest plus independently recomputable manifest digest;
- detected BS-RoFormer and Demucs model/config payload hashes when identifiable;
- exact separator command/config/seed values.

The full fresh-capture manifest must be saved **before** any optional downstream comparison so provenance cannot be lost again.

### Step 4 — Capture canonical stem identities

For both canonical stems record:

- WAV file SHA-256;
- decoded-PCM SHA-256 using exactly `SOUNDFILE_INT16_ALWAYS_2D_TOBYTES_SHA256`;
- sample rate;
- frame count;
- channel count;
- decoded sample/value count as required by the manifest contract.

Family A/B is only a current research classification from exact decoded-PCM pair equality.

Never rewrite `CURRENT_RESEARCH_FAMILY_B_COMPATIBLE` as “historical intro Family B.”

### Step 5 — Build the fresh intro cache from those exact stems

Reuse the historical measures 1–16 producer semantics:

- reference-free timing;
- original bar phase;
- exact 244-row intro grid;
- historical wide-recall sweeps;
- guitar MIDI 40..88;
- 0.30 s wide-grid acceptance;
- measures 1–16 filter;
- 0.10 s production-grid annotation;
- canonical direct/cascade stem names;
- no professional reference.

Record:

- fresh raw-attack cache SHA-256;
- raw event count;
- direct/cascade stem event counts;
- four sweep counts.

### Step 6 — Write only to an isolated run directory

Use a new run-specific directory such as:

`debug/v143-contextual-prune/intro-compatibility-runs/<captureId>/`

Recommended contents:

- `fresh-capture.json`
- `intro-raw-attack-cache.json`
- `package-inventory.txt`
- `runtime-fingerprint.json`
- `model-cache-manifest.json`
- optional full execution log

Do not overwrite:

- the historical Codespace snapshot;
- the evidence-gap artifact;
- the design contract;
- historical training/calibration files.

### Step 7 — Add static safety validation before any GPU execution

Before Modal is run, validate that the producer:

- writes only under the isolated compatibility run path;
- has no production deployment/routing calls;
- does not open a professional reference;
- does not retrain models;
- does not change thresholds/tolerances;
- does not overwrite historical artifacts;
- records the required attestations as false/true exactly as the comparator expects;
- uses the recovered decoded-PCM hash convention.

Commit this producer and static validation first.

### Step 8 — Stop before execution unless explicitly continuing

After implementation/static validation, checkpoint again.

A future run may then be performed as **fresh compatibility evidence only**. Its result must be passed through `analyzer/v143_intro_compatibility_comparator.py` offline.

---

## What not to redo

Do not restart work on:

- measures 33–113 provenance closure;
- Section3 exact-family reconstruction;
- source-audio identity;
- the 36/260/15 feature-width proof;
- whether Aug-16 Modal execution occurred;
- broad Library searches for the seeded historical hashes;
- broad Codespace archaeology.

Those areas are already exhausted or closed.

---

## Current bottom line

Measures 33–113 remain research-closed/green.

Measures 1–16 have a source-proven, checksum-pinned first-party producer chain and exact preserved output fingerprint, but the final historical whole-song separator-family bridge is not recoverable from surviving evidence.

That gap is now intentionally preserved rather than weakened.

The branch has moved to a separate compatibility architecture: a read-only comparator plus a future fully fingerprinted fresh producer. The comparator is hardened; the producer is the next unfinished task.

**Do not run Modal until `analyzer/v143_intro_compatibility_fresh_capture.py` has been implemented and statically validated.**
