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

## ASYNC RESULT LIFETIME DEFECT — ROOT PATCH APPLIED, VALIDATION PENDING

Fresh source/history inspection proved the ~900-second expiry was a real ownership defect, distinct from worker execution timeout.

Actual ownership constant:
- file: `analyzer/v143_async_job_protocol.py`
- symbol: `ASYNC_RESULT_TTL_SECONDS`
- old value: `15 * 60` = **900 seconds**
- new value: `30 * 60` = **1800 seconds**
- patch commit: `b55d9db517fe356b40600bae85ba98ead879aeb6`
- current protocol blob: `3d76808980cf7e3a6f3ce53812eea8cd41f8da72`

Why 1800:
- `orchestrate_tab_job` and `async_worker` each retain the existing **1200-second / 20-minute** worker budget
- control ownership begins at job spawn
- 1800 keeps the protocol bounded/ephemeral while leaving a full **600-second / 10-minute margin** beyond the legitimate worker budget
- no worker/model/scheduler behavior was changed

History finding:
- commit `1b139994b9bf8572093e6644a61b6fde8c14cd89` originally introduced the generic 15-minute result TTL
- later commit `e682e6faf0aa5fe9175684561ea584e9fad8bf9e` added fail-closed orchestrator control tracking and reused that same 15-minute TTL for control ownership
- no historical evidence showed that 900 seconds was intentionally chosen to cover the later 1200-second worker budget; the reuse created the lifetime mismatch

Actual ownership use at job start remains:
- `start_tab_job(...)` creates `v143_async_controls.ephemeral(partition_ttl=ASYNC_RESULT_TTL_SECONDS)`
- it then spawns `orchestrate_tab_job` and stores the spawned `FunctionCall.object_id` in that control partition
- `poll_tab_job_status(...)` later depends on that control record to reconstruct `modal.functions.FunctionCall.from_id(...)`

Result lifetime remains related but starts later:
- `finalize_tab_job(...)` creates `v143_async_results.ephemeral(partition_ttl=ASYNC_RESULT_TTL_SECONDS)` only when finalizing
- ACK explicitly clears result/control partitions

Next.js bridge remains advisory, not ownership:
- `app/api/analyze-audio-tab/route.js` currently falls back to **900 seconds** when the analyzer omits/invalidates `expiresInSeconds`
- normal analyzer responses now inherit 1800 through the shared protocol constant
- decide during static validation whether to align only this advisory fallback for truthful degraded semantics; do not mistake it for the root fix

**Validation is still pending.** Do not claim this async slice closed until a dependency-free deterministic/static validator proves the ownership TTL exceeds the 1200-second worker budget and the intended ownership sites still use the shared constant.

## WORKFLOW SAFETY

No model/scoring workflow has been manually triggered during this work. Prior checkpoint push `36fc6bda1247bedbd9642a50b07ca4d52fbadb25` produced only `.github/workflows/cleanup-tab-preview.yml` run `34080214025`.

## NEXT EXACT STEPS

1. Add a dependency-free deterministic/static validator for the async lifetime boundary.
2. Prove `ASYNC_RESULT_TTL_SECONDS == 1800` and `> 1200`, with a 600-second margin.
3. Prove the start-time control partition and final result partition still use `ASYNC_RESULT_TTL_SECONDS`.
4. Prove both existing worker/orchestrator execution timeouts remain 1200; do not modify them.
5. Align the Next.js 900-second advisory fallback to 1800 only if validation confirms it is purely fallback/reporting semantics.
6. Run the validator locally/model-free if possible without triggering workflows or importing Modal; otherwise use static AST/text validation and record the limitation explicitly.
7. Checkpoint immediately after validation.
8. **Do not deploy or run model-bearing workflows.**

## SUCCESS CONDITION

Score-structure remains closed at **725 / 970 / 967 / 3 / 0 recovery**. Async success condition: **the start-time control/result ownership lifetime must safely exceed the 1200-second worker budget, with deterministic proof and no deployment/model-bearing execution.**
