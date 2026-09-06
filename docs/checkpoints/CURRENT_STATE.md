# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — **EXACT FALSE-TERMINAL ROOT CAUSE CONFIRMED AND NARROW BRIDGE REPAIR COMMITTED; MODEL-FREE REGRESSION COMMITTED; VALIDATION PENDING.** Exactly one backend-capable real-audio start has ever been accepted in this phase; **NO SECOND START / NO RERUN**.  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Checkpoint 4 commit `f16598ac037c57f4166ed4e3d97c234dc61c8eb5` and older dedicated checkpoints remain authoritative for full forensic detail; omission here does not revoke frozen boundaries.

## FROZEN BOUNDARIES

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**; **NO REFERENCE-FACING QUALITY VERDICT**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage remains transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900s; no persistent result cache.
- No production Vercel promotion/change; no Deployment Protection weakening; no whole-branch merge.
- Do not touch unrelated musical/reference issues or `core/engine/chord_mapping.py` octave folding.

## AUTHORITATIVE PRE-REPAIR PINS

- Route `742954146a86aa36485d0bbdb3fbd6691a64a712`.
- `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.
- Pre-repair bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`.
- Protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- V143 worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`.
- Scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Approved audio `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
- Repaired breakthrough helper blob `433599afec7fff20a31ea79e4c93ef9a6da03b36`.

## SINGLE CONSUMED BACKEND-CAPABLE START — DO NOT REPEAT

Run `33999777841`, job `101396439738`, re-arm commit `67e5224d9a72c11ce5ff5aa26538cd9cbe86a612` against exact Preview deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD` / source `0a07b393bb47123a1142fd46ea6d9a55b04f0486`:

- model-free protected-route preflight: HTTP `400`, route reached;
- exactly one approved real-audio Rhythm start: HTTP `202`, `startAccepted=true`, `startRequestSeconds=4.102068`, count `1`;
- first same-token status: client HTTP `502`, request `0.555108s`, async elapsed `13.075462102890015s`, bounded error `The analyzer job stopped before it could complete.`;
- same-token ACK: HTTP `200`, `ackRequestSeconds=0.396544`, transient result/control cleared;
- aggregate artifact `9979140544`, digest `sha256:dd5eaf0db145b4b8947b95b01e565893294508dda84c13e6452bf3b9771feca7`;
- raw request/response material and token were deleted after ACK;
- production/deployment protection/reference-scoring safety accounting remained unchanged/zero.

**The one backend-capable start budget is consumed. Never rerun `33999777841`, `33999522733`, or `33998283085`; never send an ad-hoc replacement real-audio start.**

## EXACT CALL FORENSICS — FALSE TERMINAL PROVEN

Already-completed read-only Modal diagnostic run `34000077005`, job `101397240115`, used log/history reads only and explicitly invoked no audio/model/worker.

- Orchestrator FunctionCall `fc-01M1SZSP90108F9D2EP8K4PWJ8` logged `orchestrator.start` and `worker_call.start` at `23:52:28Z`.
- Modal bridge status POST completed at `23:52:33Z`; Next.js translated bounded bridge `status='failed'` to client `502`.
- ACK completed at `23:52:34Z`.
- Worker container started `23:52:34Z`; worker FunctionCall `fc-01M1SZST99RMZWN0SPV88WWEEB` logged `V143_STAGE worker.start` at `23:52:36Z`.
- Download/normalize/router/separator/Demucs/Roformer then ran; Roformer completed around `23:54:04Z`, and worker execution continued minutes beyond the false client terminal response and ACK.

Therefore the accepted job was still legitimately in flight. ACK cleared bridge tracking but did not cancel the already-dispatched worker, leaving it orphaned from client lifecycle.

Later narrowed log-only run `34000153347` showed `workerFilteredLines=0` only because its filter matched `V143_ASYNC_STAGE` but omitted actual worker marker `V143_STAGE`; it is not evidence the worker failed to start.

## EXACT ROOT CAUSE — CONFIRMED

Modal public release commit `c3922a2c5719e5843618e8cd3fcf664cc1ddfeba` is explicitly Python SDK `1.5.5` and matches the PyPI release provenance.

At exact Modal 1.5.5:

- `_Invocation.poll_function(timeout=...)` raises bare Python **built-in `TimeoutError()`** when the FunctionCall is still unfinished and the immediate poll deadline is reached;
- `_functions.py` does not import `TimeoutError` from `modal.exception`, so the bare name is the built-in class;
- `modal.exception.TimeoutError` is separately defined as `class TimeoutError(Error)` and is a distinct Modal-specific exception class.

Pre-repair bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005` did:

`call.get(timeout=0)` -> catch only `modal.exception.TimeoutError` as `processing` -> generic `Exception` as terminal failed.

Thus a normal in-flight poll raised built-in `TimeoutError`, missed the intended handler, fell into generic `Exception`, returned bounded `status='failed'`, and Next.js mapped it to client `502` while the worker was still cold-starting/running.

## CHECKPOINT 5 — NARROW REPAIR COMMITTED

### Bridge repair

Commit `62deec179531b0f3e67c0e833365c2274697f02d` (`fix: treat Modal 1.5.5 pending poll as processing`) changes exactly one source line in `analyzer/v143_modal_http_endpoint.py`:

- before: `except modal.exception.TimeoutError:`
- after: `except (TimeoutError, modal.exception.TimeoutError):`

GitHub commit diff confirms this is the **only** code change in that commit. No worker/model/scheduler/route/TTL/storage behavior changed. Current repaired bridge blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`.

This keeps compatibility with both the built-in timeout actually raised by Modal 1.5.5 and the Modal-specific timeout class without broadening generic failure handling.

### Model-free regression committed

Commit `056508efdebc5973fde25cd4d83eb40108189231` adds only:

`analyzer/test_v143_modal_http_endpoint_timeout_contract.py`

The test is dependency-free and does not import Modal. It statically parses the actual bridge and asserts:

1. the `FunctionCall.get(timeout=0)` handler catches exactly both `TimeoutError` and `modal.exception.TimeoutError`;
2. that handler returns `status='processing'` with `orchestratorRunning=True`;
3. the following generic `Exception` handler remains terminal `status='failed'` with the existing bounded error;
4. Python exception matching classifies built-in timeout and a Modal-like timeout as processing while `RuntimeError` remains failed.

No CI status was attached automatically to the test commit. A tiny branch/path-scoped model-free Actions validation is the next step; it must only `py_compile` the bridge/test and run this unittest. It must not authenticate to Modal/Vercel, access Blob/audio, spawn FunctionCalls, or invoke models.

## NEXT — MODEL-FREE VALIDATION ONLY

1. Add/run a minimal branch/path-scoped GitHub Actions check that does only:
   - checkout;
   - `python -m py_compile analyzer/v143_modal_http_endpoint.py analyzer/test_v143_modal_http_endpoint_timeout_contract.py`;
   - `python analyzer/test_v143_modal_http_endpoint_timeout_contract.py`.
2. Inspect its existing run/log output and require GREEN before declaring repair statically validated.
3. Checkpoint run ID/job ID/commit and unchanged safety accounting.
4. **Do not deploy or validate this repair with another backend-capable real-audio/model-bearing request in this diagnostic phase.**

## HARD STOPS

- **NO SECOND REAL-AUDIO START. NO RERUN OF `33999777841`, `33999522733`, OR `33998283085`.**
- No ad-hoc real-audio request; no new FunctionCall/audio/model invocation for validation.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for this repair.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in retained evidence.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **exact root cause is confirmed; one-line bridge repair + dependency-free regression are committed; only model-free static validation and checkpointing are authorized next.**
