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
- CPU only. Fresh explicit authorization is required immediately before GPU/CUDA/Modal.
- `main` / Production untouched; never modify/merge/promote without explicit user direction.

**Project Progress Score: 60%.**  
**Test Score: PHASE 1 + PHASE 2 + PHASE 3 + PHASE 4 REFERENCE-BLIND CONTRACT PASS; PHASE 5 FROZEN BEFORE CODE; ACCURACY SCORE NOT RUN.**

## Phase 1 — `STRUCTURE_INSTRUMENT_CONDITIONING_V1` COMPLETE

Pre-freeze `29ef4f7e131e35378a58abb4cf68095bd284c075`; result `a79ea4e1d62b2dfaeadac165703bf1e2315dd56f`; run `33804010524`, job `100810007255`, **SUCCESS**.

## Phase 2 — `STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1` COMPLETE

Pre-freeze `cc08ecbdb3ce661b01afa1d64429c5e2c4988073`; result `6df1729538acb36dbe38d5eb757a7d4bddc767cf`; run `33804886663`, job `100812914077`, **SUCCESS**.

## Phase 3 — `MIXTURE_STRUCTURE_CONTEXT_V1` COMPLETE

Pre-freeze `c643120922a9bea8d83f3fd458a84df8bd0c48d5`; result `b0a8035033a356983266d52e0ae0a33a92c9c7b3`; run `33809372857`, job `100827364605`, **SUCCESS**; evidence bot commit `0219c29276220f508d5a20586f3bc493a855a691`.

Phase 3 real full-mixture observation remains intentionally disconnected (`mixtureObservation: null`). Carrier/separated/V143 structure borrowing remains forbidden.

## Phase 4 — `DUAL_CONTEXT_SHADOW_FUSION_V1` COMPLETE

Pre-freeze `0ec398ce4ac0ea1c36494e70ffc02ca38711e4ea`; result `0c8e061e3e50efa871cd85a0c1f5c657ac629d81`; run `33809867672`, job `100828947197`, **SUCCESS**; evidence bot commit `318e3830fa1bf9d0df34a29ce0d3a6beafaa4c4a`; evidence blob SHA `7c55a348e01d9077ac893cfcf75030dc2bf354e4`.

Phase 4 mechanically completes the shadow dual-context topology:

- global song structure authority = validated Phase 3 mixture context;
- local note evidence = copied normalized analyzer events;
- role/tuning/capo authority = Conditioning V1 instrument config;
- fused projection = shadow-only research metadata.

No Product/PDF consumption or Production mutation is authorized.

## Phase 5 — `FULL_MIXTURE_AUTO_STRUCTURE_ESTIMATOR_V1` FROZEN BEFORE CODE

Pre-implementation checkpoint:

`docs/checkpoints/SONGSTERR_FULL_MIXTURE_AUTO_STRUCTURE_ESTIMATOR_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Creation commit `5ee029dff31fdd52422f70cb6e4714d2339519b5`.

Status: **`REFERENCE-BLIND CPU WAVEFORM ESTIMATOR AUTHORIZED / SHADOW ONLY / REFERENCE SCORING NOT AUTHORIZED`**.

Key frozen design:

- waveform/PCM input from the full mixture only;
- no Basic Pitch/transcribed-event input and no V143/separated-carrier input;
- 20 ms mean-absolute-energy frames, 10 ms hop, positive novelty against 8-frame median history;
- deterministic onset peaks, 70 ms refractory;
- tempo candidates 50–220 BPM at 0.5 BPM using phase coherence + onset-gap compatibility;
- meter V1 may emit only 3/4, 4/4 or unresolved using accent/downbeat evidence;
- pickup derives from first resolved full-measure downbeat phase;
- feel uses straight half-beat versus triplet 1/3 and 2/3 subdivision evidence;
- output is the exact trusted Phase 3 full-mixture observation schema;
- A1–A12 synthetic waveform tests frozen before implementation;
- no route connection in Phase 5: current route must keep `mixtureObservation: null` until a separate wiring freeze exists.

V34 was inspected and is not sufficient as the new authority because its tempo diagnostic is derived from transcribed onset groups/events. Phase 5 intentionally moves structure inference earlier to the mixture waveform itself.

## NEXT SAFE ACTION

1. Implement `analyzer/full_mixture_auto_structure_estimator_v1.py` exactly against the Phase 5 freeze.
2. Add deterministic synthetic waveform verifier A1–A12; no external audio assets.
3. Run it CPU-only in the branch workflow together with existing Phase 1–4 safety gates.
4. On pass, create a Phase 5 result checkpoint and update this file.
5. Do **not** connect the estimator to the live analyzer/API yet; that requires a separate post-result wiring freeze.
6. Await GOAT owner approval/denial; do not substitute another holdout.
7. No SplitMySong/GuitarSet work, no Modal/GPU, and no `main`/Production changes.
