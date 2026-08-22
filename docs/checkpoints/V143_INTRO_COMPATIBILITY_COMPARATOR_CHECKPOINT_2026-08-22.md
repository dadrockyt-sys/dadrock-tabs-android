# V143 Intro Compatibility Comparator Checkpoint — 2026-08-22

Branch: `v143-contextual-prune-lobo`

## Scope

Continue the measures 1–16 historical producer recovery after the targeted separator-family archaeology reached its explicit fail-closed stop condition.

This checkpoint preserves the transition from **historical provenance archaeology** to **fresh compatibility evidence design**. It does not authorize historical-provenance claims from a fresh run.

## Archaeology result

The formal gap artifact already present on the branch is:

`debug/v143-contextual-prune/intro-separator-family-evidence-gap.json`

Status: `EVIDENCE_GAP`

Targeted searches were repeated against the surviving Aug-16 checkpoint and retained Library evidence for:

- `carrierA`
- `carrierB`
- seeded/repeatability output
- historical cascade benchmark SHA
- the intro `11164 / 11106` fingerprint paired with a whole-song stem identity

No missing historical pass hashes or direct intro-to-Family-A/B bridge were recovered.

The safe historical conclusion therefore remains unchanged:

- source audio identity is proven;
- the first-party measures 1–16 source/artifact chain is proven;
- the frozen 1/.10/6 + batch-1 separator recipe is proven;
- the intro raw-attack cache and event fingerprint are exact;
- the historical direct benchmark WAV SHA is recovered;
- later Section3 Family B is independently proven;
- the exact whole-song separator PCM family that produced the preserved intro cache is **not independently authenticated** from surviving retained output evidence.

Do not infer Family B backward into the intro solely from Section3.

## New compatibility design

Added:

`debug/v143-contextual-prune/intro-compatibility-comparator-design.json`

Commit:

`de83a6589d5e88ada55a122082f2228950ebf64b`

The contract requires a future fresh capture to retain:

- source Git/blob and audio SHA identity;
- complete runtime fingerprint;
- package inventory and package-inventory digest;
- BS-RoFormer and Demucs identifiers plus fresh payload hashes;
- exact frozen separator commands/settings;
- fresh WAV and decoded-PCM hashes for direct/cascade stems;
- intro raw-cache digest and exact event fingerprints;
- frozen downstream replay fields;
- explicit non-production/non-historical attestations.

Allowed results are compatibility classifications only. The design explicitly forbids conclusions such as `historical-provenance-closed`, `historical-intro-family-B-proven`, or `bit-exact-historical-raw-audio-replay` from fresh execution alone.

## Offline comparator implementation

Added:

`analyzer/v143_intro_compatibility_comparator.py`

Commit:

`1a1a110eed9d98280e9c879905933cfb363f1855`

The comparator itself does **not** invoke Modal or a separator.

It:

1. verifies the preserved historical raw-cache file against both the pinned SHA and `SHA256SUMS.txt`;
2. requires the evidence-gap state to remain explicit;
3. fails closed when a fresh capture omits required runtime/model/stem identity fields;
4. checks source-audio Git blob identity;
5. checks the frozen separator recipe and model identifiers;
6. checks `audio-separator==0.44.5` identity in the capture;
7. compares exact intro raw-event, per-stem and sweep fingerprints;
8. compares the fresh intro raw-cache digest against the preserved historical digest;
9. may label a fresh decoded-PCM pair as current/research Family A or Family B only when its exact known pair matches;
10. always leaves `historicalProvenanceClosed=false` and `productionPromotionAllowed=false`.

Downstream exact replay is intentionally not promoted by this comparator yet because an authenticated expected downstream decision/score digest pair has not been pinned into this new compatibility contract. The capture retains those fields for audit, but the comparator reports them as not yet evaluated rather than manufacturing an expected digest.

## Fail-closed fresh capture template

Added:

`debug/v143-contextual-prune/intro-compatibility-fresh-capture.template.json`

Commit:

`d3139ca601735358c460d373593929578b9100d2`

Unknown fresh values are `null`/empty by design, so passing the untouched template to the comparator must produce an incomplete-capture result rather than a false green result.

## Important fresh-run guard

Do **not** invoke the existing local entrypoint in:

`analyzer/v143_intro_capture_raw_attack_cache.py`

for a fresh compatibility run.

That historical capture script writes to:

`public/training/v143-musical-reconstruction-calibration/intro-raw-attack-cache.json`

A future compatibility run must instead use a new isolated output path under:

`debug/v143-contextual-prune/`

and must never overwrite the preserved historical cache or its Codespace snapshot.

The tracked historical remote function is still useful as source evidence for the exact Basic Pitch/timing/filtering behavior, but a new wrapper must capture fresh stem/runtime/model hashes before analysis and write only new research artifacts.

## Validation note

The new files were reviewed through GitHub after creation. No Codespace, Modal, GPU, production deployment, retraining or threshold/tolerance change was used in this phase.

The current tool environment does not expose the repository checkout locally, so no claim of an executed `py_compile` or comparator runtime test is made in this checkpoint. Do not silently convert static review into an executed-test claim.

## Current branch safety state

- branch isolated: yes
- production modified: no
- `main` modified: no
- live endpoint modified/deployed: no
- Modal run during this phase: no
- Codespace used during this phase: no
- professional reference used at runtime: no
- frozen model/predictions modified: no
- historical cache overwritten: no
- thresholds/tolerances changed: no

## Exact next safe action

Build a **new research-only fresh-capture producer** that writes only to `debug/v143-contextual-prune/intro-compatibility-fresh-capture.json` (or an equivalent run-specific path), captures all identity fields required by the design **before** any compatibility classification, and reuses the tracked historical producer logic without invoking its historical-cache-writing local entrypoint.

Before any fresh GPU execution, the new producer must prove by static inspection that:

- no historical cache path is writable;
- no production/live endpoint is modified;
- model payload and runtime/package identities are captured rather than assumed;
- the exact seed 143 / shifts 1 / overlap .10 / segment 6 / RoFormer batch 1 recipe is preserved;
- results are labelled fresh compatibility evidence only.

Only after those guards exist should a fresh L4 compatibility capture be considered.
