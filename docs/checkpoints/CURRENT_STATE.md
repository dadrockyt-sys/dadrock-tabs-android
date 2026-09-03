# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 access is still awaiting explicit owner approval/denial.
- Restricted GOAT bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3 terminal `NO_DEVELOPMENT_SIGNAL`; V4 terminal `V4_PLAYER05_CONFIRMATION_FAIL`; V5 terminal `NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL`.
- GuitarSet development hold remains frozen; no V6 neighboring-threshold sweep, no mining V5 near-signals, no V3/V4/V5 reruns or retuning.
- Prospective GuitarSet players `00/01/03` remain sealed; prospective GuitarSet score calls = **0**.
- Open-corpus work cannot mutate V168.
- CPU only. Fresh explicit authorization is required immediately before GPU/CUDA/Modal.
- `main` / Production untouched; never modify/merge/promote without explicit user direction.

Detailed frozen history remains in the earlier V3/V4/V5, GuitarSet hold, SplitMySong and V168 checkpoints.

**Project Progress Score: 60%.**  
**Test Score: REFERENCE-BLIND CONTRACT PASS; ACCURACY SCORE NOT RUN.**

## GOAT pre-access path — COMPLETE / waiting

`docs/checkpoints/V168_GOAT_PREACCESS_GAP_AUDIT_20260902.md`  
Creation commit `bb74b64f4a6be8cbab2da46569161c37f2bc09ab`.

Status: **`GOAT_PREACCESS_IMPLEMENTATION_COMPLETE / AWAIT_OWNER_DECISION`**.

Existing access/grant provenance, complete-base-DI inventory, source/reference SHA256 binding, 50 ms onset-EOF integrity, deterministic Tier 1/Tier 2 selection, metadata-only selection validator, base-manifest validator and provenance validator already cover the pre-access admission path. Absence of a GOAT candidate generator/scorer remains intentional until real access/admission.

## Songsterr public clue set — captured, not reverse engineering

- `SONGSTERR_PUBLIC_AI_TRANSCRIPTION_OBSERVATION_20260903.md` — commit `4210b1e6d1ec44fcbb0833d3411118924fd8706b`.
- `SONGSTERR_ARCHITECTURE_GAP_INVENTORY_20260903.md` — commit `592762183301a8767cba75c1c9e280a83ab4aa19`.
- `SONGSTERR_DUAL_CONTEXT_TOPOLOGY_HYPOTHESIS_20260903.md` — commit `8da294acc7d5e503fe7b193bf3903caed3d0beca`.

Independent architecture gap:

1. **`STRUCTURE_INSTRUMENT_CONDITIONING_V1`** — meter/pickup/tempo/feel plus role/tuning/capo carried through the pipeline.
2. **Dual-context topology** — preserve the full mixture for global structure evidence while role/separated carrier evidence supplies local note information, then fuse before alignment/tab decoding.

Existing DadRock already has individual tempo, measure-grid and separation components. The new idea is integration/conditioning, not simply adding Demucs, tempo estimation or another threshold sweep.

This is a DadRock architecture hypothesis motivated by public clues, **not a claim about Songsterr's exact private models, data, thresholds or APIs**.

## Phase 1 — `STRUCTURE_INSTRUMENT_CONDITIONING_V1` COMPLETE

Pre-freeze checkpoint: `SONGSTERR_STRUCTURE_INSTRUMENT_CONDITIONING_V1_PREIMPLEMENTATION_FREEZE_20260903.md`  
Creation commit `29ef4f7e131e35378a58abb4cf68095bd284c075`.

Result checkpoint: `SONGSTERR_STRUCTURE_INSTRUMENT_CONDITIONING_V1_PHASE1_RESULT_20260903.md`  
Creation commit `a79ea4e1d62b2dfaeadac165703bf1e2315dd56f`.

Status: **`PHASE1_REFERENCE_BLIND_CONTRACT_PASS / NO_ACCURACY_CLAIM / NO_REFERENCE_SCORE`**.

Implemented:

- `lib/aiTabConditioningV1.mjs` — commit `a36235371441e2e1209335dd4017093a2aa0da7a`;
- analyzer API normalization/forwarding/server-owned conditioning contract — commit `71beaa8a947ede8a706d28c48bf9bd26852aeb3c`;
- frozen deterministic T1–T10 verifier — commit `2444a0528fa21dcb69dd490ab43ddd1adc132f97`;
- branch workflow wiring — commit `7ce26de92e4018d8849f07d3b57ee82c7e030784`.

Final deterministic evidence:

- run `33804010524`;
- job `100810007255`;
- tested head `ab84f27bcd55990fadbc824cfc8ad883e786d971`;
- conclusion **SUCCESS**;
- evidence bot commit `22b0bf3661b251eddeb9e41f0f844683ba2d3ca6`;
- evidence blob SHA `8bf20c176c27edb01cca649c36e8ac144c3d684a`.

T1–T10 passed. The two earlier end-to-end failures were stale source-text assertions against already stricter V143 fail-closed code; the verifier was aligned without weakening product/safety code.

No corpus/reference reads/scores, Modal calls, GPU use, payment/token/email/deployment side effects or Production modification occurred.

## Phase 2 — `STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1` FROZEN BEFORE CODE

Pre-implementation checkpoint:

`docs/checkpoints/SONGSTERR_STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Creation commit:

`cc08ecbdb3ce661b01afa1d64429c5e2c4988073`

Status: **`REFERENCE-BLIND SHADOW IMPLEMENTATION AUTHORIZED / PRODUCT OUTPUT MUTATION FORBIDDEN / REFERENCE SCORING NOT AUTHORIZED`**.

Frozen Phase 2 rules:

- operate only on copied normalized analyzer events plus server-normalized Conditioning V1;
- never overwrite `generatedTab`, `events`, `renderEvents`, `measureGrid` or `analysisEngine`;
- structure is fully resolved only when explicit tempo + time signature + pickup are all supplied; Auto values produce `UNRESOLVED_AUTO_STRUCTURE` rather than invented defaults;
- BPM is quarter-note BPM; meter denominator determines `signatureUnitSeconds`; 6/8 is therefore not hard-coded as 4/4;
- pickup events use `measureNumber=0`, first full measure begins exactly at `pickupSeconds`;
- straight feel uses 4 subdivisions/signature unit; triplet uses 3; Auto feel does not guess subdivision;
- Conditioning V1 physical tuning remains low-to-high, while shadow DadRock string indexes are decoded high-to-low (`stringIndex=0` highest string);
- sounding open pitch = physical open MIDI + capo;
- playable fret range `[0,24]`;
- deterministic compatibility scoring is frozen from existing DadRock lead/rhythm/bass fingering preferences before tests;
- output must be `shadowOnly=true`, `referenceBlind=true`, `referenceScoreAuthorized=false`, `productionEligible=false`;
- synthetic/reference-blind tests S1–S10 are frozen before implementation.

## NEXT SAFE ACTION

1. Implement the now-frozen `STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1` in a new pure module on this branch.
2. Append only `conditioningShadowProjection` to the research response; product transcription fields remain byte-for-byte owned by the existing payload builder.
3. Run only frozen deterministic S1–S10 reference-blind tests and the existing end-to-end safety gate.
4. On pass, create a Phase 2 result checkpoint and update this file.
5. Await explicit GOAT approval/denial; do not substitute another holdout.
6. No SplitMySong/GuitarSet work, no Modal/GPU, and no `main`/Production changes.
