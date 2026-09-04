# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 access still awaits explicit owner approval/denial.
- Restricted GOAT bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; development hold remains frozen; prospective players `00/01/03` remain sealed and prospective score calls = **0**.
- CPU only unless freshly and specifically needed. No GPU/CUDA/Modal is needed for Phase 8.
- `main` / Production untouched; never modify/merge/promote without explicit user direction.

**Project Progress Score: 60%.**  
**Test Score: PHASE 1–7 REFERENCE-BLIND/SYNTHETIC CONTRACT PASS; PHASE 8 IMPLEMENTED / VERIFICATION PENDING; ACCURACY SCORE NOT RUN.**

## Phases 1–7 — COMPLETE

- Phase 1 `STRUCTURE_INSTRUMENT_CONDITIONING_V1`: run `33804010524`, job `100810007255`, **SUCCESS**.
- Phase 2 `STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1`: run `33804886663`, job `100812914077`, **SUCCESS**.
- Phase 3 `MIXTURE_STRUCTURE_CONTEXT_V1`: run `33809372857`, job `100827364605`, **SUCCESS**.
- Phase 4 `DUAL_CONTEXT_SHADOW_FUSION_V1`: run `33809867672`, job `100828947197`, **SUCCESS**.
- Phase 5 `FULL_MIXTURE_AUTO_STRUCTURE_ESTIMATOR_V1`: run `33810847829`, job `100832069691`, **SUCCESS**; A1–A12 pass.
- Phase 6 `FULL_MIXTURE_WAV_ADAPTER_V1`: run `33811270987`, job `100833411365`, **SUCCESS**; W1–W10 pass.
- Phase 7 `FULL_MIXTURE_ANALYZER_RUNTIME_SHADOW_WIRING_V1`: run `33826597803`, job `100880476202`, **SUCCESS**; S1–S12 pass.

Phase 7 analyzer shadow remains append-only research metadata; Product/PDF authority is unchanged.

## Phase 8 — `FULL_MIXTURE_SERVER_OBSERVATION_ADMISSION_WIRING_V1` IMPLEMENTED / VERIFICATION PENDING

User authorization received in this continuation; nothing is required from the user at this time.

Pre-implementation freeze:

`docs/checkpoints/SONGSTERR_FULL_MIXTURE_SERVER_OBSERVATION_ADMISSION_WIRING_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Freeze commit: `f00e1d8161c0ebdcb8713b43b02548b07d337306`.

Frozen status: **`SERVER RESEARCH-CONTEXT TRUST AUTHORIZED / PRODUCT-PDF AUTHORITY UNCHANGED / FAIL-OPEN REQUIRED / NO MODAL-GPU / NO REFERENCE SCORE`**.

Implementation commits so far:

- `a24c68b43e7ba0dd0eeadb1ea814b6a6bfd0b87a` — added `lib/aiTabAnalyzerMixtureObservationAdmissionV1.mjs`;
- `3f56aaf6ae67e1c4175ea7db8f3c2ba3462e50a3` — wired Phase 8 into `app/api/analyze-audio-tab/route.js`;
- `270f217748712b53c4d73471daf555ba81b1a208` — added deterministic/static T1–T12 verifier.

Implemented server behavior:

- route still builds `structuredPayload` before any mixture observation trust;
- route explicitly builds `baselineMixtureStructureContext` with `mixtureObservation: null` first;
- helper independently admits only version-1 full-mixture/request-audio/reference-blind observations with Phase 6/7 diagnostics proving no carrier/separated-carrier/event input;
- missing/malformed/bad-provenance observation returns the exact baseline object;
- provenance-valid but field-invalid candidate context is caught and returns the exact baseline object;
- admitted observations can populate only the existing research `mixtureStructureContext` through `buildAiTabMixtureStructureContextV1(...)`;
- explicit user priors retain field-by-field precedence through the unchanged Phase 3 builder;
- `structuredPayload`, analyzer selection/status, V143 safety gate, generated tab/events/render events/measure grid, Product/UI and PDF paths remain independent of the observation.

Verification matrix T1–T12 is encoded in `analyzer/verify_full_mixture_server_observation_admission_v1.mjs` and has not yet been run in CI at this checkpoint.

Safety accounting remains: external/reference assets read=false; GuitarSet=false; SplitMySong=false; GOAT restricted bytes=false; reference score calls=0; Modal invoked/deployed=false; GPU=false; Product/PDF authority changed=false; `main`/Production changed=false.

## NEXT SAFE ACTION

1. Add isolated CPU-only Phase 8 GitHub Actions workflow for T1–T12.
2. Run/inspect the workflow and tighten only implementation/verifier issues without weakening the frozen contract.
3. On success, write the dedicated Phase 8 result checkpoint and update this file with run/job/tested-head evidence.
4. Do not expand Product/PDF authority, deploy/invoke Modal, use GPU, read reference assets, score references, merge `main`, or promote Production in Phase 8.
