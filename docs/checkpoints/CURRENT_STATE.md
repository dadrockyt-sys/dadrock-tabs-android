# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-07 America/Toronto
Branch: `v143-contextual-prune-lobo`

Compact fresh-chat source of truth. Full prior detail remains in Git history.

## SAFETY / AUTHORIZATION

Authorized model-bearing evaluation budget is consumed. Do **not** start another Rhythm/Lead/Bass model run, professional scorer, Modal/GPU inference, Production deployment/promotion, optimizer/training/threshold sweep, or manual workflow run without new explicit user authorization.

Safe work remains deterministic source/history inspection, static/unit validation, CPU-only synthetic proofs, CI/workflow cleanup, and safety hardening.

## FROZEN INVARIANTS — PRESERVE

- **725 retained attacks**
- **970 selected pitches**
- **967 rendered notes**
- exactly **3 legal-voicing drops**
- **0 recovery**
- all **113 measures** populated
- `referenceFree=true`
- `newInferenceUsed=false`

Exact drops: m40/s14 MIDI 78; m63/s14 MIDI 47; m113/s13 MIDI 43.

Async lifetime must remain:
- shared result/control TTL **1800s**
- orchestrator timeout **1200s**
- ownership margin **600s**

Endpoint exact blob must remain `169b4bb136eba742c3422a73ee5dd0174ca06c49`.

## SOURCE-ONLY FINAL SWEEP — INTERIM SAVE

Fresh-chat sweep began from branch head `72e2688cfcc1e7e93a074eef6cfa149273762b7b` (`docs: save fresh-chat source sweep handoff`), whose parent is `c3622076d57bfe95b148089f7d73c605fe2ec7fc`.

Verified directly on the current branch with **no workflow dispatch and no model/GPU/scorer/Production activity**:

1. `analyzer/v143_async_job_protocol.py`
   - `ASYNC_RESULT_TTL_SECONDS = 30 * 60` = **1800s**.
   - source documents the 20-minute worker/orchestrator budget plus 10-minute ownership margin.
   - protocol relationship remains **1800 / 1200 / 600**.

2. `app/api/analyze-audio-tab/route.js`
   - current Next.js async-result fallback remains **1800s**.
   - therefore the shared Python protocol and Next.js/runtime fallback agree.

3. `analyzer/v143_modal_http_endpoint.py`
   - current Git blob SHA is exactly **`169b4bb136eba742c3422a73ee5dd0174ca06c49`**.
   - orchestrator function timeout remains **1200s**.
   - no endpoint repin or runtime edit was made.

4. `.github/workflows/v143-ai-tab-real-audio-canary.yml`
   - inspected read-only.
   - trigger remains `workflow_dispatch` only; no automatic push trigger is present.
   - workflow was **not** dispatched or edited.

5. Persisted real-candidate PDF evidence at commit `2470225d9cb726e35a07459e29783997a3447699`
   - `debug/v143-contextual-prune/real-candidate-professional-pdf/render-report.json` records **967 source/projected events**, **113 unique measures**, and **725 unique onsets**.
   - it records `referenceFree: true`, `professionalReferenceUsed: false`, `modalInvoked: false`, and `productionModified: false`.
   - the historical workflow input named `debug/v143-contextual-prune-ci/pinned-capture/repaired-timing-precision-candidate-product.json`; that input is not a currently committed branch file, so this sweep is **not** treating the absent artifact as current-source proof for the remaining 970/3-drop/0-recovery fields.

Still being inspected before declaring the final sweep CLEAN:
- committed contract/evidence that preserves **970 selected pitches**;
- exactly the three legal-voicing drops (m40/s14 MIDI 78; m63/s14 MIDI 47; m113/s13 MIDI 43);
- **0 recovery** and `newInferenceUsed=false`;
- confirmation that recent documentation/CI-cleanup commits did not alter renderer event construction, thresholds, scheduler settings, model paths, endpoint selection, async ownership semantics, or Production behavior.

No source code, renderer behavior, thresholds, scheduler settings, model paths, endpoint selection, async semantics, Production behavior, or workflow source has been changed during this sweep. This checkpoint-only commit is the first requested progress save.

## PRESERVED GREEN STATE / HISTORY

Historical crash-loop root cause remains closed: persisted run `34047990402` proved `worker.done` after **936.836s** while the old ownership TTL was **900s**; runtime ownership is now **1800s** with **600s** margin over the **1200s** orchestrator ceiling.

Key repair/evidence commits preserved:
- `b55d9db517fe356b40600bae85ba98ead879aeb6` — shared async TTL 900 → 1800
- `330a3d5dbde5bcc3e51eb577892c8d9643fcba58` — Next.js fallback 900 → 1800
- `fd230ee2ad4c19ad4758bbc753f4d110233591ff` — stale async protocol gate aligned
- `c3c09c2d8e1c93f286d24e3c398922becaf8e8b8` — real-audio canary automatic push trigger removed
- `ab27ae3b95d6aa5942f2d456c3f29792c96ecc3b` — cleanup preview workflow converted to read-only verifier

Authoritative deterministic greens preserved from the prior checkpoint:
- V143 AI Tab Branch Build Gate `34174714737` — SUCCESS
- Rhythm Render Presentation CPU Proof `34174831412` — SUCCESS
- Rhythm Pre-Holdout Static Preflight `34175371296` — SUCCESS
- Rhythm Professional Holdout Self Test `34175371403` — SUCCESS
- Rhythm Pre-Holdout Static Preflight V2 `34175475746` — SUCCESS
- cleanup preview verification `34175871883` — SUCCESS

Prior static proof remains: schema-v7/product/runtime/anti-leakage/rendering checks, 400 synthetic events / 100 measures, valid full + preview PDFs, PDF event fidelity 1.0, frozen/PDF event hash `6475a7d68071a8810890982e1c06c0d39f99e85d646680706233ceed5a58b37e`, with no Production/model activity.

## NEXT SAFE WORK — EXACT ORDER

1. Finish only the remaining source/history inspection listed above.
2. Do **not** run Rhythm/Lead/Bass inference, Modal/GPU, professional scorer, optimizer/training, threshold sweeps, Production deploy/promotion, or any manual workflow.
3. If all frozen contract fields and source-diff checks are clean, update this checkpoint with exact evidence and mark the final sweep **CLEAN**.
4. Then stop changing code and leave the branch at the safe deterministic checkpoint until the user gives explicit new authorization for model-bearing evaluation or Production action.
5. If any invariant differs, record the exact discrepancy here before considering any fix; do not automatically change model/renderer behavior.

## NON-NEGOTIABLES

- **725 / 970 / 967 / exactly 3 drops / 0 recovery**
- **1800s / 1200s / 600s**
- endpoint blob `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- real-audio canary remains **manual-only**
- no new Modal/GPU/model inference, professional scoring, optimizer/training, threshold sweep, or Production promotion without explicit new authorization
- keep `docs/checkpoints/CURRENT_STATE.md` updated after each meaningful diagnosis/fix
