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

**New push-safety warning:** ordinary source pushes on this branch can automatically trigger workflows. In particular, changing `analyzer/v143_modal_http_endpoint.py` automatically triggers `V143 Hardened Async Failfast Smoke`, which deploys an isolated Modal bridge + failfast driver and invokes the synthetic driver. Therefore do **not** make another ordinary endpoint/source push without first accounting for workflow side effects. An uppercase `[Skip CI]` commit message did **not** suppress these branch workflows and must not be relied on.

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

Validation already established:
- **PASS — ttl=1800s / worker=1200s / margin=600s / control=result=shared TTL**
- do not create/trigger a workflow merely to re-run it

## CURRENT SOURCE STATE

### Analyzer endpoint — exact pin restored

`analyzer/v143_modal_http_endpoint.py` is restored to the pre-cleanup exact blob:
- blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- restore commit: `708c4fccb0e6c67c4879fb1ead6446955878f95f`

The stale source comment still says “same hard 15-minute TTL”. This wording is intentionally left stale because a comment-only edit changed the exact endpoint blob and broke exact-source static pins. Runtime behavior remains governed by `ASYNC_RESULT_TTL_SECONDS = 1800`; do **not** reopen the comment cleanup absent a coordinated pin/workflow decision.

### Next.js advisory fallback — aligned

`app/api/analyze-audio-tab/route.js` keeps the isolated truthful-fallback cleanup from commit `330a3d5dbde5bcc3e51eb577892c8d9643fcba58`:
- async `start` fallback: `1800`
- async `status` fallback: `1800`
- exact source change was two numeric literal replacements `900` → `1800`
- analyzer-provided `expiresInSeconds` remains authoritative; the bridge fallback does not own or expire analyzer state

Static failures observed after that route push are not caused by the two fallback literals:
- pre-holdout static preflight failed at existing final Rhythm PDF renderer/branding contract checks; its analyzer-route runtime-safety check passed
- Full Mixture Server Observation Admission V1 failed a brittle source-order assertion requiring `responseOkIndex < v143SafetyIndex < structuredPayloadIndex`; the route defines `v143RuntimeSafetyVerified` inside `buildCompletedProductPayload()` near the top, so that assertion is independent of the later `900` → `1800` replacements

## READ-ONLY PDF CONTRACT DIAGNOSIS — 2026-09-07

Latest continuation began from branch head `0b5a786ad21fbc2890f76706a0e409e2c49d5778` with no intervening work.

`Rhythm Pre-Holdout Static Preflight V2` is defined by `.github/workflows/rhythm-preholdout-static-preflight-v2.yml` and runs `validation/rhythm_holdout/run_static_preholdout_preflight.sh` against synthetic-only data. The workflow itself persists canonical evidence back to the branch, so ordinary writes to its watched paths can cause an automatic bot evidence commit.

The `ai-tab-pdf-product-contract` failure is now isolated to literal branding-contract drift in `lib/createV143RhythmPdf.js`, not musical placement or render-event validation:
- exact renderer event validation is present: `const events = validateV143RenderEvents(renderEvents)`
- non-empty complete stream fail-closed behavior is present
- exact logo path is present: `path.join(process.cwd(), 'public', 'DadRock-Tabs-Logo.png')`
- preview watermark `DADROCK TABS PREVIEW` is present
- preview lock logic `preview && index >= clearPreviewSystems` is present
- the verifier's branding check additionally requires four strings that are currently absent from this renderer:
  - `DIY Guitar & Bass TAB Generator`
  - `Powered by DadRock AI • V143 Rhythm`
  - `FULL TAB LOCKED`
  - `Generated by DadRock Tabs Studio • dadrocktabs.com`
- current renderer instead uses `PREVIEW LOCKED`, a simple `DadRock Tabs Studio` center footer, and `dadrocktabs.com` separately

Therefore `structured-rhythm-polished-branding-and-preview-lock` fails, which makes `polishedBrandingContractPassed=false` and in turn causes `ai-tab-pdf-product-contract` / static preflight failure. This diagnosis is source-only and required no PDF render, model, scorer, Modal, GPU, real audio, or Production action.

Before editing `lib/createV143RhythmPdf.js`, first enumerate every workflow path trigger that watches that file. Do not assume the preflight workflow is the only automatic side effect.

## AUTOMATIC WORKFLOW SIDE EFFECTS DISCOVERED DURING THIS CONTINUATION

No workflow was manually triggered. However, source pushes automatically triggered branch workflows.

Comment cleanup commit `2f630afcfa7222a3af823661e45546b19f305f0c`:
- changed only endpoint comment wording
- automatically triggered seven push workflows
- exact-source gates failed because the endpoint blob changed from pinned `169b4bb...`
- `V143 Hardened Async Failfast Smoke` automatically deployed an **isolated** Modal bridge + failfast driver and invoked its synthetic driver
- that workflow enforces: `audioRead=false`, `modelExecuted=false`, `separatorModelExecuted=false`, `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`, then stops the isolated apps
- no model-bearing analysis, real audio, GPU inference, professional reference scoring, optimizer, or Production promotion occurred

Route fallback commit `330a3d5dbde5bcc3e51eb577892c8d9643fcba58`:
- automatically triggered route-path static/build workflows
- `Rhythm Pre-Holdout Static Preflight V2` used synthetic-only input and failed unrelated final-renderer/branding checks
- the workflow automatically persisted failed static evidence via bot commit `0c4a51879dacc707f6eecc310709acfe3069ce59` in `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json`
- no real professional reference was opened and no Production modification was authorized

Endpoint restore commit `708c4fccb0e6c67c4879fb1ead6446955878f95f`:
- commit message used uppercase `[Skip CI]`, but this repo still created seven push workflows; therefore do **not** rely on that token/casing here
- `V143 Hardened Async Failfast Smoke` run `34084988160` automatically executed again
- it completed **successfully**, including the final **Stop isolated apps** step
- the same enforced no-audio/no-model/no-reference safety contract passed
- the endpoint exact blob is restored to `169b4bb...`

Cloudflare Pages also reacts to ordinary branch pushes. A checkpoint-only push previously produced a failed Cloudflare build attempt. Treat branch pushes as externally observable actions even when GitHub workflow path filters exclude the changed file.

## CONTINUATION COMMITS

Starting branch head: `41dd108c07cb1439f887dbc8f0d1185bd2998848`

Continuation history:
- `8df101086c8fb21a4a4dc3da6fb377d57b26c300` — inspection checkpoint
- `2f630afcfa7222a3af823661e45546b19f305f0c` — attempted comment-only TTL wording cleanup
- `f618b314447430aba6248bc3f474c75d9b2ab79e` — intermediate checkpoint
- `330a3d5dbde5bcc3e51eb577892c8d9643fcba58` — Next.js fallback `900` → `1800`
- `0c4a51879dacc707f6eecc310709acfe3069ce59` — automatic Actions bot static-preflight evidence commit
- `1aed09858a1e52041e2298eba28d1237f0660e34` — prior checkpoint
- `708c4fccb0e6c67c4879fb1ead6446955878f95f` — endpoint exact-source restore
- `0b5a786ad21fbc2890f76706a0e409e2c49d5778` — automation-side-effects checkpoint

## WORKFLOW SAFETY — UPDATED

No model/scoring workflow was manually triggered. No model-bearing Rhythm/Lead/Bass analysis, professional scorer, optimizer, training/threshold sweep, real-audio inference, GPU model execution, Production promotion, or model/scheduler mutation was performed during this continuation.

But automatic push workflows **did** invoke isolated Modal infrastructure twice through the synthetic Hardened Async Failfast Smoke path. Both runs are contractually no-audio/no-model/no-reference, and the latest run `34084988160` completed its `Stop isolated apps` cleanup successfully. This is why future ordinary source pushes must not be treated as purely static.

## FRESH CHAT — START HERE

1. Re-open this file first on branch `v143-contextual-prune-lobo` and refresh branch head. Treat any newer checkpoint as authoritative.
2. Preserve score structure: **725 retained attacks / 970 selected pitches / 967 rendered / 3 legal-voicing drops / 0 recovery**. Do not reopen the score-structure slice absent new explicit authorization/reason.
3. Preserve async root behavior: shared analyzer TTL **1800s**, orchestrator timeout **1200s**, margin **600s**.
4. Preserve endpoint exact blob `169b4bb136eba742c3422a73ee5dd0174ca06c49`. Leave the stale 15-minute comment alone unless exact-source pins and automatic workflow consequences are deliberately handled together.
5. Keep the Next.js advisory fallback at **1800s on start + status** unless new evidence shows a problem; current observed static failures are unrelated to those two numeric replacements.
6. The current PDF static failure is isolated to four missing branding strings in `lib/createV143RhythmPdf.js`; before any edit, enumerate all push workflows watching that file and verify none crosses the authorization boundary.
7. **Do not make an ordinary push to `analyzer/v143_modal_http_endpoint.py`**: it auto-triggers an isolated Modal deploy/invocation workflow. Do not assume `[Skip CI]` uppercase suppresses it; it did not.
8. Do not manually trigger any workflow, Modal function, model run, scorer, deployment, or Production action merely to validate source.
9. Do **not** run model-bearing Rhythm/Lead/Bass analysis, professional scoring, paid/GPU inference, optimizer/training/threshold sweeps, or change model/scheduler/threshold parameters without new explicit user authorization.
10. Before any future score-quality work, require a fresh explicit evaluation-budget decision because the authorized model-bearing and professional-scoring evaluation budget is exhausted.

## FRESH CHAT SUCCESS CONDITION

Safe state to preserve:
- score structure: **725 / 970 / 967 / 3 drops / 0 recovery**
- async ownership: **1800s shared TTL > 1200s orchestrator by 600s**
- endpoint exact pin: **169b4bb... restored**
- Next.js fallback semantics: **1800s on start + status**
- latest automatic synthetic failfast run: **success, isolated apps stopped, no audio/model/reference scoring**
- current PDF diagnosis: **branding-contract drift only; no render-event/musical-placement defect identified in this slice**
- **no model-bearing execution, no professional scoring, no paid/GPU inference, no Production promotion**

This branch is at a safe deterministic checkpoint. Future work should begin with read-only inspection and explicit push-side-effect review before any write.
