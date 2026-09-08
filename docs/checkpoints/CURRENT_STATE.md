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

## CLEANUP-TAB-PREVIEW DIAGNOSIS / FIX — ACTIVE

Latest observed failure before repair:
- run `34175719332`
- head `ae25972ce1f1d518a40e3dcc00739b70ff2a34ff`
- docs-only commit nevertheless created a cleanup workflow run
- run name appeared as `.github/workflows/cleanup-tab-preview.yml` instead of declared workflow name
- conclusion `failure`
- **zero jobs** were scheduled

This is an invalid-workflow/registration-style failure signature, not a failure inside the Python patch step.

Source inspection also proved the cleanup had already been applied in `app/ai-tab/page.js`:
- `Tab Studio Preview` is present
- old `Review Your Tab Preview` text absent
- old `Watermarked preview ready` text absent
- old `Full transcription locked` overlay absent

The old workflow was obsolete one-shot mutation logic and was not idempotent: it expected the removed overlay to still exist and performed a write/commit/push.

Repair commit:
- `ab27ae3b95d6aa5942f2d456c3f29792c96ecc3b` — `Fix cleanup preview workflow`

Current `.github/workflows/cleanup-tab-preview.yml` now:
- has `contents: read` only
- triggers only when the workflow file itself changes
- does **not** mutate source
- does **not** commit or push
- verifies `Tab Studio Preview` is present
- fails only if old preview/overlay text returns
- is idempotent

Automatic Actions verification for commit `ab27ae3b95d6aa5942f2d456c3f29792c96ecc3b` still needs to be inspected in the current session; do not manually dispatch anything to obtain it.

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
- score structure preserved: **725 / 970 / 967 / 3 / 0**
- async lifetime preserved: **1800 / 1200 / 600**
- endpoint blob pin preserved
- no new model-bearing run, paid/GPU inference, real professional scoring run, or live Production promotion
- cleanup workflow source repaired in isolation; V143 musical/model/renderer logic untouched

## NEXT SAFE WORK — EXACT ORDER

1. Inspect automatic Actions created by cleanup repair commit `ab27ae3b95d6aa5942f2d456c3f29792c96ecc3b`.
2. Confirm the cleanup workflow parses, schedules a job, and is green.
3. Confirm `V143 AI Tab Real Audio Product Canary` is absent; do **not** manually dispatch it.
4. Update this checkpoint with the run ID/result.
5. Only after cleanup is closed, inspect historical red preserved-capture PDF workflows if dashboard cleanup is still desired. Repair stale deterministic assertions/transforms only; never alter musical/model logic to satisfy a stale harness.

## FRESH CHAT NON-NEGOTIABLES

- **725 / 970 / 967 / exactly 3 drops / 0 recovery**
- **1800s / 1200s / 600s**
- endpoint blob `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- real-audio canary remains **manual-only**
- no new Modal/GPU/model inference, professional scoring, optimizer/training, threshold sweep, or Production promotion without explicit new authorization
- keep `docs/checkpoints/CURRENT_STATE.md` updated after each meaningful diagnosis/fix
