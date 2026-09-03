# STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1 — PHASE 2 RESULT

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`PHASE2_REFERENCE_BLIND_SHADOW_PASS / PRODUCT_OUTPUT_UNCHANGED / NO_ACCURACY_CLAIM / NO_REFERENCE_SCORE`**

## Purpose

Close the first deterministic implementation of the Songsterr-inspired structure/tuning/capo interpretation path after the independently frozen S1–S10 contract passed on the isolated research branch.

This result proves architecture/plumbing behavior only. It does **not** prove transcription accuracy, does **not** use a reference corpus, and does **not** reconstruct Songsterr's private implementation.

## Frozen predecessor

Pre-implementation freeze:

`docs/checkpoints/SONGSTERR_STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Creation commit:

`cc08ecbdb3ce661b01afa1d64429c5e2c4988073`

The structure math, pickup semantics, feel handling, tuning/capo decoder, legacy compatibility scoring, output isolation and S1–S10 tests were fixed before code.

## Implementation

### Pure shadow projector

Commit `854b6eb572efec6dc145611395462cb41b0cc965`

Added:

`lib/aiTabConditionedShadowProjectionV1.mjs`

Behavior:

- accepts copied normalized analyzer events plus server-normalized Conditioning V1;
- never mutates input events/conditioning;
- Auto tempo/meter/pickup produces `UNRESOLVED_AUTO_STRUCTURE` rather than hidden defaults;
- explicit BPM is quarter-note BPM;
- time-signature denominator determines `signatureUnitSeconds`;
- pickup span is measure 0 and the first full measure starts exactly at `pickupSeconds`;
- straight feel uses 4 subdivisions/signature unit;
- triplet feel uses 3 subdivisions/signature unit;
- Auto feel leaves subdivision unresolved while retaining explicit measure placement;
- Conditioning V1 physical tuning stays low-to-high;
- DadRock string indexes are decoded high-to-low (`0 = highest string`);
- sounding open MIDI = physical open MIDI + capo;
- conditioned fret candidates are limited to `[0,24]`;
- deterministic candidate scoring is the compatibility rule frozen before tests;
- impossible pitches fail shadow decoding closed without touching source string/fret.

The output contract explicitly carries:

- `shadowOnly=true`;
- `referenceBlind=true`;
- `referenceScoreAuthorized=false`;
- `productionEligible=false`.

### Research API attachment

Commit `0312c1a08349afa8cae297f652af43cac61b4ec0`

`app/api/analyze-audio-tab/route.js` now appends:

`conditioningShadowProjection`

from `structuredPayload.events` plus the already-normalized Conditioning V1 object.

The route still spreads the existing `structuredPayload` unchanged. The shadow adapter does not overwrite:

- `generatedTab`;
- `events`;
- `renderEvents`;
- `measureGrid`;
- `analysisEngine`.

It does not participate in analyzer selection or V143 safety verification.

### Frozen deterministic S1–S10 verifier

Commit `bd4c3612090d2091f652ee4273587671e4fe19b7`

Added:

`analyzer/verify_ai_tab_conditioned_shadow_projection_v1.mjs`

Tests:

1. S1 Auto structure remains unresolved and does not invent placement;
2. S2 120 BPM 4/4 straight gives 0.5 s quarter/signature unit, 2.0 s measure and 0.125 s subdivision;
3. S3 120 BPM 6/8 uses 0.25 s eighth-signature units and 1.5 s measures, protecting against hidden 4/4 assumptions;
4. S4 one-unit pickup maps pre-boundary events to measure 0 and the exact boundary to measure 1;
5. S5 triplet feel uses three subdivisions per signature unit;
6. S6 Auto feel leaves subdivision unguessed while explicit bar placement still resolves;
7. S7 Drop D `[38,45,50,55,59,64]` + capo 2 changes deterministic playable decoding while preserving physical tuning separately;
8. S8 impossible conditioned pitch returns null conditioned position while source string/fret remain untouched;
9. S9 pure adapter and route preserve source/product ownership;
10. S10 safety accounting keeps the path shadow-only, reference-blind and non-Production.

### Full product safety gate

Commit `6511f12a53838def0c711b3068380a4cad3a9e03`

The existing end-to-end verifier was extended to require:

- shadow route wiring;
- shadow contract safety flags;
- no product-payload mutation;
- no Phase 2 shadow consumption by preview PDF or full PDF routes;
- all pre-existing Lead/Bass/V143 safety behavior.

Workflow commit `6721b96a58347789aae99c8253ec1cd717b726c8` runs:

1. Phase 1 Conditioning V1 verifier;
2. Phase 2 shadow S1–S10 verifier;
3. complete AI Tab product-wiring verifier;
4. compact safety enforcement;
5. compact evidence commit.

## Final deterministic result

GitHub Actions run: `33804886663`  
Job: `100812914077`  
Tested head: `6721b96a58347789aae99c8253ec1cd717b726c8`  
Conclusion: **SUCCESS**

All stages passed on the first full Phase 2 workflow run.

The workflow committed compact evidence as:

`c6bb396e69cfe8634d2b57c29faf066d1a00d5b6` — `Record AI Tab end-to-end contract`

Evidence path:

`debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`

Evidence blob SHA:

`4d0ad6983646588338472fdb27cd8cdd60dbe60a`

Evidence schema version: `4`.

Final compact evidence asserts:

- `conditioningV1Wired=true`;
- `conditioningV1ReferenceBlind=true`;
- `conditioningV1ReferenceScoreAuthorized=false`;
- `dualContextProvenanceWired=true`;
- `conditioningShadowProjectionWired=true`;
- `conditioningShadowProjectionShadowOnly=true`;
- `conditioningShadowProjectionReferenceBlind=true`;
- `conditioningShadowProjectionReferenceScoreAuthorized=false`;
- `conditioningShadowProjectionProductionEligible=false`;
- `conditioningShadowProjectionConsumedByPdf=false`;
- `productPayloadMutatedByShadowProjection=false`;
- Lead legacy path preserved;
- Bass legacy path preserved;
- V143 Rhythm route fail closed;
- V143 structured renderer fail closed;
- no manufactured product placement for legacy output;
- no payment attempt;
- no token redemption;
- no customer email;
- no Vercel deployment attempt;
- `productionModified=false`;
- `productionPromotionAuthorized=false`.

## Scientific accounting

During Phase 2 implementation/testing:

- reference-facing score calls: **0**;
- GuitarSet read: **false**;
- SplitMySong read: **false**;
- restricted GOAT bytes read: **false**;
- Modal analyzer invoked by these tests: **false**;
- GPU/CUDA used: **false**;
- Production modified: **false**.

No transcription-quality metric was generated. Shadow projection output must not be treated as a development score or as evidence of accuracy improvement.

## Phase 2 conclusion

The DadRock research branch now has a functioning deterministic bridge from the Phase 1 conditioning contract to a concrete parallel musical interpretation:

```text
server-normalized structure prior
        +
server-normalized role/tuning/capo
        +
copied analyzer note events
        |
        v
STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1
        |
        +-> explicit measure/signature-unit placement when structure is known
        +-> straight/triplet shadow quantization when feel is known
        +-> tuning/capo-conditioned string/fret decode
        |
        v
shadow metadata only
```

This establishes the mechanics needed for the public Songsterr-inspired architecture without altering the tab a customer receives.

## Next independently motivated direction

The most important remaining architectural gap is not another fret/threshold heuristic. It is the **mixture-side structure context** itself.

A future Phase 3 should be frozen separately before code. It should define how a trusted full-mixture structure observation can populate tempo/meter/pickup/feel context while preserving explicit user overrides and source provenance. Until a genuinely full-mixture estimator is connected, Auto fields should remain unresolved rather than silently borrowing structure from a separated carrier.

An immediately useful independent product-facing step is also possible on the research branch: expose optional advanced structure/tuning/capo controls with Auto defaults so users can supply the information Phase 1/2 now understand. That step must be separately frozen and must not imply an accuracy claim.

GOAT/GuitarSet/SplitMySong restrictions and CPU/no-Modal/no-Production boundaries remain unchanged.
