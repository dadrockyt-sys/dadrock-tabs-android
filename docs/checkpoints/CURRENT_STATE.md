# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`

Compact fresh-chat source of truth. Full prior detail remains in Git history.

## AUTHORIZATION / SAFETY BOUNDARY

Authorized evaluation budget is consumed:
- replacement V143 Rhythm model-bearing start: **0 available / 1 consumed**
- professional full-1–113 score: **0 available / 1 consumed**
- replacement PDF E2E: **1 performed / passed**

**DO NOT** start another model-bearing Rhythm/Lead/Bass analysis, run the professional scorer, invoke Modal/GPU/paid inference, run optimizer/training/threshold sweeps, deploy/promote Production, weaken Deployment Protection, or mutate model/scheduler parameters without new explicit user authorization.

Safe continuation: deterministic/model-free source/history inspection, static/unit validation, and CPU-only/read-only replay of already-persisted evidence. Do not manually trigger workflows.

## FROZEN LIVE / HOLDOUT — DO NOT RERUN

Authorized Rhythm run `34046854397`, recovery `34048291636`:
- **364 selected attacks / 925 rendered notes**
- PDF event fidelity **1.0**

Consumed professional holdout `34048719525`:
- `near100ProfessionalGatePassed=false`
- pitch-content F1 `0.30892570817744525`
- pitch-timing tolerant F1 `0.05879208979155532`
- chord pitch-set tolerant F1 `0.004136504653567736`
- unmatched generated/reference: `779 / 800`

Infrastructure/rendering succeeded; musical score construction did not. **Do not tune against the professional reference.**

## PERSISTED PRECISION EVIDENCE

Authorized paid capture run `32805316807`:
- commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`
- artifact `v143-precision-v2-one-shot-32805316807`, id `9548666053`
- fixture SHA-256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- artifact digest `sha256:5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`
- no further paid capture authorized

Persisted invariants:
- 113 measures
- 725 retained attacks
- 970 precision-v2 selected pitches
- 967 rendered after deterministic guitar voicing
- exactly 3 legal-voicing drops
- 0 recovered/pruned hypotheses
- 0 primary failures
- 0 unobserved attacks/pitches
- all 113 measures populated

Schema-2: 984 eligible attacks / 7535 candidate hypotheses / 725 retained / 970 selected / 967 rendered; `referenceFree=true`, `newInferenceUsed=false`, `failSafeAttackCount=0`.

## SCORE-STRUCTURE PRESERVATION SLICE — CLOSED

Current blobs:
- helper `analyzer/v143_precision_polyphony_boundary.py`: `83a1d993ff654c45bb965a7794f2d155aab18a25`
- adapter `analyzer/v143_contextual_prune_precision_candidate_events.py`: `509032e3969ea057c05743c148ade2d2d4da4bf0`
- validator `analyzer/validate_v143_precision_polyphony_preservation.py`: `8f4c420482674f484541a4c6d5bf90df0d7f6465`

Commits:
- adapter hardening `255616674eb4d113804d5a4296b771318717745f`
- validator `838d900732abeb19740bea0ca8a23131a8701fe3`

Policy is preservation-only at helper + adapter: precision-v2 retained set is sole authority; primary immutable; any recovery/widening raises; legacy recovery metadata is hard false.

Dependency-free validator: **PASS**.
Persisted current-helper replay: **725 / 970 / 967 / 3 drops / 0 recovery**.
Exact drops: m40/s14 MIDI 78; m63/s14 MIDI 47; m113/s13 MIDI 43.

## ASYNC RESULT LIFETIME DEFECT — ACTUAL BOUNDARY LOCATED, NOT YET PATCHED

Fresh source inspection proved the ~900-second expiry is a real ownership defect, distinct from worker execution timeout.

Actual ownership constant:
- file: `analyzer/v143_async_job_protocol.py`
- symbol: `ASYNC_RESULT_TTL_SECONDS`
- current value: `15 * 60` = **900 seconds**

Actual ownership use at job start:
- file: `analyzer/v143_modal_http_endpoint.py`
- `start_tab_job(...)` creates `v143_async_controls.ephemeral(partition_ttl=ASYNC_RESULT_TTL_SECONDS)`
- it then spawns `orchestrate_tab_job` and stores the spawned `FunctionCall.object_id` in that control partition
- `poll_tab_job_status(...)` later depends on that control record to reconstruct `modal.functions.FunctionCall.from_id(...)`
- if the control record is absent/expired, status reports that the token is unknown/expired

Worker execution budget:
- `orchestrate_tab_job = app.function(... timeout=1200, ...)`
- `async_worker = app.function(... timeout=1200, ...)`

Therefore the control partition can expire at **t=900** while a valid orchestrator/worker is still allowed to run until **t=1200**. The status/control ownership can disappear **300 seconds before** the legitimate worker budget ends.

Result lifetime is related but starts later:
- `finalize_tab_job(...)` creates `v143_async_results.ephemeral(partition_ttl=ASYNC_RESULT_TTL_SECONDS)` only when finalizing, so its 900-second clock is a post-completion retrieval window rather than the start-time ownership defect
- ACK explicitly clears result/control partitions

Next.js bridge is not the owner:
- `app/api/analyze-audio-tab/route.js` has fallback/advisory `ANALYZER_JOB_EXPIRES_SECONDS = 15 * 60`
- it normalizes `expiresInSeconds`, but does not own or delete the analyzer control/result record
- align it later only if needed for truthful fallback semantics; do not mistake it for the root cause

**Decision before patch:** inspect history and current async validators/tests to determine the intended safe TTL/margin. Do not guess a replacement value. Patch only the actual ownership lifetime (and any purely advisory mirror needed for consistency), then add deterministic/static validation proving ownership TTL exceeds the 1200-second worker budget.

## WORKFLOW SAFETY

No model/scoring workflow has been manually triggered during this work. Prior checkpoint push `36fc6bda1247bedbd9642a50b07ca4d52fbadb25` produced only `.github/workflows/cleanup-tab-preview.yml` run `34080214025`.

## NEXT EXACT STEPS

1. Inspect commit history for `analyzer/v143_async_job_protocol.py` and `analyzer/v143_modal_http_endpoint.py` around async TTL introduction/changes.
2. Locate any existing async protocol validator/test on this branch.
3. Establish intended TTL > 1200 with an explicit safety/retrieval margin from existing design/history rather than guessing.
4. Checkpoint again before patch if history changes interpretation.
5. Make the smallest isolated lifetime patch; do not change worker/model/scheduler behavior.
6. Add/run dependency-free deterministic/static validation.
7. Checkpoint immediately after patch/validation.
8. **Do not deploy or run model-bearing workflows.**

## SUCCESS CONDITION

Score-structure remains closed at **725 / 970 / 967 / 3 / 0 recovery**. Async success condition: **the start-time control/result ownership lifetime must safely exceed the 1200-second worker budget, with deterministic proof and no deployment/model-bearing execution.**
