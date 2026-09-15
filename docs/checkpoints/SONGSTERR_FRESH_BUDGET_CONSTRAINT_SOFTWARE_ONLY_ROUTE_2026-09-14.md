# Songsterr Fresh — Budget Constraint / Software-Only Route

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **ACTIVE BUDGET BOUNDARY**

## User constraint

The user has clarified that available budget is effectively limited to existing Vercel/model costs. No additional hardware, bench equipment, interface, piezo system, donor instrument, performer, vendor service, studio time, or other paid acquisition should be assumed available.

This supersedes any earlier implication that a small Stage-0 purchase should happen now.

## Immediate consequence

- `HARDWARE_PROCUREMENT_PAUSED:true`
- `PAID_VENDOR_CONTACT_PAUSED:true`
- `PAID_PERFORMER_OR_STUDIO_WORK_PAUSED:true`
- `REAL_CALIBRATION_CAPTURE_PAUSED:true`
- `REAL_HOLDOUT_CAPTURE_PAUSED:true`
- `SOFTWARE_DOCUMENTATION_SYNTHETIC_CI_ALLOWED:true`

The prior finding remains technically true that a real physical reference system and non-holdout calibration are eventually necessary to complete the purpose-built untouched external-validation route. The budget boundary means that route cannot advance into physical evidence now.

## What may continue at zero additional hardware cost

The branch may continue with software/document work that reduces future discretion and preserves readiness:
- deterministic schemas/contracts;
- reference-only validators;
- synthetic fixtures and regression tests;
- ordinary GitHub CPU CI within existing free/available capacity;
- Vercel-hosted tooling if it fits existing paid capacity and does not create new spend;
- capture/governance/population-binding code;
- synthetic no-real-correctness harnesses;
- documentation of the exact hard blocker that remains after software preparation.

No synthetic/software result may be relabeled as real external validation.

## Hard truth boundary

Without either:
1. a qualifying existing external corpus with independent real performed note truth and usable product-validation rights, or
2. real physical reference hardware plus non-holdout calibration,

the project cannot honestly establish untouched real-world external correctness for the purpose-built route.

The current public-corpus search remains without a known candidate clearing all frozen gates, so the budget-constrained path is to finish all defensible zero-cost preparation and stop at the physical-evidence boundary rather than lower the validation standard.

## Next software-only work

1. Freeze the Stage-0 contact replay/schema contract before any future bench data.
2. Implement that validator with synthetic-only fixtures and CI.
3. Continue freezing any remaining capture/population/governance software that can be completed without real data.
4. Keep a precise list of items that cannot be resolved without physical evidence so future funding can restart from a clean boundary.

## Authority boundary

No hardware purchase is authorized under the current budget constraint.
No real holdout exists.
No Basic Pitch/V6/correctness execution is authorized.

Keep:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Archived V143/Gomyway remains untouched and closed.
