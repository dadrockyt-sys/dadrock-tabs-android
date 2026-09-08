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

Safe continuation: deterministic/model-free source/history inspection, static/unit validation, CPU-only/read-only replay of already-persisted evidence, and safety hardening that prevents accidental model-bearing push workflows. Do not manually trigger workflows.

## FROZEN SCORE / HOLDOUT — DO NOT RERUN

Persisted score-structure invariants are closed and must remain unchanged:
- **725 retained attacks**
- **970 selected pitches**
- **967 rendered notes**
- exactly **3 legal-voicing drops**
- **0 recovery**
- all 113 measures populated
- `referenceFree=true`
- `newInferenceUsed=false`

Exact drops: m40/s14 MIDI 78; m63/s14 MIDI 47; m113/s13 MIDI 43.

Consumed professional holdout remains failed musically and must not be tuned against:
- `near100ProfessionalGatePassed=false`
- pitch-content F1 `0.30892570817744525`
- pitch-timing tolerant F1 `0.05879208979155532`
- chord pitch-set tolerant F1 `0.004136504653567736`

## ASYNC RESULT LIFETIME — ROOT PATCHED

Shared ownership lifetime is intentionally:
- `analyzer/v143_async_job_protocol.py`
- `ASYNC_RESULT_TTL_SECONDS = 30 * 60` = **1800s**
- root patch commit `b55d9db517fe356b40600bae85ba98ead879aeb6`
- protocol blob `3d76808980cf7e3a6f3ce53812eea8cd41f8da72`

Orchestrator budget remains:
- `run_rhythm_async_job` timeout **1200s**
- ownership margin **600s**

The ownership path remains Queue-based: start spawns a Modal `FunctionCall`, control metadata stores its object id under the shared TTL, status reconstructs/polls that FunctionCall, completed/failed structured results use the same TTL, and ACK clears both result/control partitions.

Next.js advisory fallback remains aligned at **1800s** on async start + status via commit `330a3d5dbde5bcc3e51eb577892c8d9643fcba58`.

## CRASH-LOOP BREAKTHROUGH — 2026-09-07

The preserved historical Modal diagnostic proves the apparent crash-loop job did **not** terminate in a worker crash.

Evidence:
- diagnostic workflow: `.github/workflows/v143-modal-crash-log-diagnostic.yml`
- diagnostic run: `34047990402`
- preserved artifact id: `9993685857`
- live app in diagnostic: `dadrock-v143-ai-tab-live`
- historical FunctionCall: `fc-01M1VT9BDS5TYWE52GPYQQ8W9E`
- artifact logs reach `worker.done`
- measured completion time: **936.836 seconds**
- the TensorFlow cuDNN/cuFFT/cuBLAS CUDA registration messages in the log were non-terminal startup noise; no later terminal traceback was found

Root-cause timing match:
- old shared ownership/control TTL: **900s**
- worker completion: **936.836s**
- ownership therefore expired about **36.836s before the worker completed**

This explains the user-visible/status-layer failure pattern: the long-running job could remain valid and eventually complete while the async control/result ownership record had already expired. The runtime TTL repair to **1800s** removes that premature ownership loss and preserves a **600s margin** over the 1200s orchestrator ceiling.

No new Modal/model execution was performed to establish this; the conclusion comes from persisted diagnostic evidence plus current source/history inspection.

## STALE ASYNC PROTOCOL GATE — FIXED + GREEN

A separate CI error was stale validation, not runtime behavior.

`analyzer/v143_async_job_protocol_gate.py` still asserted:
- TTL `900`
- exact old exception spelling `except modal.exception.TimeoutError:`

Current source intentionally requires:
- TTL `1800`
- timeout handling `except (TimeoutError, modal.exception.TimeoutError):`

Fix commit:
- `fd230ee2ad4c19ad4758bbc753f4d110233591ff`
- message: `fix(v143): align async protocol gate with 30-minute ownership`
- only `analyzer/v143_async_job_protocol_gate.py` changed
- no endpoint/model/renderer/scoring code changed

Automatic verification:
- workflow: `V143 Async Job Protocol Gate`
- run: `34173726834`
- result: **SUCCESS**
- source-only; no Modal/model execution

An unrelated `cleanup-tab-preview` run `34173725948` also appeared and failed immediately. Its current workflow file only watches `.github/workflows/cleanup-tab-preview.yml`, so it is not a current renderer watcher and is being treated as separate Actions noise/cleanup debt.

## ENDPOINT EXACT PIN — PRESERVE

`analyzer/v143_modal_http_endpoint.py` must remain exact blob:
- `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- restore commit `708c4fccb0e6c67c4879fb1ead6446955878f95f`

The stale source comment mentioning a 15-minute TTL is intentionally left alone because prior comment-only changes broke exact-source pins. Runtime behavior comes from the shared 1800s constant.

## PDF CONTRACT DIAGNOSIS — STILL OPEN

`lib/createV143RhythmPdf.js` already has:
- `const events = validateV143RenderEvents(renderEvents)`
- non-empty complete-stream fail-closed behavior
- exact logo path `public/DadRock-Tabs-Logo.png`
- preview watermark `DADROCK TABS PREVIEW`
- preview lock condition `preview && index >= clearPreviewSystems`

The remaining static product-contract drift is four missing exact branding strings:
- `DIY Guitar & Bass TAB Generator`
- `Powered by DadRock AI • V143 Rhythm`
- `FULL TAB LOCKED`
- `Generated by DadRock Tabs Studio • dadrocktabs.com`

Current renderer instead contains `PREVIEW LOCKED`, a simpler `DadRock Tabs Studio` footer, and `dadrocktabs.com` separately. Musical/event construction must remain untouched.

## RENDERER PUSH WORKFLOW AUDIT — CRITICAL FINDING

Historical renderer commit `08ee3bcc1cec3428641741a8281206aa4218cb8d` woke seven workflows. Current definitions were re-audited before any renderer edit.

Current renderer watchers confirmed:

1. `.github/workflows/rhythm-render-presentation-proof.yml`
   - explicitly watches `lib/createV143RhythmPdf.js`
   - CPU-only synthetic presentation/render proof
   - installs only isolated `pdf-lib` + `pypdf`
   - no Modal/GPU/real audio/professional reference/Production action

2. `.github/workflows/v143-ai-tab-branch-build-gate.yml`
   - explicitly watches renderer
   - local Next.js build/server and stubbed localhost analyzer HTTP tests
   - evidence explicitly records `actualVercelPreviewDeployment=false`, `vercelDeploymentAttempted=false`, `liveEndpointDeployedOrModified=false`, `productionModified=false`
   - no external analyzer/model run

3. `.github/workflows/rhythm-professional-holdout-self-test.yml`
   - explicitly watches renderer
   - despite the name, constructs `.synthetic-self-test.json` with provenance `synthetic CI contract fixture only; not real ground truth`
   - verifies runtime isolation and positive/negative scorer contract behavior against synthetic fixtures
   - no real professional reference/model run

4. `.github/workflows/rhythm-preholdout-static-preflight.yml`
   - explicitly watches renderer
   - deterministic/static, synthetic-only
   - can persist compact evidence back to branch

5. `.github/workflows/rhythm-preholdout-static-preflight-v2.yml`
   - explicitly watches renderer
   - deterministic/static, synthetic-only
   - can persist canonical evidence back to branch

6. `.github/workflows/v143-ai-tab-real-audio-canary.yml`
   - **UNSAFE FOR AN ORDINARY RENDERER PUSH UNDER CURRENT AUTHORIZATION**
   - explicitly watches `lib/createV143RhythmPdf.js`
   - has Modal credentials in job environment
   - if credentials exist, runs `python -m modal run analyzer/v143_ai_tab_product_canary_modal.py::run --audio-path public/gomywayfullaitest.m4a ...`
   - therefore a renderer push can invoke real audio + Modal/model execution

7. `.github/workflows/cleanup-tab-preview.yml`
   - current `push.paths` contains only its own workflow file
   - **does not currently watch the renderer**

Conclusion: **DO NOT push the renderer while the real-audio canary remains automatically push-triggered by renderer changes.**

Preferred safety hardening before renderer patch: make the real-audio product canary manual-only (`workflow_dispatch`) so expensive/model-bearing canary execution requires an explicit action instead of an ordinary source push. Preserve the canary itself; only remove automatic push invocation. Verify that workflow-safety edit itself does not invoke Modal before proceeding.

## CONTINUATION COMMITS

Relevant recent history:
- `b55d9db517fe356b40600bae85ba98ead879aeb6` — shared async TTL 900 → 1800
- `58dac164b45dbdd0ff23100e69969caf911f4ab2` — deterministic async lifetime validator
- `330a3d5dbde5bcc3e51eb577892c8d9643fcba58` — Next.js fallback 900 → 1800
- `708c4fccb0e6c67c4879fb1ead6446955878f95f` — endpoint exact-source restore
- `7876c47d82a4755f296b1c5bb7ecc0c2b3b23cfe` — PDF-contract diagnosis checkpoint
- `9e7b3a8e42e67c6b304ff44e14f2d6d2b0669987` — prior fresh-chat checkpoint
- `fd230ee2ad4c19ad4758bbc753f4d110233591ff` — stale async protocol gate aligned; automatic gate green

## NEXT STEPS

1. Preserve **725 / 970 / 967 / 3 drops / 0 recovery**.
2. Preserve **1800s / 1200s / 600s**.
3. Preserve endpoint blob `169b4bb136eba742c3422a73ee5dd0174ca06c49`.
4. Harden `.github/workflows/v143-ai-tab-real-audio-canary.yml` so the real-audio Modal canary is **manual-only**, not automatically triggered by renderer/source pushes. Do not execute it.
5. Verify the safety-hardening push spawned no model-bearing/Modal run.
6. Re-read the exact PDF validator expectations and `lib/createV143RhythmPdf.js` header/subtitle/lock/footer.
7. Make only the minimal four-string renderer branding patch; do not change events, note placement, attacks, pitches, voicing, model/scheduler parameters, or fail-closed validation.
8. Immediately inspect all automatic runs after renderer push. Expected safe automatic work after canary hardening: CPU presentation proof, local build/stub smoke, synthetic holdout self-test, static preflights; no real audio/Modal/model.
9. Expect preflight workflows may persist bot evidence commits.
10. Diagnose the unrelated `cleanup-tab-preview` failure separately; do not mix it into the renderer or async lifetime repair.

## SUCCESS CONDITION

- crash-loop ownership defect explained by persisted timing evidence: **900s ownership < 936.836s completed worker**
- runtime ownership fixed: **1800s > 1200s by 600s**
- stale protocol CI gate fixed and **green** (`34173726834`)
- score structure unchanged: **725 / 970 / 967 / 3 / 0**
- endpoint exact pin preserved
- renderer branding contract still awaiting safe four-string patch
- real-audio canary must be removed from automatic renderer pushes before that patch
- **no new model-bearing run, no professional scoring, no paid/GPU inference, no Production promotion**
