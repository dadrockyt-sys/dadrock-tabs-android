# V143 Contextual-Prune Recovery Checkpoint

Last updated: 2026-08-21
Repository: `dadrockyt-sys/dadrock-tabs-android`
Working branch: `v143-contextual-prune-lobo`

## Non-negotiable scope and safety rules

1. This branch remains research-only unless a later, explicit promotion gate proves a safe integration path.
2. Do not modify the frozen contextual-prune model, frozen predictions, thresholds, or comparison tolerances to make a replay pass.
3. Do not use the professional reference at runtime or in a reference-free provenance replay.
4. Do not modify or deploy the live V143 endpoint while closing research provenance.
5. Preserve original historical band boundaries. Do not substitute a monolithic 17-96 carrier for band-preserving provenance evidence.
6. Preserve current-container mismatch observations inside evidence artifacts; do not hide them when historical exact-family evidence is used.
7. Measures 17-32 are not yet claimed by the carrier-provenance closure.
8. Production promotion remains disabled.

## Section 3 exact historical Family-B closure — PASSED

Authoritative artifact:
- `debug/v143-contextual-prune/section3-exact-family-provenance-capture.json`

Historical Family B:
- direct PCM SHA256: `1542856aca8275c727e6c77edd941588aa359b65b8b897c1b3ada2926f2d579e`
- cascade PCM SHA256: `e26f7a430b835adcd7a284db8a18c3aa93632b81e1c1a653eeffa16c02a62bc3`
- exact worker: 1
- canonical stem filenames: `direct-demucs6s-guitar.wav`, `bsroformer-demucs6s-guitar.wav`
- carrier rows: 802
- raw events: 20,830
- candidate clusters: 9,048
- exact carrier semantics: true
- exact capture diagnostics: true
- exact frozen decision set: true
- exact base scores: true
- exact sequence scores: true
- exact keep probabilities: true

Strict invariants remain intact: no weakened comparison, no threshold/model/prediction changes, no professional reference, no live endpoint change, no production change.

## Surviving historical bands 33-113 — PASSED

Authoritative artifact:
- `debug/v143-contextual-prune/surviving-band-provenance.json`

All original-boundary carriers now pass:
- Section 2: measures 33-48
- Section 3: measures 49-64, closed with validated exact historical Family-B evidence
- Section 4: measures 65-80
- Section 5: measures 81-96
- Reserve: measures 97-113

Aggregate:
- `allCarrierProvenancePassed = true`
- `allSurvivingBandsProvenancePassed = true`
- `section3ExactFamilyEvidenceApplied = true`

The current-container Section 3 observation is retained in the artifact and is not treated as the historical Family-B carrier.

Reserve measure 113 has only historical steps 0-7. The research adapter adds steps 8-15 solely to satisfy the unchanged completeness guard, hides those synthetic rows from nearest-slot assignment, and removes them before comparison. Historical reserve comparison remains exactly 264 rows. The frozen scorer is unchanged.

## Downstream exact-family closure — PASSED

Authoritative artifact:
- `debug/v143-contextual-prune/downstream-exact-family-closure.json`

Aggregate:
- `allHistoricalBandsDecisionEquivalent = true`
- `allHistoricalBandsFullyEquivalentWithinTolerance = true`

Section 2 remains fully exact. Section 3 is closed using the independent exact Family-B capture, including exact decision/base/sequence/keep score maps. The earlier current-container Section 3 score drift is retained in `currentContainerObservation` for auditability.

No tolerance, threshold, model, prediction, live endpoint, or production changes were used.

## Consolidated research evidence closure — PASSED

Authoritative artifact:
- `debug/v143-contextual-prune/research-evidence-closure.json`

Latest bot-recorded commit at creation time:
- `e1a273e68cd24e208b32d152b4c6c20735c36448` — `Record V143 research evidence closure`

The closure chains and verifies:
- exact 33-113 carrier provenance,
- exact-family downstream decision and score equivalence,
- frozen runtime development fingerprint,
- exact reserve base replay,
- exact reserve contextual replay,
- isolated Modal dependency smoke,
- static research-constant/model-fingerprint gate,
- shadow packaging dependency closure,
- protected live modules excluded from the shadow package,
- live V143 files unchanged.

Final closure fields:
- `researchEvidenceClosurePassed = true`
- claim scope: research-only surviving historical/reference-free behavior for measures 33-113
- measures 17-32 claimed: false
- production promotion allowed: false
- production modified: false

## Why the old monolithic 17-96 replay is not authoritative carrier provenance

The older 17-96 end-to-end diagnostic built one monolithic 17-96 carrier. Its mismatch was outside the intro band, but that execution shape does not preserve the original historical carrier boundaries proven by the newer 33-113 gate. Do not use the old monolithic replay to overwrite the band-preserving provenance standard.

It may still be useful as supporting output-level evidence, but not as a substitute for a dedicated 17-32 reference-free carrier provenance proof.

## Remaining isolated gap — measures 17-32

The frozen development artifact exists:
- `public/training/v143-musical-reconstruction-calibration/contextual-prune-17-96-frozen-events.json`
- 651 frozen contextual events across measures 17-96

The original freeze manifest confirms:
- development measures 17-96
- 431 development reference events
- 765 base events
- 651 contextual events
- frozen model/predictions before reserve grading

However, the calibration tree has reference-free carrier caches for Sections 2-5 and reserve, but no equivalent `fresh-section1-reference-free-cache.json` for measures 17-32.

Therefore the next research task is **not** to rerun or retune Sections 2-5. It is to determine whether a historical/reference-free 17-32 carrier can be reconstructed and provenance-checked under the same strict rules. If no historical carrier artifact exists, keep the distinction explicit between:
- frozen output/runtime replay for measures 17-32, and
- raw carrier provenance for measures 17-32.

Do not invent a carrier cache or silently promote output equivalence into carrier provenance.

## Immediate next step

1. Inspect existing intro/Section-1 research scripts, manifests, and historical event artifacts for a reconstructable 17-32 reference-free carrier definition.
2. If the historical carrier inputs are recoverable, add a research-only 17-32 provenance diagnostic with original boundaries and strict exact comparisons.
3. If they are not recoverable, write an explicit evidence-gap artifact rather than weakening the gate.
4. Only after the 17-32 question is resolved should the project consider an expanded 17-113 evidence closure or any opt-in canary integration plan.
5. Production remains untouched until a separate explicit promotion decision is made.

## Fresh-chat handoff

```text
Continue V143 contextual-prune research from GitHub.
Repo: dadrockyt-sys/dadrock-tabs-android
Branch: v143-contextual-prune-lobo
Read analyzer/V143_CONTEXTUAL_PRUNE_RECOVERY_CHECKPOINT.md first.
Do not reopen the already-passed Section 3 exact Family-B work unless new evidence contradicts it.
33-113 carrier provenance is closed and downstream exact-family equivalence is closed.
The consolidated research-evidence closure passed and production promotion remains disabled.
Immediate research gap: measures 17-32 lack a dedicated fresh Section-1 reference-free carrier cache/provenance artifact. Determine whether historical intro carrier inputs can be reconstructed exactly; do not weaken thresholds/tolerances or invent evidence.
```
