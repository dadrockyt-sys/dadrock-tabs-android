# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-07 America/Toronto
Branch: `v143-contextual-prune-lobo`

Compact fresh-chat source of truth. Full prior detail remains in Git history.

## SAFETY / AUTHORIZATION

Authorized model-bearing evaluation budget is consumed. Do **not** start another Rhythm/Lead/Bass model run, professional scorer, Modal/GPU inference, Production deployment/promotion, optimizer/training/threshold sweep, or manual workflow run without new explicit user authorization.

Safe work: deterministic source/history inspection, static/unit validation, CPU-only synthetic proofs, CI/workflow cleanup, and safety hardening.

## FROZEN INVARIANTS — PRESERVE

- **725 retained attacks**
- **970 selected pitches**
- **967 rendered notes**
- exactly **3 legal-voicing drops**
- **0 recovery**
- all 113 measures populated
- `referenceFree=true`
- `newInferenceUsed=false`

Exact drops: m40/s14 MIDI 78; m63/s14 MIDI 47; m113/s13 MIDI 43.

Async lifetime must remain:
- shared result/control TTL **1800s**
- orchestrator timeout **1200s**
- ownership margin **600s**

Endpoint exact blob must remain `169b4bb136eba742c3422a73ee5dd0174ca06c49`.

## CORE V143 RHYTHM STATE — GREEN / CLOSED

Historical crash-loop root cause is closed: persisted run `34047990402` proved the worker reached `worker.done` after **936.836s** while old ownership TTL was **900s**. Runtime ownership is now **1800s**, leaving a **600s** margin over the 1200s orchestrator ceiling.

Key completed fixes/evidence:
- `b55d9db517fe356b40600bae85ba98ead879aeb6` — shared async TTL 900 → 1800
- `330a3d5dbde5bcc3e51eb577892c8d9643fcba58` — Next.js fallback 900 → 1800
- `fd230ee2ad4c19ad4758bbc753f4d110233591ff` — stale async protocol gate aligned; run `34173726834` SUCCESS
- `c3c09c2d8e1c93f286d24e3c398922becaf8e8b8` — real-audio canary automatic push trigger removed; canary is manual-only
- `0b403b6419180be3bcf9dc0b42894411fa2e34de` — V143 PDF branding contract restored
- `6b8f3a6b277f13b8c5083fbc64cbe39fd044077f` — whole-number BPM, visible 16th-note timing, SECTION labels
- `a088bf4957fb5c472ebbd1a280a1b3093e7e30bc` — stale renderer proof transform fixed
- `da736e5c83772feac1b9471cbad690b296831951` — built HTTP gate now explicitly requests supported `operation: 'analyze'`
- `b94af651807a7597eedeb9f9d3ba2838493e80cc` — stale PDF product-contract source assertion fixed
- `17b07a67d13463197b2a30d8e6d38a4627e60a1c` — static preholdout ESM transform fixed
- `d035dc668141f4e04fa3b80cc93ceb226c914387` — CI-only successful-worktree cleanup before evidence rebase
- `36dbf6e79a712824dbcf677e2e83ae83e223099b` — bounded evidence push retry for branch races

Authoritative deterministic greens:
- **V143 AI Tab Branch Build Gate** — `34174714737` — SUCCESS
- **Rhythm Render Presentation CPU Proof** — `34174831412` — SUCCESS
- **Rhythm Pre-Holdout Static Preflight** — `34175371296` — SUCCESS
- **Rhythm Professional Holdout Self Test** — `34175371403` — SUCCESS
- **Rhythm Pre-Holdout Static Preflight V2** — `34175475746` — SUCCESS

Static proof includes schema-v7/product/runtime/anti-leakage/rendering checks, **400 synthetic events / 100 measures**, valid full + preview PDFs, **PDF event fidelity = 1.0**, frozen/PDF event hash `6475a7d68071a8810890982e1c06c0d39f99e85d646680706233ceed5a58b37e`, and no production/model activity.

## CLEANUP-TAB-PREVIEW — CLOSED GREEN

Historical failure signature before repair:
- run `34175719332`
- head `ae25972ce1f1d518a40e3dcc00739b70ff2a34ff`
- docs-only commit nevertheless created the cleanup workflow run
- run name appeared as `.github/workflows/cleanup-tab-preview.yml` instead of declared workflow name
- conclusion `failure`
- **zero jobs** scheduled

This was an invalid-workflow/registration-style failure, not a failure inside the old Python patch step.

Source inspection proved the UI cleanup had already been applied in `app/ai-tab/page.js`:
- `Tab Studio Preview` present
- old `Review Your Tab Preview` absent
- old `Watermarked preview ready` absent
- old `Full transcription locked` overlay absent

The obsolete one-shot mutator was replaced by an idempotent, read-only verifier:
- repair commit `ab27ae3b95d6aa5942f2d456c3f29792c96ecc3b` — `Fix cleanup preview workflow`
- `contents: read` only
- triggers only when `.github/workflows/cleanup-tab-preview.yml` changes
- no source mutation, commit, or push
- verifies the cleaned preview contract and fails only if old UI text returns

Automatic verification:
- **Clean up tab preview card** — run `34175871883` — **SUCCESS**
- job `verify-preview-cleanup` scheduled and succeeded
- checkout succeeded
- `Verify preview cleanup is already applied` succeeded
- no manual dispatch used
- `V143 AI Tab Real Audio Product Canary` absent from the post-fix run set

Result: unrelated cleanup workflow noise is closed green without touching V143 musical/model/renderer behavior.

## PRESERVED-CAPTURE PDF WORKFLOWS — HISTORICAL AUDIT CLOSED

Audited the three deterministic preserved-capture workflows without manual dispatch or model/GPU/professional scoring activity:
- `.github/workflows/v143-professional-pdf-fixture.yml`
- `.github/workflows/v143-render-real-candidate-pdf.yml`
- `.github/workflows/v143-render-v5-shadow-professional-pdf.yml`

Repository history already contains bot-authored persisted successful evidence from each harness:
- professional fixture: `a5655d56df411cd3011c42807dc9119019b9858d`
- real candidate: `2470225d9cb726e35a07459e29783997a3447699`
- V5 shadow: `f160d2a7c0d047584650913d182cf3b427b8d1a2`

The real-candidate persisted evidence records **967 events / 113 measures / 725 onsets**, `reference-free`, Modal unused, and Production untouched. The V5-shadow persisted evidence likewise records reference-free validation with Modal and Production untouched.

Conclusion:
- no reproducible current deterministic renderer defect was established
- old red/dashboard entries are superseded historical harness/persistence noise unless a current deterministic run reproduces them
- no renderer event construction, score structure, thresholds, scheduler settings, async timing, endpoint pin, or model path was changed for this audit
- no preserved-capture workflow was manually dispatched
- no model-bearing, paid/GPU, professional-scoring, or Production activity occurred

## RECENT AUTOMATIC CI AUDIT — CLEAN

Inspected branch-level automatic workflow history after the cleanup repair:
- newest failure remains historical cleanup run `34175719332` at head `ae25972ce1f1d518a40e3dcc00739b70ff2a34ff`
- newer cleanup verification run `34175871883` at head `ab27ae3b95d6aa5942f2d456c3f29792c96ecc3b` is **SUCCESS**
- no automatic branch failure exists newer than `34175719332`
- `V143 AI Tab Real Audio Product Canary` is absent from the recent branch run set
- checkpoint-only commits did not trigger unrelated workflows

Result: there is no current deterministic/source-only automatic CI failure established that warrants another code or workflow mutation.

## CURRENT VERIFIED STATE

- crash-loop ownership defect explained and fixed
- async protocol gate green
- V143 branch build/HTTP preview path green
- V143 Rhythm deterministic PDF presentation proof green
- static PDF product contract green
- exact-event PDF fidelity green at **1.0**
- consolidated synthetic holdout self-test green
- V2 fresh static preflight + evidence persistence green
- polished branding contract present
- exact-event fail-closed validation still present
- real-audio canary automatic trigger removed and remains manual-only
- cleanup-tab-preview workflow repaired and green
- preserved-capture PDF historical audit closed with successful persisted evidence for all three harnesses
- recent automatic CI audit has no newer failure to repair
- score structure preserved: **725 / 970 / 967 / 3 / 0**
- async lifetime preserved: **1800 / 1200 / 600**
- endpoint blob pin preserved
- no new model-bearing run, paid/GPU inference, real professional scoring run, or live Production promotion

## FRESH CHAT HANDOFF — START HERE

A final **source-only invariant/safety sweep was started but not completed** before this handoff. No workflow was dispatched and no model/GPU/professional-scoring/Production activity was started.

Latest observed branch head before this handoff was `c3622076d57bfe95b148089f7d73c605fe2ec7fc` (`docs: checkpoint automatic CI audit`). Treat the branch itself as authoritative if newer commits exist when the fresh chat begins.

One history check completed during the partial sweep:
- commit `b55d9db517fe356b40600bae85ba98ead879aeb6` explicitly changed `analyzer/v143_async_job_protocol.py` `ASYNC_RESULT_TTL_SECONDS` from `15 * 60` to `30 * 60`, documenting the 20-minute worker budget plus 10-minute margin.

Important: that history check is **not** a substitute for inspecting current branch source. The fresh chat should verify the current files directly.

## NEXT SAFE WORK — EXACT ORDER

1. Read this file first and re-read the current branch head before doing anything else.
2. Complete the source-only invariant sweep on the **current branch source**, with no manual workflow dispatch.
3. Verify async lifetime remains exactly **1800 / 1200 / 600**:
   - shared result/control TTL = **1800s**
   - orchestrator timeout = **1200s**
   - ownership margin = **600s**
   - confirm both Python/shared protocol and any Next.js/runtime fallback still agree.
4. Verify the exact endpoint blob pin remains `169b4bb136eba742c3422a73ee5dd0174ca06c49` everywhere it is expected. Do not replace or repin it during the sweep.
5. Inspect the `V143 AI Tab Real Audio Product Canary` workflow source and confirm it remains **manual-only** (`workflow_dispatch` only; no automatic `push`, `pull_request`, schedule, or other automatic trigger).
6. Verify the frozen score/evidence contract still represents exactly:
   - **725 retained attacks**
   - **970 selected pitches**
   - **967 rendered notes**
   - exactly **3 legal-voicing drops**
   - **0 recovery**
   - all **113 measures** populated
   - `referenceFree=true`
   - `newInferenceUsed=false`
   - drops: m40/s14 MIDI 78; m63/s14 MIDI 47; m113/s13 MIDI 43
7. Confirm no recent documentation/CI cleanup commit altered renderer event construction, thresholds, scheduler settings, model paths, endpoint selection, async ownership semantics, or Production behavior.
8. Do **not** run Rhythm/Lead/Bass inference, Modal/GPU, professional scorer, optimizer/training, threshold sweeps, Production deploy/promotion, or any manual workflow to prove these source invariants.
9. If every source-only check is clean, update this checkpoint with the exact files/lines or commits inspected and mark the final sweep **CLEAN**.
10. Then stop changing code. The branch should remain at the safe deterministic checkpoint until the user gives explicit new authorization for any model-bearing evaluation or Production action.
11. If any invariant differs, do not automatically “fix” model/renderer behavior. Record the exact discrepancy in this checkpoint first, identify whether it is documentation drift versus runtime behavior, and keep all prohibited activity stopped.

## FRESH CHAT NON-NEGOTIABLES

- **725 / 970 / 967 / exactly 3 drops / 0 recovery**
- **1800s / 1200s / 600s**
- endpoint blob `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- real-audio canary remains **manual-only**
- no new Modal/GPU/model inference, professional scoring, optimizer/training, threshold sweep, or Production promotion without explicit new authorization
- keep `docs/checkpoints/CURRENT_STATE.md` updated after each meaningful diagnosis/fix
