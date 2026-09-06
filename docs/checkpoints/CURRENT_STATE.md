# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — **EXACT FALSE-TERMINAL ROOT CAUSE CONFIRMED; NARROW BRIDGE REPAIR + MODEL-FREE REGRESSION COMMITTED; AUTHORITATIVE MODEL-FREE CI GREEN; FINAL NET-DIFF AUDIT CLEAN.** Exactly one backend-capable real-audio start has ever been accepted in this phase; **NO SECOND START / NO RERUN**.  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Checkpoint 4 commit `f16598ac037c57f4166ed4e3d97c234dc61c8eb5` and older dedicated checkpoints remain authoritative for the full forensic timeline; omission here does not revoke frozen boundaries.

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

Run `33999777841`, job `101396439738`, re-arm commit `67e5224d9a72c11ce5ff5aa26538cd9cbe86a612`, exact Preview deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, source `0a07b393bb47123a1142fd46ea6d9a55b04f0486`:

- model-free protected-route preflight: HTTP `400`, route reached;
- exactly one approved real-audio Rhythm start: HTTP `202`, `startAccepted=true`, `startRequestSeconds=4.102068`, count `1`;
- first same-token status: client HTTP `502`, request `0.555108s`, async elapsed `13.075462102890015s`, bounded error `The analyzer job stopped before it could complete.`;
- same-token ACK: HTTP `200`, `ackRequestSeconds=0.396544`, transient result/control cleared;
- aggregate artifact `9979140544`, digest `sha256:dd5eaf0db145b4b8947b95b01e565893294508dda84c13e6452bf3b9771feca7`;
- raw request/response material + job token deleted after ACK;
- production/deployment-protection/reference-scoring safety accounting unchanged/zero.

**The one backend-capable start budget is consumed. Never rerun `33999777841`, `33999522733`, or `33998283085`; never send an ad-hoc replacement real-audio/model-bearing start.**

## FALSE TERMINAL FORENSICS — PROVEN

Already-completed read-only Modal diagnostic run `34000077005`, job `101397240115`, used log/history reads only and invoked no audio/model/worker.

- Orchestrator FunctionCall `fc-01M1SZSP90108F9D2EP8K4PWJ8`: `orchestrator.start` + `worker_call.start` at `23:52:28Z`.
- Modal bridge status POST completed at `23:52:33Z`; Next translated bounded bridge `status='failed'` to client `502`.
- ACK completed at `23:52:34Z`.
- Worker container started `23:52:34Z`; worker FunctionCall `fc-01M1SZST99RMZWN0SPV88WWEEB` logged `V143_STAGE worker.start` at `23:52:36Z`.
- Download/normalize/router/separator/Demucs/Roformer ran; Roformer completed around `23:54:04Z`; worker execution continued minutes beyond client `502` + ACK.

Therefore the accepted job was still legitimately in flight. ACK cleared bridge tracking but did not cancel the already-dispatched worker, leaving it orphaned from client lifecycle.

Later narrowed log-only run `34000153347` reported `workerFilteredLines=0` only because its regex omitted actual worker marker `V143_STAGE`; it is not contrary evidence.

## EXACT ROOT CAUSE — CONFIRMED

Modal public release commit `c3922a2c5719e5843618e8cd3fcf664cc1ddfeba` is Python SDK `1.5.5` and matches PyPI release provenance.

At exact Modal 1.5.5:

- `_Invocation.poll_function(timeout=...)` raises bare Python **built-in `TimeoutError()`** when the FunctionCall is unfinished and the immediate poll deadline is reached;
- `_functions.py` does not import `TimeoutError` from `modal.exception`, so the bare name is built-in;
- `modal.exception.TimeoutError` is separately defined as a distinct Modal-specific exception class.

Pre-repair bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005` caught only `modal.exception.TimeoutError` around `call.get(timeout=0)`. A normal in-flight built-in timeout therefore fell into generic `Exception`, returned bounded terminal `status='failed'`, and Next mapped it to client `502` while the worker was still cold-starting/running.

## NARROW REPAIR — COMMITTED / DIFF-AUDITED

Commit `62deec179531b0f3e67c0e833365c2274697f02d` changes exactly one source line in `analyzer/v143_modal_http_endpoint.py`:

- before: `except modal.exception.TimeoutError:`
- after: `except (TimeoutError, modal.exception.TimeoutError):`

GitHub commit diff confirms that is the only code change in the repair commit. Repaired bridge blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`.

No worker/model/scheduler/route/TTL/storage behavior changed. The catch remains narrow: legitimate built-in or Modal timeout => `processing`; unrelated exceptions still use the bounded terminal-failure branch.

## MODEL-FREE REGRESSION — COMMITTED

Commit `056508efdebc5973fde25cd4d83eb40108189231` adds `analyzer/test_v143_modal_http_endpoint_timeout_contract.py` (blob `938be19d064b7bb5d125bd886816129f455e5e14`).

The dependency-free regression does not import Modal. It locks:

1. `FunctionCall.get(timeout=0)` catches exactly `TimeoutError` + `modal.exception.TimeoutError`;
2. timeout handler returns `status='processing'` + `orchestratorRunning=True`;
3. generic `Exception` remains terminal failed with the existing bounded message;
4. Python matching classifies built-in timeout + Modal-like timeout as processing while `RuntimeError` remains failed.

## AUTHORITATIVE MODEL-FREE CI — GREEN

Commit `97b94e7fe2afc76e61ff2ddc89138849ed173f7d` adds `.github/workflows/v143-modal-timeout-contract.yml` (30 additions). It is push/path-scoped to this branch and the repair/test/workflow, with `contents: read`; no project secrets, Modal/Vercel auth, Blob/audio access, FunctionCall spawn, or model invocation.

Automatic push run `34000667026`, job `101398830737`, attempt `1`, checked out exact validation head `97b94e7fe2afc76e61ff2ddc89138849ed173f7d` and completed **SUCCESS** at `2026-09-06T00:12:26Z`.

Authoritative log evidence:

- `Compile bridge and regression` -> success;
- `Run timeout regression` -> success;
- `python -m py_compile analyzer/v143_modal_http_endpoint.py analyzer/test_v143_modal_http_endpoint_timeout_contract.py` -> success;
- `python analyzer/test_v143_modal_http_endpoint_timeout_contract.py` -> `Ran 3 tests in 0.007s` / `OK`;
- Actions permissions: `Contents: read`, `Metadata: read`;
- no manual dispatch or rerun.

A separate temporary workflow created during concurrent work (`97cfab26dafa4fa6ee3c1b63521fe52be35a481c`) never became validation evidence and was removed in `c19a72d0dd3a1c026c7249b84e2e15ea94771461`.

## FINAL NET-DIFF AUDIT — CLEAN

Audited base: exact-root-cause checkpoint `f16598ac037c57f4166ed4e3d97c234dc61c8eb5`.  
Audited branch head before this checkpoint write: `4f4dbfe102b73967673b91883d57b8f78dbe5c8b` (`docs: checkpoint green modal timeout validation`), parent `5fe9459ac67c5e3bd9b31474a9edc93a4a0d295e`.

GitHub compare reports the branch is `ahead` by 8 commits, behind by 0, with exactly four **net** changed files:

- `.github/workflows/v143-modal-timeout-contract.yml` — added, `+30/-0`;
- `analyzer/test_v143_modal_http_endpoint_timeout_contract.py` — added, `+119/-0`;
- `analyzer/v143_modal_http_endpoint.py` — modified, `+1/-1`;
- `docs/checkpoints/CURRENT_STATE.md` — checkpoint-only changes.

The temporary unregistered workflow is absent from the net diff. No worker, scheduler, route, protocol, model, storage, TTL, production, protection, or reference-scoring file is changed by this repair phase.

Safety accounting after diagnosis/repair/validation/audit remains:

- additional backend-capable real-audio starts: **0**;
- validation FunctionCalls/audio/model invocations: **0**;
- production promotion/change: **0**;
- Deployment Protection weakening: **0**;
- reference-facing inputs: **0**;
- reference score calls: **0**;
- quality verdicts: **0**;
- raw audio/stems/model bytes retained: **0**.

## NEXT — HOLD AT STATICALLY VALIDATED REPAIR

- Preserve the one-start budget as consumed and retain every hard stop below.
- Do not deploy/promote or perform live real-audio/model-bearing validation in this diagnostic phase without a new explicit authorization boundary.
- Future work may resume from this checkpoint with the repaired bridge + regression + GREEN model-free CI + clean final net-diff audit as authoritative state.

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

Current authorization state: **exact root cause fixed by the one-line bridge catch; regression committed; authoritative model-free CI GREEN; final net-diff audit clean; diagnostic phase is HOLD unless a new explicit authorization boundary is established.**
