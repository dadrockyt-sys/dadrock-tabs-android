# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **SYNTHETIC TUNING CLOSED; P1/P2 PROSPECTIVE TRANSFER IMPLEMENTATION FROZEN OFFLINE; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub work and bounded inexpensive synthetic GitHub model runs are pre-authorized.

P1/P2/P3 real-data access, Codespaces, potentially billable Vercel work, production/deployment and main mutation remain separate authorization boundaries.

## S11 retained

S11 failed robustness magnitude criteria despite directionally positive diversity deltas in all three seeds for chord F1/recall and overall onset F1/recall.

No more synthetic tuning should run automatically.

## P1/P2 transfer preparation completed offline

Design:
- `docs/astra/P1_P2_TRANSFER_EVALUATION_DESIGN_V1.md`

Implementation:
- `astra_backend/evaluation/p1_p2_transfer_candidate_v1.py`
- `astra_backend/evaluation/p1_p2_transfer_evaluation_v1.py`
- focused tests
- `.github/workflows/astra-p1-p2-transfer-evaluation-v1.yml`

Authorization request:
- `docs/astra/P1_P2_TRANSFER_EVALUATION_AUTHORIZATION_REQUEST_V1.json`

Key frozen choices:
- P2 is primary transfer population; P1 is compatibility context only.
- baseline is exact frozen V3 checkpoint; no baseline retraining.
- candidate is one S9/S11 128-unit nonlinear-state model, synthetic-only, seed **20260927**, 500 steps.
- evaluator V2 with symmetric 50 ms crop-edge eligibility guard.
- thresholds fixed at 0.50 / 0.50.
- no seed selection, threshold tuning, architecture sweep, retry, P3 or production claim.
- if the V3 artifact expires, stop; do not retrain it merely to recreate provenance.

## Exact next step

**Do not create an authorization or launch file yet. Do not access P1/P2.**

The implementation is ready. Explicit authorization is still required for P1/P2 real-development access and the one 500-step synthetic candidate training that accompanies the transfer workflow.

P3 remains sealed.
