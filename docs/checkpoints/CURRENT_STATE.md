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
- GuitarSet development hold remains frozen; no V6 threshold rescue/mining, no V3/V4/V5 reruns or retuning.
- Prospective GuitarSet players `00/01/03` remain sealed; prospective GuitarSet score calls = **0**.
- Open-corpus work cannot mutate V168.
- CPU only. Fresh explicit authorization is required immediately before GPU/CUDA/Modal.
- `main` / Production untouched; never modify/merge/promote without explicit user direction.

**Project Progress Score: 60%.**  
**Test Score: PHASE 1 REFERENCE-BLIND CONTRACT PASS; PHASE 2 SHADOW CONTRACT RUNNING; ACCURACY SCORE NOT RUN.**

## GOAT pre-access path — COMPLETE / waiting

`docs/checkpoints/V168_GOAT_PREACCESS_GAP_AUDIT_20260902.md` — creation commit `bb74b64f4a6be8cbab2da46569161c37f2bc09ab`.

Status: **`GOAT_PREACCESS_IMPLEMENTATION_COMPLETE / AWAIT_OWNER_DECISION`**.

Existing access/grant provenance, complete-base-DI inventory, source/reference SHA256 binding, 50 ms onset-EOF integrity, deterministic Tier 1/Tier 2 selection, metadata-only selection validator, base-manifest validator and provenance validator already cover the pre-access admission path. Absence of a GOAT candidate generator/scorer remains intentional until real access/admission.

## Songsterr public clue set — captured, not reverse engineering

- `SONGSTERR_PUBLIC_AI_TRANSCRIPTION_OBSERVATION_20260903.md` — `4210b1e6d1ec44fcbb0833d3411118924fd8706b`.
- `SONGSTERR_ARCHITECTURE_GAP_INVENTORY_20260903.md` — `592762183301a8767cba75c1c9e280a83ab4aa19`.
- `SONGSTERR_DUAL_CONTEXT_TOPOLOGY_HYPOTHESIS_20260903.md` — `8da294acc7d5e503fe7b193bf3903caed3d0beca`.

Independent DadRock architecture gap:

1. **`STRUCTURE_INSTRUMENT_CONDITIONING_V1`** — meter/pickup/tempo/feel plus role/tuning/capo carried through the pipeline.
2. **Dual-context topology** — full mixture for global structure evidence plus role/separated carrier for local note evidence, fused before alignment/tab decoding.

This is an independently motivated DadRock hypothesis, not a claim about Songsterr private models, data, thresholds or APIs.

## Phase 1 — `STRUCTURE_INSTRUMENT_CONDITIONING_V1` COMPLETE

Pre-freeze: `SONGSTERR_STRUCTURE_INSTRUMENT_CONDITIONING_V1_PREIMPLEMENTATION_FREEZE_20260903.md` — `29ef4f7e131e35378a58abb4cf68095bd284c075`.

Result: `SONGSTERR_STRUCTURE_INSTRUMENT_CONDITIONING_V1_PHASE1_RESULT_20260903.md` — `a79ea4e1d62b2dfaeadac165703bf1e2315dd56f`.

Status: **`PHASE1_REFERENCE_BLIND_CONTRACT_PASS / NO_ACCURACY_CLAIM / NO_REFERENCE_SCORE`**.

Final deterministic evidence:

- run `33804010524`, job `100810007255`;
- tested head `ab84f27bcd55990fadbc824cfc8ad883e786d971`;
- conclusion **SUCCESS**;
- evidence bot commit `22b0bf3661b251eddeb9e41f0f844683ba2d3ca6`;
- evidence blob SHA `8bf20c176c27edb01cca649c36e8ac144c3d684a`.

No reference/corpus reads or scores, Modal calls, GPU use or Production modification occurred.

## Phase 2 — `STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1`

Pre-implementation freeze:

`docs/checkpoints/SONGSTERR_STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Creation commit `cc08ecbdb3ce661b01afa1d64429c5e2c4988073`.

Frozen status: **`REFERENCE-BLIND SHADOW IMPLEMENTATION AUTHORIZED / PRODUCT OUTPUT MUTATION FORBIDDEN / REFERENCE SCORING NOT AUTHORIZED`**.

### Phase 2 implementation coded

- `854b6eb572efec6dc145611395462cb41b0cc965` — new pure `lib/aiTabConditionedShadowProjectionV1.mjs`.
- `0312c1a08349afa8cae297f652af43cac61b4ec0` — analyzer API appends `conditioningShadowProjection` from copied `structuredPayload.events` plus server-normalized conditioning.
- `bd4c3612090d2091f652ee4273587671e4fe19b7` — frozen deterministic S1–S10 verifier.
- `6511f12a53838def0c711b3068380a4cad3a9e03` — existing end-to-end verifier extended to prove shadow-only separation and PDF non-consumption.
- `6721b96a58347789aae99c8253ec1cd717b726c8` — branch workflow runs Phase 1 contract, Phase 2 S1–S10, full product wiring and compact safety evidence.

Shadow implementation follows the pre-freeze exactly:

- Auto tempo/meter/pickup -> `UNRESOLVED_AUTO_STRUCTURE`; no invented placement.
- explicit quarter-note BPM + denominator-aware signature units; 6/8 test protects against hidden 4/4 assumption.
- pickup span -> measure 0; first full bar begins at explicit pickup boundary.
- straight=4 divisions/signature unit; triplet=3; Auto feel does not guess subdivision.
- physical tuning remains low-to-high in Conditioning V1; DadRock shadow string indexing reverses to high-to-low.
- capo changes sounding open pitch; conditioned fret range `[0,24]`.
- product source events and all existing payload fields remain untouched.
- PDF routes are required not to consume the shadow projection.
- `shadowOnly=true`, `referenceBlind=true`, `referenceScoreAuthorized=false`, `productionEligible=false`.

Current deterministic workflow:

- run `33804886663`;
- job `100812914077`;
- tested head `6721b96a58347789aae99c8253ec1cd717b726c8`;
- status **IN PROGRESS** when this checkpoint was written.

No analyzer/audio/reference corpus was invoked by these tests. No GuitarSet/SplitMySong/GOAT read, no reference score, no Modal/GPU, no Production change.

## NEXT SAFE ACTION

1. Check run `33804886663` / job `100812914077`.
2. If S1–S10 or the full safety gate fails, fix only implementation/contract defects without weakening the frozen Phase 2 rules.
3. On success, create `STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1` result checkpoint and update this file with final run/evidence hashes.
4. Then decide the next independently motivated step without using the shadow output as an accuracy signal. A likely next phase is a full-mixture structure-context estimator adapter, still shadow/reference-blind first.
5. Await GOAT owner approval/denial; do not substitute another holdout.
6. No SplitMySong/GuitarSet work, no Modal/GPU, and no `main`/Production changes.
