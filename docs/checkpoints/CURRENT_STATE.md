# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or change live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional human reference is scorer-only. Runtime/shadows may never read/train/tune/select from it.
- Retired scored freeze event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb` must never be rerun/rescored.
- Any accepted correction requires a completely new approved-audio candidate → immutable freeze/PDF → lock → one professional score.
- Completion remains score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is not complete.**

## Last scored candidate / holdout result
- Repaired timing + precision: 449 repaired beats, 0 interval outliers, 113 measures / 1796 slots, all measures populated, explicit primary complete.
- Exact 2-pass proof run `32697939613` passed. Old candidate/freeze must not be rerun/rescored.
- One-shot professional run `32731885778`: coverage recall `1.0`, pitch-content F1 `0.23718280683583634`, pitch+timing F1 `0.033143448990160536`, critical mismatches `1723`.
- Scorer/reference is closed again. Allowed diagnosis only: coverage solved; timing/grid identity and pitch identity fundamentally wrong.
- Retired scored render identity `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`: 725 selected/unique attacks → 985 rendered notes, 236 multi-note onsets, max chord size 6, 113 measures, PDF fidelity 1.0.

## Physical onset provenance — corrected and proven
- sustain promotion no longer overwrites physical `onsetTime`; grid `timeSeconds/start` remains separate.
- observed schema-v2 proof passed with unchanged event/grid/pitch identity and protected runtime.
- render/freeze projection omits physical timing seconds, so this fix alone cannot change scored identity.

## Precision polyphonic expansion — audio-only defect PROVEN
Committed-product CPU audit established:
- 725 attacks → 985 notes = 260 secondary notes.
- 144 fundamental promotions; all 144 still rendered the strongest raw pitch.
- 96/144 promoted attacks rendered that strongest pitch at a harmonic-family interval above the promoted primary: +12=78, +19=11, +24=6, +28=1.
- synthetic `[40,52]` proof reproduces the contradiction: 52 strongest raw, 40 promoted as fundamental, then 52 still emitted as an independent note.
- protected runtime exact; no professional reference/runtime labels/Production/Modal GPU used by the audit.

## Minimal promoted-harmonic guard — PROVEN GREEN
- helper: `analyzer/v143_precision_promoted_harmonic_guard.py`, commit `588b314c3103ffbea8a0a933351562551750f670`.
- guard removes only the exact strongest upper harmonic when the precision stage promoted a lower primary away from it; attacks/grid/primary/non-harmonic secondaries remain unchanged.
- observed `precision-promoted-harmonic-guard-proof.json` has `passed=true`, old-candidate opportunity count 96, attack identity unchanged, scoring pitch identity changed, protected runtime exact, anti-leakage passed, no reference/GPU/Production.
- product path integration commit `534be3fec36cf5ec4a87089b1298becb4933693d`; emits `promotedHarmonicGuardDiagnostics` and schema v4.
- product-proof workflow extended commit `30d7da578667f7d128824d7d343be782bf064533`.

## One-shot new approved-audio candidate — TRIGGERED
Created `.github/workflows/v143-harmonic-guard-candidate-once.yml` commit `346d0f38381906e9c821b7f6020c932f3e2b4c1c`.

Safety design:
- dedicated marker only; bot commits excluded from triggering a second inference.
- pre-Modal gate requires old candidate blob exact `20e7a583...`, protected pipeline exact, approved fixture SHA exact, green guard proof/opportunity count 96, checker pass, anti-leakage pass.
- exactly one Modal L4 invocation writes new path `debug/v143-contextual-prune/repaired-timing-precision-harmonic-guard-candidate-product.json`; old candidate is never overwritten.
- after inference it prepares repaired-timing freeze payload, canonicalizes projected render events, requires schema v4 + guard suppression >0 + 113 measures + safety invariants, and fails closed unless projected render SHA differs from retired `a81190...`.
- success commit writes candidate + `repaired-timing-precision-harmonic-guard-candidate-proof.json` and removes marker in the same bot commit.

Trigger marker was created in commit `a9e9ddd61c1d41b2530ab15e352bf8f410b592fc`. Therefore the one approved-audio inference is now in-flight/eligible; **do not create another marker or dispatch another candidate workflow**.

At this checkpoint the new candidate file is still not present on the branch (latest re-check returned 404). Do not claim inference success yet.

## CPU post-proof prepared
Created `.github/workflows/v143-harmonic-guard-candidate-postproof.yml` commit `5d7e96c38c8328457bd82aeeb691245a66ffed00`.
- triggers automatically only when the bot commits the new candidate/proof.
- recomputes final committed candidate blob/raw-event SHA/projected render SHA.
- requires new projected render identity != retired `a81190...` and match between candidate trace + initial proof + fresh projection.
- inherits determinism from prior exact 2-pass run `32697939613` only after requiring all upstream stage/section hashes exact; new harmonic guard is separately proven pure deterministic, so this avoids paying for a second GPU inference.
- writes `repaired-timing-precision-harmonic-guard-candidate-binding-proof.json`; no reference, no GPU, no Production.

## New fail-closed preholdout workflow — PREPARED, NOT TRIGGERED
Created `.github/workflows/v143-harmonic-guard-final-preholdout.yml` commit `12958a2f5f245697148a7fba190dd7bb8e98987c`.
- triggers only from dedicated `RUN_HARMONIC_GUARD_PREHOLDOUT_ONCE` marker; marker has not been created.
- refuses to run unless the new candidate, initial proof, and final binding proof all exist and pass.
- binds final candidate blob SHA + projected render SHA and rejects retired identities `c621...`, `e693...`, and scored `a81190...` before freeze.
- uses repaired-timing-specific freeze prep, runtime isolation, protected hash and approved-audio gates, and anti-leakage checks.
- freezes exact committed candidate, renders full/preview PDFs, verifies renderer projection and `pdfEventFidelity == 1.0`, and requires frozen SHA == bound projected SHA != every retired identity.
- writes compact `rhythm-harmonic-guard-final-preholdout.json`, uploads immutable freeze/PDF artifacts, then removes the preholdout marker in the same bot commit.
- scorer/reference remains sealed; workflow cannot claim Rhythm complete and cannot promote Production.

## Holdout workflow safety drift
- old `.github/workflows/v143-repaired-timing-precision-final-preholdout.yml` remains stale and must not be dispatched.
- use only the new harmonic-guard preholdout path after candidate binding proof is green.

## Cost control
- Exactly one new harmonic-guard candidate trigger has been issued; do not issue another.
- No professional scorer/reference has been opened.
- Old candidate/freeze/scorer remain untouched.

## Next exact actions
1. Re-check branch for new candidate + initial proof; require `passed=true`, guard suppression >0, 113 measures, protected hash exact, projected render SHA != retired `a81190...`.
2. Re-check for automatic binding proof; require final committed blob/event hashes and determinism inheritance proof green.
3. Save exact new candidate/render identities here immediately.
4. Only after binding proof green, create `RUN_HARMONIC_GUARD_PREHOLDOUT_ONCE` exactly once.
5. Require final preholdout `passed=true`, frozen SHA == bound projected SHA, PDF-event fidelity 1.0, and all retired identities rejected.
6. Only then may exactly one professional score be permitted.
