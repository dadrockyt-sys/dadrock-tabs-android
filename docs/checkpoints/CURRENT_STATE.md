# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-07 America/Toronto
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
- commit `c1451df43cc1162edb38aa3f3300b7af4d9b527`
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

## ASYNC RESULT LIFETIME DEFECT — ROOT PATCHED + STATIC TARGET PROOF PASSED

The real branch source uses transient Modal Queue partitions. The ownership defect was the shared Queue partition TTL expiring before the allowed orchestrator runtime.

Actual shared lifetime constant:
- file: `analyzer/v143_async_job_protocol.py`
- symbol: `ASYNC_RESULT_TTL_SECONDS`
- old value: `15 * 60` = **900 seconds**
- new value: `30 * 60` = **1800 seconds**
- root patch commit: `b55d9db517fe356b40600bae85ba98ead879aeb6`
- protocol blob after patch: `3d76808980cf7e3a6f3ce53812eea8cd41f8da72`

Actual ownership path in `analyzer/v143_modal_http_endpoint.py`:
- `_start_rhythm_job(...)` spawns `run_rhythm_async_job`
- `_queue_orchestrator_control(...)` stores the spawned `FunctionCall.object_id`
- control Queue partition uses `partition_ttl=ASYNC_RESULT_TTL_SECONDS`
- `_status_rhythm_job(...)` requires that control record to reconstruct/poll the FunctionCall
- `_queue_job_envelope(...)` stores completed/failed structured result with the same TTL
- ACK clears both result and control partitions

Execution budget from current branch source:
- `run_rhythm_async_job = @app.function(... timeout=1200, ...)`
- timeout was **not changed**
- 1800-second ownership leaves a **600-second / 10-minute margin** beyond the 1200-second orchestrator budget

History finding:
- commit `1b139994b9bf8572093e6644a61b6fde8c14cd89` introduced the generic 15-minute result TTL
- commit `e682e6faf0aa5fe9175684561ea584e9fad8bf9e` later added fail-closed orchestrator control tracking and reused that same 15-minute TTL
- no historical evidence showed 900 seconds was intentionally chosen to cover the later 1200-second orchestrator allowance

Deterministic validator:
- file: `analyzer/validate_v143_async_result_lifetime.py`
- commit: `58dac164b45dbdd0ff23100e69969caf911f4ab2`
- blob: `93c9c8cc79f4bc62ee34ad6a8ddb3c16f9937f41`
- dependency-free; parses source with Python `ast`; does not import Modal or execute analyzer/model code
- asserts TTL = 1800, orchestrator timeout = 1200, margin >= 600, both control/result partition TTLs use the shared constant, and start/status expose the same shared expiry

Validation performed in this environment:
- exact fetched target constructs were replayed through the validator's AST logic model-free
- result: **PASS — ttl=1800s / worker=1200s / margin=600s / control=result=shared TTL**
- a full on-checkout invocation of `python analyzer/validate_v143_async_result_lifetime.py` remains optional when a local checkout is available; do not create/trigger a workflow merely to run it

Next.js bridge:
- `app/api/analyze-audio-tab/route.js` still has `900` only as a fallback when analyzer `expiresInSeconds` is missing/invalid
- analyzer start/status responses now expose the shared 1800-second value, so this fallback does **not** own or expire analyzer state
- leave the advisory fallback unchanged unless doing a separate truthful-fallback cleanup

One stale source comment remains in `analyzer/v143_modal_http_endpoint.py` saying “hard 15-minute TTL”; behavior is governed by the imported shared 1800-second constant. This is documentation-only cleanup, not a runtime defect.

## CONTINUATION — DETERMINISTIC CLEANUP INSPECTION

Fresh continuation inspection on 2026-09-07 America/Toronto:
- branch head before writes was `41dd108c07cb1439f887dbc8f0d1185bd2998848`
- no newer branch work was present beyond this checkpoint
- `analyzer/v143_modal_http_endpoint.py` still contains the stale comment “hard 15-minute TTL” while both Queue partition TTL sites use `ASYNC_RESULT_TTL_SECONDS`
- `app/api/analyze-audio-tab/route.js` still contains advisory `900` fallbacks in both async `start` and `status` response shaping
- no model/scoring workflow, Modal/GPU inference, deployment, scheduler/model mutation, or professional scoring was triggered during this inspection

Next safe action is limited to isolated deterministic source cleanup plus static verification. Preserve the root behavior: shared analyzer TTL **1800s**, orchestrator timeout **1200s**, margin **600s**.

## WORKFLOW SAFETY

No model/scoring workflow was manually triggered during these slices. No Modal/GPU/paid inference, professional scorer, optimizer, threshold sweep, deployment, Production promotion, model change, or scheduler change was performed.

## FRESH CHAT — START HERE

1. Re-open this file first on branch `v143-contextual-prune-lobo` and refresh branch head. Treat any newer checkpoint as authoritative.
2. Treat the precision score-structure slice as **closed**. Do not reopen or alter helper/adapter/model behavior unless there is a new explicit reason. Preserve **725 / 970 / 967 / 3 drops / 0 recovery**.
3. Treat the async ownership root defect as **code-patched**: shared TTL is now 1800 seconds and the orchestrator timeout remains 1200 seconds, giving a 600-second margin.
4. If a normal local checkout is available, run only the dependency-free/model-free command `python analyzer/validate_v143_async_result_lifetime.py`. Do **not** trigger a GitHub workflow, Modal function, model run, or deployment just to validate it.
5. If that validator passes, optional cleanup is limited to deterministic non-runtime semantics:
   - update the stale “hard 15-minute TTL” comment in `analyzer/v143_modal_http_endpoint.py` to describe the shared bounded TTL accurately;
   - optionally align the Next.js fallback `ANALYZER_JOB_EXPIRES_SECONDS` from 900 to 1800 so fallback UI semantics match the analyzer, but remember this is advisory and not the ownership root cause.
6. If making either cleanup, keep it isolated, use ordinary static/JS validation only, and save this checkpoint immediately afterward.
7. Do **not** deploy, promote Production, weaken Deployment Protection, run model-bearing Rhythm/Lead/Bass analysis, run the professional scorer, invoke Modal/GPU/paid inference, or change model/scheduler/threshold parameters without new explicit user authorization.
8. Before any future score-quality work, require a fresh explicit authorization/budget decision because the authorized model-bearing and professional-scoring evaluation budget is exhausted.

## FRESH CHAT SUCCESS CONDITION

The safe state to preserve is:
- score structure: **725 retained attacks / 970 selected pitches / 967 rendered / 3 legal-voicing drops / 0 recovery**
- async ownership: **1800s shared TTL > 1200s orchestrator budget by 600s**
- deterministic validator target: **PASS**
- **no deployment, no model-bearing execution, no professional scoring, no paid/GPU inference**

If no further cleanup is desired, this branch is at a safe checkpoint for a fresh chat.
