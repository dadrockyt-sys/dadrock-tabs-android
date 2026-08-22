# CURRENT STATE — V143 contextual-prune / exact fresh intro compatibility

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

The single authorized fresh intro compatibility capture has now been completed and preserved. **Do not run another separator/GPU compatibility capture.** The one-shot evidence is auditable and must remain unchanged.

The fresh capture achieved the strongest result allowed by the committed compatibility contract:

```text
INTRO_CACHE_EXACT_COMPATIBLE
CURRENT_RESEARCH_FAMILY_A_COMPATIBLE
```

This means the fresh measures 1–16 raw-attack cache bytes and every authenticated intro fingerprint exactly match the preserved historical cache, and the fresh direct/cascade decoded-PCM pair exactly matches known current/research Family A.

It **does not** authenticate which separator family generated the historical intro cache because the missing historical whole-song output identity has still not been recovered.

Therefore these remain explicit and non-negotiable:

```text
historicalProvenanceClosed: false
historicalIntroFamilyAuthenticated: false
productionPromotionAllowed: false
```

Production promotion remains disabled. No production code, live endpoint, frozen V143 model, threshold, prediction, tolerance, timing phase, or professional-reference behavior was modified by this work.

---

## One-shot execution record

One-shot GitHub Actions harness:

`.github/workflows/v143-intro-compatibility-fresh-capture-once.yml`

Harness commit / capture branch HEAD:

`1e0fc5eb6f0a4c98557769d37b5d0ba5233e8c75` — `Add one-shot V143 intro compatibility capture workflow`

Preserved research-artifact commit:

`b72f8939ea93d10c50e08e731dfb8c59311410c1` — `Record V143 intro fresh compatibility capture`

Capture ID:

`gha-32594407449-1-1e0fc5eb6f0a`

Run directory:

`debug/v143-contextual-prune/intro-compatibility-runs/gha-32594407449-1-1e0fc5eb6f0a/`

The one-shot harness performed, in order:

1. branch/source/historical-baseline identity checks;
2. committed static fail-closed validation;
3. explicit producer invariant preflight;
4. exactly one Modal fresh compatibility capture;
5. artifact inventory and SHA-256 preservation;
6. the committed offline comparator;
7. research-boundary assertions;
8. preservation of the complete fresh run on this branch.

No second separator graph was launched. No run or comparator failure occurred.

---

## Capture artifact integrity

Fresh capture manifest:

`debug/v143-contextual-prune/intro-compatibility-runs/gha-32594407449-1-1e0fc5eb6f0a/fresh-capture.json`

SHA-256:

`d1526bc90f177096d5546e7a13d66dd98cbd4d00e4cb468eadad951277ac9f87`

Fresh raw-attack cache:

`debug/v143-contextual-prune/intro-compatibility-runs/gha-32594407449-1-1e0fc5eb6f0a/fresh-raw-attack-cache.json`

SHA-256:

`698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9`

That raw-cache SHA-256 is **exactly identical** to the preserved historical measures 1–16 cache SHA-256.

Additional fresh artifact SHA-256 values:

```text
package-inventory.txt      032d25321a46843d3abcfaee1fe8cb4e8ea0a158eceb02bbf9dc9586d1e265ca
runtime-fingerprint.json   13b5fccf1e104cd8088b6de3dfd7f640346a00f0c7f79a809381380b07398b8b
model-cache-manifest.json  7066977959954628bc3f614c1f7c6ee33ef11a0ff78331593ad1ac7586bd9cc0
```

Run inventory:

`debug/v143-contextual-prune/intro-compatibility-runs/gha-32594407449-1-1e0fc5eb6f0a/SHA256SUMS.txt`

---

## Fresh runtime and provenance identity

Source audio Git blob remained pinned and matched:

`5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

Source audio SHA-256:

`215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

Runtime fingerprint digest:

`eb86c72e209fe228dc36723053cb14ddc5819f87f92f1059001aa964529fc468`

Installed-package inventory digest:

`e65d3075d3c7cc93b5ee0b616495dadd84bdfcd4bc72e081e272ba651b002230`

Model-cache manifest canonical digest:

`78805bcba2b5f2b97d047b416af93d7f2bd7b07938eca0a9a2145c3beb967637`

Model payload capture:

```text
modelPayloadCaptureComplete: true
requested model identifiers present: true
```

Requested separator model identities were captured in the manifest:

```text
model_bs_roformer_ep_317_sdr_12.9755.ckpt
htdemucs_6s.yaml
```

Comparator package/runtime/model provenance digest integrity result:

```text
passed: true
```

Fresh runtime included:

```text
Python 3.11.12
audio-separator 0.44.5
NVIDIA L4
CUDA 13.0
ONNX Runtime 1.28.0
```

The exact runtime fingerprint is preserved in the run directory; do not generalize those versions into a historical-runtime claim.

---

## Fresh separator identity

The producer executed the frozen seeded graph exactly once:

```text
seed 143
Demucs Guitar shifts=1 overlap=.10 segment=6
BS-RoFormer Instrumental batch=1
then Demucs Guitar shifts=1 overlap=.10 segment=6
```

Recorded graph command count:

`3`

Decoded-PCM convention:

`soundfile-int16-always2d-numpy-tobytes-sha256-v1`

Direct stem:

```text
WAV SHA-256:
afd1037bc7d62572ac9b99644d13d95b8593e25b4f442aa4a8f85c1111d97c78

Decoded PCM SHA-256:
30cffcc2e472abe6d613b3853295c47b71ae8c4318f8709c8c9d45d69d9351f8

sample rate: 44100
frames: 9324544
channels: 2
```

Cascade stem:

```text
WAV SHA-256:
44e0fe8874b07bcd4bca7e28f4a512b61214061f6bbf8771426c1b1237ffa201

Decoded PCM SHA-256:
68a1c75e59bf45fbae340938e580575c043e7a94a70e7be2361e4c2d4621cb56

sample rate: 44100
frames: 9324544
channels: 2
```

The decoded-PCM pair is an exact match for the previously authenticated **current/research Family A** pair. The permitted label is therefore only:

`CURRENT_RESEARCH_FAMILY_A_COMPATIBLE`

Do not rename this to “historical Family A,” “historical intro Family A,” or equivalent.

---

## Exact measures 1–16 intro result

Fresh raw-cache SHA-256:

`698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9`

Preserved historical raw-cache SHA-256:

`698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9`

Exact equality: **yes**.

Fresh fingerprint:

```text
rawEventCount: 22270
directStemEventCount: 11164
cascadeStemEventCount: 11106

o015_f010: 12776
o020_f012: 4979
o025_f015: 2830
o030_f020: 1685

gridRowCount: 244
```

Every count above exactly equals the preserved historical fingerprint.

The fresh raw-attack cache bytes themselves also exactly match, so this is stronger than count compatibility alone.

---

## Authoritative comparator result

Comparator output:

`debug/v143-contextual-prune/intro-compatibility-runs/gha-32594407449-1-1e0fc5eb6f0a/comparison.json`

Run summary:

`debug/v143-contextual-prune/intro-compatibility-runs/gha-32594407449-1-1e0fc5eb6f0a/run-summary.json`

Comparator exit code:

`0`

Primary classification:

`INTRO_CACHE_EXACT_COMPATIBLE`

Compatibility labels:

```text
CURRENT_RESEARCH_FAMILY_A_COMPATIBLE
INTRO_CACHE_EXACT_COMPATIBLE
```

Comparator gates:

```text
freshCaptureCompleteness.passed: true
historicalBaselineIntegrity.passed: true
sourceRecipeCompatibility.passed: true
freshProvenanceDigestIntegrity.passed: true
decodedPcmHashConventionCompatibility.passed: true
safetyAttestations.passed: true
introCountCompatibility.passed: true
introCacheExactCompatibility.passed: true
```

Explicit comparator boundary:

```text
historicalProvenanceClosed: false
historicalIntroFamilyAuthenticated: false
productionPromotionAllowed: false
```

---

## Historical evidence gap remains open

The authoritative evidence-gap artifact remains:

`debug/v143-contextual-prune/intro-separator-family-evidence-gap.json`

Status remains:

`EVIDENCE_GAP`

The new exact fresh result is powerful compatibility evidence, but it is not a surviving historical whole-song separator identity. Therefore it cannot close the missing lineage link by itself.

In particular, the following inference remains forbidden:

> “Because the fresh Family A run reproduced the historical intro cache exactly, the historical intro must have been generated by Family A.”

That would exceed the evidence. A historical Family A attribution would require a genuinely surviving historical record that independently binds the historical intro cache to the historical whole-song Family A output identity.

Do not restart broad historical archaeology unless a genuinely new historical record appears.

---

## Production boundary remains closed

This compatibility result does **not** authorize production promotion.

Do not:

- modify `main`;
- deploy or change a live endpoint;
- retrain or replace frozen V143 models;
- change frozen predictions, thresholds, tolerances, timing phase, or the 244-row intro geometry;
- use a professional/reference transcription at runtime;
- rewrite or delete the fresh run because of its conclusion;
- run another fresh separator compatibility capture;
- treat current/research Family A compatibility as authenticated historical Family A provenance;
- treat intro compatibility as production authorization.

Any future production consideration requires a separate explicit checkpoint and decision.

---

## Current stop point / next-turn directive

The planned one-shot fresh compatibility experiment is **complete**.

There is no remaining GPU task in this compatibility plan. Do not rerun the capture for confirmation; doing so would violate the one-shot evidence contract.

On the next turn, first re-read this file and verify the branch is still `v143-contextual-prune-lobo`.

Then:

- preserve the completed run unchanged;
- keep the historical separator-family gap open unless genuinely new historical evidence is found;
- keep production promotion disabled unless the user explicitly starts a separate production-readiness/promotion decision;
- prefer offline/auditable follow-up work over any new separator execution.

If the user simply says “continue” with no new scope, the safest useful next step is to evaluate what additional **offline evidence or validation** can be extracted from the now-exact compatibility result without reopening the separator run, changing production, or claiming historical provenance.
