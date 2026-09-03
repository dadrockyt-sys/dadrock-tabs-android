# MIXTURE_STRUCTURE_CONTEXT_V1 — PHASE 3 RESULT

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`PHASE3_REFERENCE_BLIND_MIXTURE_CONTEXT_PASS / CARRIER_BORROWING_FORBIDDEN / OBSERVATION_CHANNEL_DISCONNECTED / NO_REFERENCE_SCORE`**

## Frozen source

Pre-implementation checkpoint:

`docs/checkpoints/SONGSTERR_MIXTURE_STRUCTURE_CONTEXT_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Creation commit:

`c643120922a9bea8d83f3fd458a84df8bd0c48d5`

No Phase 3 rule was weakened after implementation began.

## Implementation

- `80ca61f539d31c9b23fd6c8c11d22ddf81544b98` — pure `lib/aiTabMixtureStructureContextV1.mjs` resolver.
- `f8ec5909f16fe8179e9c5a4330dd4d60c6a5a864` — deterministic frozen M1–M10 verifier.
- `f8fa690cbe8b0fc2f30155024a22149134db4ea8` — analyzer route appends `mixtureStructureContext` with the real observation channel intentionally disconnected via `mixtureObservation: null`.
- `bd8598633a03a198d503f64abe7b62190eab271d` — complete AI Tab contract extended for mixture-context provenance, carrier-borrowing prohibition, product isolation and PDF non-consumption.
- `4591c12c35a125f197652e1547929fecd27f2be4` — branch workflow runs Phase 1, Phase 2, Phase 3 M1–M10, complete product wiring and compact safety evidence.

## Deterministic evidence

GitHub Actions:

- run `33809372857`;
- job `100827364605`;
- tested head `4591c12c35a125f197652e1547929fecd27f2be4`;
- conclusion **SUCCESS**.

Every workflow stage succeeded:

1. Conditioning V1 reference-blind contract;
2. conditioned shadow projection reference-blind contract;
3. **Mixture Structure Context V1 M1–M10**;
4. complete AI Tab product wiring;
5. compact safety evidence;
6. evidence commit.

Evidence bot commit:

`0219c29276220f508d5a20586f3bc493a855a691`

Evidence file:

`debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`

Evidence blob SHA:

`1c7082e4fe37d22426cc301d6c9c536bf7212544`

Evidence schema version: **5**.

## What M1–M10 establish

Mechanically/reference-blind:

- all-Auto with no trusted mixture observation stays unresolved;
- explicit user tempo/meter/pickup/feel resolve without any estimator;
- a trusted full-mixture observation can fill only Auto fields, field-by-field;
- explicit user values always override disagreeing observations;
- explicit/observed pickup `0` is preserved;
- `instrument-carrier`, `separated-stem`, `v143-rhythm-carrier`, missing provenance and wrong source identity fail closed;
- reference-bearing provenance fails closed;
- invalid version/confidence/value/method/feel/meter fails closed;
- current route passes **`mixtureObservation: null`** exactly;
- PDFs do not consume `mixtureStructureContext`;
- product tab fields and V143 gates are not mutated by Phase 3.

## Safety evidence

The complete evidence records:

- `mixtureStructureContextWired=true`;
- `mixtureStructureContextReferenceBlind=true`;
- `mixtureStructureContextReferenceScoreAuthorized=false`;
- `mixtureStructureContextCarrierBorrowingAllowed=false`;
- `mixtureStructureContextProductionEligible=false`;
- `mixtureStructureContextObservationConnected=false`;
- `mixtureStructureContextConsumedByPdf=false`;
- `productPayloadMutatedByMixtureContext=false`;
- `productionModified=false`;
- `productionPromotionAuthorized=false`.

No reference-facing scoring occurred. GuitarSet, SplitMySong and GOAT restricted bytes were not read. No Modal analyzer was invoked and no GPU was used.

## Scientific interpretation

Phase 3 does **not** prove improved transcription accuracy and does not claim to know Songsterr's private implementation.

It establishes the DadRock dual-context boundary needed for the next work: global song structure now has a dedicated provenance-gated full-mixture context instead of being silently borrowed from a separated guitar carrier. The actual Auto full-mixture estimator remains intentionally unconnected.

## Next safe direction

A real full-mixture observation adapter must be independently frozen before connection. Until then Auto estimator fields remain unresolved.

A separate safe product-facing phase may expose optional research-branch structure/tuning/capo controls with Auto/default values, because Phase 1–3 already validate and carry those inputs. Such UI work must not connect the estimator channel, change default analyzer selection, alter PDF gates or promote Production.
