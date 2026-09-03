# STRUCTURE_INSTRUMENT_CONDITIONING_V1 — PRE-IMPLEMENTATION FREEZE

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **REFERENCE-BLIND IMPLEMENTATION AUTHORIZED / REFERENCE SCORING NOT AUTHORIZED**

## Purpose

Freeze the first implementation boundary independently motivated by public Songsterr product behavior and the previously recorded dual-context architecture hypothesis before any code is changed.

This checkpoint does **not** claim to reconstruct Songsterr's private implementation. It converts only public product/architecture clues into an independently specified DadRock research contract.

## Scientific boundary

This work does not reopen GuitarSet development, does not modify V143 historical predictions, does not arm V168 GOAT scoring, and does not authorize any SplitMySong/GuitarSet/GOAT reference-facing score call.

No GPU/CUDA/Modal use is authorized. `main` and Production remain untouched.

## Frozen Phase 1 name

`STRUCTURE_INSTRUMENT_CONDITIONING_V1`

Phase 1 scope is **schema + plumbing + deterministic reference-blind contract tests only**.

## Frozen request schema

The `/ai-tab` request may carry the following optional object:

```json
{
  "conditioning": {
    "version": 1,
    "structurePrior": {
      "tempoBpm": null,
      "timeSignature": null,
      "pickupBeats": null,
      "feel": "auto"
    },
    "instrumentConfig": {
      "role": "lead",
      "tuningMidi": [40, 45, 50, 55, 59, 64],
      "capoFret": 0
    }
  }
}
```

### StructurePriorV1

- `tempoBpm`: `null` for Auto or finite number in `[20, 400]`.
- `timeSignature`: `null` for Auto or `{ numerator, denominator }` where numerator is integer `[1, 32]` and denominator is one of `1, 2, 4, 8, 16, 32`.
- `pickupBeats`: `null` for Auto or finite number in `[0, 32]`.
- `feel`: one of `auto`, `straight`, `triplet`.

Phase 1 does not require an ML structure estimator. Auto values remain explicitly Auto and may later be resolved by an isolated structure-context adapter.

### InstrumentConfigV1

- `role`: one of `lead`, `rhythm`, `bass`; it must agree with the existing `transcriptionType` after normalization.
- `tuningMidi`: ordered low-to-high open-string MIDI pitches.
  - guitar roles: 4–8 strings;
  - bass role: 4–6 strings;
  - each MIDI pitch integer `[0, 127]`;
  - strictly increasing pitches required.
- `capoFret`: integer `[0, 24]`.

Default tuning when omitted:
- lead/rhythm guitar: `[40,45,50,55,59,64]` = E2 A2 D3 G3 B3 E4;
- bass: `[28,33,38,43]` = E1 A1 D2 G2.

The effective sounding open pitch for each string is `tuningMidi[i] + capoFret`; the stored tuning remains the physical open-string tuning plus a separate capo value.

## Frozen dual-context provenance contract

Phase 1 must preserve two logically distinct audio identities even when they currently point to the same uploaded source:

1. `mixtureSource` — normalized/full-mixture context reserved for global structure evidence.
2. `instrumentCarrierSource` — role-specific/local-note carrier identity; may initially be `same-as-mixture` for legacy paths and may identify V143/separated carriers where the analyzer supplies provenance.

No Phase 1 code may silently replace mixture provenance with carrier provenance.

Suggested response shape:

```json
{
  "conditioningContract": {
    "name": "structure-instrument-conditioning",
    "version": 1,
    "referenceBlind": true,
    "referenceScoreAuthorized": false,
    "structurePrior": {},
    "instrumentConfig": {},
    "provenance": {
      "mixtureSource": {},
      "instrumentCarrierSource": {}
    }
  }
}
```

## Frozen implementation topology

```text
UPLOADED / NORMALIZED FULL MIX
        |                         \
        |                          \
        v                           v
MixtureStructureContextV1     InstrumentEventContextV1
(global structure evidence)   (role/local-note evidence)
        |                           |
        +-------------+-------------+
                      v
          structure-aware alignment
                      v
        tuning/capo-aware tab decode
                      v
             editable tab result
```

Phase 1 only establishes the contract/plumbing needed for this topology. It does not claim a new transcription model.

## Phase 1 implementation plan — FROZEN

1. Add a pure server-side JS normalizer/validator for `conditioning`.
2. Add default tuning by instrument role and deterministic tuning/capo normalization.
3. Route the normalized conditioning object from `/api/analyze-audio-tab` to the selected analyzer without changing analyzer selection logic.
4. Preserve current Lead/Bass legacy paths and V143 Rhythm fail-closed safety checks.
5. Return a sanitized `conditioningContract` alongside the existing structured payload; never trust analyzer-returned request conditioning over the server-normalized request.
6. Extend the existing branch-only AI Tab end-to-end contract to test the new schema/plumbing and to prove Production remains untouched.
7. Add deterministic synthetic/unit-style assertions only; no corpus/reference scoring.
8. UI controls are optional within Phase 1. If added, Auto must remain the default so existing user behavior is unchanged.

## Deterministic test cases — FROZEN BEFORE IMPLEMENTATION

The implementation must demonstrate at minimum:

### T1 — default lead
Input: `transcriptionType=lead`, conditioning omitted.  
Expected: guitar standard tuning, capo 0, all structure fields Auto/null, role lead.

### T2 — default bass
Input: `transcriptionType=bass`, conditioning omitted.  
Expected: bass standard tuning, capo 0, role bass.

### T3 — explicit structure
Input: tempo `96`, time signature `6/8`, pickup `1.5`, feel `triplet`.  
Expected: values preserved exactly after normalization.

### T4 — alternate guitar tuning + capo
Input: Drop D `[38,45,50,55,59,64]`, capo `2`.  
Expected: physical tuning preserved, capo preserved separately; no forced standard tuning.

### T5 — role mismatch fail closed
Input: `transcriptionType=rhythm` but `instrumentConfig.role=lead`.  
Expected: request rejected rather than silently changing role.

### T6 — invalid tuning fail closed
Input: unordered/non-integer/out-of-range tuning.  
Expected: request rejected.

### T7 — invalid structure fail closed
Input: impossible/unsupported meter, tempo, pickup, or feel.  
Expected: request rejected.

### T8 — analyzer forwarding
Expected: selected analyzer receives normalized `conditioning` plus the existing request fields. Analyzer route selection remains unchanged.

### T9 — response provenance
Expected: returned payload exposes the server-normalized contract, `referenceBlind=true`, `referenceScoreAuthorized=false`, mixture provenance and carrier provenance without manufacturing corpus/reference provenance.

### T10 — legacy safety
Expected: Lead legacy preserved, Bass legacy preserved, V143 Rhythm fail-closed anti-leakage gate preserved, no payment/token/email/deployment side effects in contract verification, `productionPromotionAuthorized=false`.

## Explicit non-goals

Phase 1 must not:

- add or tune GuitarSet thresholds;
- score SplitMySong, GuitarSet, GOAT or another frozen reference;
- infer Songsterr private APIs/models/weights/training data;
- change Demucs/BS-RoFormer settings from frozen historical experiments;
- change V143 historical candidate predictions;
- promote any analyzer to Production;
- use GPU/CUDA/Modal;
- treat successful contract tests as evidence of transcription-accuracy improvement.

## Promotion/evaluation state

`implementationAllowed=true`  
`syntheticContractTestsAllowed=true`  
`referenceFacingScoreAllowed=false`  
`productionPromotionAuthorized=false`

The next valid action is to implement the frozen Phase 1 contract on `v143-contextual-prune-lobo`, checkpoint the code/test result, and remain reference-blind while GOAT access is unresolved.
